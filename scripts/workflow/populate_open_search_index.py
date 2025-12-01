#!/usr/bin/env python3

import argparse
import hashlib
import json
import logging
import os
import sys
from typing import Dict, List, Optional, Tuple

from urllib.parse import quote as urlquote

import boto3
import botocore.exceptions
import botocore.session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.client import BaseClient
from botocore.credentials import ReadOnlyCredentials
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("populate_open_search_index")

EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
DEFAULT_DDB_TABLE = "ftrs-dos-local-database-healthcare-service"
INDEXING_TIMEOUT_SECONDS = 60

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Populate an OpenSearch Serverless index from a DynamoDB table")
    parser.add_argument("--final-index", dest="final_index", help="Final index name" )
    parser.add_argument("--endpoint", dest="endpoint", help="OpenSearch endpoint" )
    parser.add_argument("--workspace", dest="workspace", default=os.environ.get('WORKSPACE', ''), help="Terraform workspace suffix to append to index/table names (e.g. 'ftrs-856')")
    parser.add_argument("--aws-region", dest="aws_region", default=os.environ.get('AWS_REGION'), help="AWS region")
    parser.add_argument("--dynamodb-table", dest="ddb_table", default=os.environ.get('DYNAMODB_TABLE', DEFAULT_DDB_TABLE), help="DynamoDB table name")
    parser.add_argument("--batch-size", dest="batch_size", type=int, default=1, help="Number of records to send in one bulk request (1 = per-document PUT)")
    parser.add_argument("--log-level", dest="log_level", default=os.environ.get('LOG_LEVEL', 'INFO'))
    return parser.parse_args(argv)

def validate_inputs(open_search_domain: Optional[str], index: Optional[str]) -> None:
    if not open_search_domain or not index:
        log.error('OPEN_SEARCH_DOMAIN and INDEX must be set')
        raise SystemExit(2)

def build_endpoint(raw: str) -> str:
    if raw.startswith("https://"):
        return raw.rstrip('/')
    return "https://" + raw.rstrip('/')

def get_aws_signing_credentials() -> ReadOnlyCredentials:
    session = botocore.session.get_session()
    creds = session.get_credentials()
    if creds is None:
        raise RuntimeError("AWS credentials not found")
    return creds.get_frozen_credentials()

def compute_payload_hash(body: Optional[str]) -> str:
    if not body:
        return EMPTY_SHA256
    return hashlib.sha256(body.encode("utf-8")).hexdigest()

def build_aws_request(method: str, url: str, body: Optional[str], payload_hash: str) -> AWSRequest:
    headers = {"Content-Type": "application/json", "x-amz-content-sha256": payload_hash}
    return AWSRequest(method=method, url=url, data=body or "", headers=headers)

def sign_aws_request(aws_req: AWSRequest, credentials: ReadOnlyCredentials, service: str, region: Optional[str]) -> None:
    SigV4Auth(credentials, service, region or os.environ.get("AWS_REGION") or "").add_auth(aws_req)

class SignedRequestsSession:
    def __init__(self, aws_region: Optional[str], service: str = "aoss") -> None:
        self.aws_region = aws_region
        self.service = service
        self.session = requests.Session()
        self.credentials = get_aws_signing_credentials()
        self._signer = lambda aws_req: sign_aws_request(aws_req, self.credentials, self.service, self.aws_region)

    def request(self, method: str, url: str, body: Optional[str]) -> requests.Response:
        payload_hash = compute_payload_hash(body)
        aws_req = build_aws_request(method, url, body, payload_hash)
        self._signer(aws_req)
        prepared = requests.Request(method=aws_req.method, url=aws_req.url, data=aws_req.body, headers=dict(aws_req.headers)).prepare()
        return self.session.send(prepared, timeout=INDEXING_TIMEOUT_SECONDS)

def prepare_dynamodb_client(region: Optional[str]) -> BaseClient:
    return boto3.client('dynamodb', region_name=region) if region else boto3.client('dynamodb')

def scan_dynamodb_table(dynamodb_client: BaseClient, table_name: str, attributes: List[str]) -> List[Dict]:
    paginator = dynamodb_client.get_paginator('scan')
    projection = ",".join(attributes) if attributes else None
    scan_kwargs = {}
    if projection:
        scan_kwargs['ProjectionExpression'] = projection
    try:
        items = [item for page in paginator.paginate(TableName=table_name, **scan_kwargs) for item in page.get('Items', [])]
    except botocore.exceptions.ClientError as exc:
        log.error('DynamoDB scan failed: %s', exc)
        raise
    return items

def parse_dynamo_string(attr: Dict) -> Optional[str]:
    if not isinstance(attr, dict):
        return None
    if 'S' in attr:
        return attr['S']
    if 'N' in attr:
        return str(attr['N'])
    return None

def convert_dynamodb_format(items: List[Dict]) -> List[Dict]:

    def _to_int(value) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, dict):
            n = value.get('N')
            if n is None:
                return None
            try:
                return int(n)
            except (TypeError, ValueError):
                return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _parse(elem: Dict) -> Optional[Dict]:
        if not isinstance(elem, dict):
            return None
        m = elem.get('M')
        if isinstance(m, dict):
            return {'sg': _to_int(m.get('sg')), 'sd': _to_int(m.get('sd'))}
        if 'sg' in elem and 'sd' in elem:
            return {'sg': _to_int(elem.get('sg')), 'sd': _to_int(elem.get('sd'))}
        return None

    if not isinstance(items, list):
        return []
    return [r for r in (_parse(e) for e in items) if r is not None]

def transform_records(raw_items: List[Dict]) -> List[Dict]:
    def _extract_field(record: Dict, *keys: str) -> Optional[str]:
        def _try_key(k: str) -> Optional[str]:
            v = record.get(k)
            if v is None:
                return None
            return parse_dynamo_string(v) or (str(v) if not isinstance(v, dict) else None)

        return next((res for res in (_try_key(k) for k in keys) if res is not None), None)

    def _extract_sgsds(record: Dict) -> List[Dict]:
        candidates = (
            record.get('symptomGroupSymptomDiscriminators'),
            record.get('symptomGroupSymptomDiscriminator'),
            record.get('symptomGroup_symptomDiscriminators')
        )

        def _try_convert(cand):
            if isinstance(cand, dict) and 'L' in cand and isinstance(cand['L'], list):
                return convert_dynamodb_format(cand['L'])
            if isinstance(cand, list):
                return convert_dynamodb_format(cand)
            return None

        return next((res for res in (_try_convert(c) for c in candidates) if res is not None), [])

    if not isinstance(raw_items, list):
        return []

    def _parse_item(record: Dict) -> Optional[Dict]:
        try:
            rid = _extract_field(record, 'id', 'Id')
            field = _extract_field(record, 'field', 'Field')
            if not rid or not field:
                return None
            sgsds = _extract_sgsds(record)
            return {'id': rid, 'field': field, 'sgsds': sgsds}
        except (TypeError, ValueError, KeyError):
            return None

    return [r for r in map(_parse_item, raw_items) if r]

def build_doc_id(record: Dict) -> str:
    return f"{record['id']}|{record['field']}"

def build_doc_path(index_name: str, doc_id: str) -> str:
    return '/' + urlquote(index_name) + '/_doc/' + urlquote(doc_id)

def build_name_with_workspace(name: str, workspace: Optional[str]) -> str:
    ws_raw = (workspace or "").strip()
    if not ws_raw:
        return name
    ws_normalized = ws_raw.lstrip('-')
    suffix = "-" + ws_normalized if ws_normalized else ""
    if suffix and name.endswith(suffix):
        return name
    return name + suffix

def build_bulk_payload(index_name: str, records: List[Dict]) -> str:
    lines = [line for record in records for line in (json.dumps({"index": {"_index": index_name, "_id": build_doc_id(record)}}), json.dumps(record))]
    return "\n".join(lines) + "\n"

def index_single_record(session: SignedRequestsSession, endpoint: str, index_name: str, record: Dict) -> Tuple[bool, int, str]:
    doc_id = build_doc_id(record)
    path = build_doc_path(index_name, doc_id)
    url = endpoint.rstrip('/') + path
    body = json.dumps(record)

    try:
        resp = session.request('PUT', url, body)
        resp_text = resp.text or ''
        status = resp.status_code
        if status in (200, 201, 202):
            return True, status, resp_text
        if 400 <= status < 500:
            return False, status, resp_text
        log.warning('Transient failure indexing id=%s status=%s body=%s', doc_id, status, resp_text)
        return False, status, resp_text
    except requests.RequestException as exc:
        log.error('Request exception indexing id=%s: %s', doc_id, exc)
        return False, 500, str(exc)

def index_bulk(session: SignedRequestsSession, endpoint: str, index_name: str, records: List[Dict]) -> Tuple[int, int]:
    if not records:
        return 0, 0
    payload = build_bulk_payload(index_name, records)
    url = endpoint.rstrip('/') + '/_bulk'
    resp = session.request('POST', url, payload)
    if resp.status_code in (200, 201, 202):
        try:
            body = resp.json()
            items = body.get('items', [])
            success = sum(1 for it in items if 'index' in it and 200 <= it['index'].get('status', 500) < 300)
            return success, len(records)
        except (ValueError, json.JSONDecodeError):
            log.debug('Could not parse bulk response JSON; treating as failures')
            return 0, len(records)
    return 0, len(records)

def index_records(session: SignedRequestsSession, endpoint: str, index_name: str, records: List[Dict], batch_size: int = 1) -> Tuple[int, int]:
    success_count = 0
    total = 0
    if batch_size <= 1:
        total = len(records)

        def _attempt_index(record: Dict) -> int:
            if not record.get('id'):
                log.debug('Skipping record with missing id: %s', record)
                return 0
            log.info('Indexing record ID: %s', record['id'])
            try:
                ok, status, body = index_single_record(session, endpoint, index_name, record)
                if ok:
                    return 1
                log.error('Failed to index id=%s status=%s body=%s', record['id'], status, body)
                return 0
            except requests.RequestException as exc:
                log.error('Request exception indexing record id=%s: %s', record.get('id'), exc)
                return 0
            except Exception as exc:
                log.error('Unexpected exception indexing record id=%s: %s', record.get('id'), exc)
                return 0

        success_count = sum(map(_attempt_index, records))
        return success_count, total
    if records:
        chunks = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_chunks = len(chunks)

        def _process_chunk(args: Tuple[List[Dict], int]) -> Tuple[int, int]:
            chunk, idx = args
            attempted = len(chunk)
            log.info('Bulk indexing %d records (chunk %d/%d)', attempted, idx + 1, total_chunks)
            ok, attempted_returned = index_bulk(session, endpoint, index_name, chunk)
            if ok < attempted_returned:
                log.error('Bulk chunk had %d failures out of %d', attempted_returned - ok, attempted_returned)
            return ok, attempted_returned

        results = list(map(_process_chunk, ((chunk, idx) for idx, chunk in enumerate(chunks))))
        success_count += sum(r[0] for r in results)
        total += sum(r[1] for r in results)
    return success_count, total

def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    log.setLevel(getattr(logging, args.log_level.upper(), logging.INFO))

    try:
        validate_inputs(args.endpoint or os.environ.get('OS_ENDPOINT'),
                        args.final_index or os.environ.get('OS_FINAL_INDEX'))
    except SystemExit as e:
        return int(e.code)

    endpoint_input = args.endpoint or os.environ.get('OS_ENDPOINT')
    endpoint = build_endpoint(endpoint_input) if endpoint_input else None

    final_index = args.final_index or os.environ.get('OS_FINAL_INDEX')

    aws_region = args.aws_region
    ddb_table = args.ddb_table
    workspace = args.workspace or os.environ.get('WORKSPACE', '')

    final_table = build_name_with_workspace(ddb_table, workspace) if ddb_table else ddb_table
    final_index = build_name_with_workspace(final_index, workspace) if final_index else final_index

    log.info('Using configuration:')
    log.info('  Endpoint: %s', endpoint)
    log.info('  Final index: %s', final_index)
    log.info('  AWS region: %s', aws_region)
    log.info('  DynamoDB table: %s', final_table)
    log.info('  Workspace: %s', workspace)

    session = SignedRequestsSession(aws_region)

    try:
        log.info('Scanning DynamoDB table...')
        raw_items = scan_dynamodb_table(prepare_dynamodb_client(aws_region), final_table, ['id', 'field', 'symptomGroupSymptomDiscriminators', 'symptomGroupSymptomDiscriminator', 'symptomGroup_symptomDiscriminators'])
        log.info('Transforming records...')
        transformed = transform_records(raw_items)
        log.info('Indexing records...')
        success, total = index_records(session, endpoint, final_index, transformed, args.batch_size)
        log.info('Indexing complete: %d successful, %d total records', success, total)
    except Exception as exc:
        log.error('Unexpected error: %s', exc)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
