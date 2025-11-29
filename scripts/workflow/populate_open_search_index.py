#!/usr/bin/env python3

import os
import sys
import json
import logging
import time
import argparse
from typing import Optional, List, Dict, Tuple
import hashlib
from urllib.parse import quote as urlquote

import boto3
import botocore.session
import botocore.exceptions
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("populate_open_search_index")

EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
DEFAULT_DDB_TABLE = "ftrs-dos-local-database-healthcare-service"
INDEXING_TIMEOUT_SECONDS = 60
INDEXING_MAX_RETRIES = 3


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Populate an OpenSearch Serverless index from a DynamoDB table")
    parser.add_argument("--index", dest="index", help="Index name (final)" )
    parser.add_argument("--workspace", dest="workspace", default=os.environ.get('WORKSPACE', ''), help="Terraform workspace suffix to append to index/table names (e.g. 'ftrs-856')")
    parser.add_argument("--aws-region", dest="aws_region", default=os.environ.get('AWS_REGION'), help="AWS region")
    parser.add_argument("--dynamodb-table", dest="ddb_table", default=os.environ.get('DYNAMODB_TABLE', DEFAULT_DDB_TABLE), help="DynamoDB table name")
    parser.add_argument("--batch-size", dest="batch_size", type=int, default=1, help="Number of records to send in one bulk request (1 = per-document PUT)")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Print what would be indexed without sending requests")
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


def get_aws_signing_credentials():
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


def sign_aws_request(aws_req: AWSRequest, credentials, service: str, region: Optional[str]) -> None:
    SigV4Auth(credentials, service, region or os.environ.get("AWS_REGION") or "").add_auth(aws_req)


class SignedRequestsSession:
    def __init__(self, aws_region: Optional[str], service: str = "aoss") -> None:
        self.aws_region = aws_region
        self.service = service
        self.session = requests.Session()
        self.credentials = get_aws_signing_credentials()

    def request(self, method: str, url: str, body: Optional[str]) -> requests.Response:
        payload_hash = compute_payload_hash(body)
        aws_req = build_aws_request(method, url, body, payload_hash)
        sign_aws_request(aws_req, self.credentials, self.service, self.aws_region)
        prepared = requests.Request(method=aws_req.method, url=aws_req.url, data=aws_req.body, headers=dict(aws_req.headers)).prepare()
        return self.session.send(prepared, timeout=INDEXING_TIMEOUT_SECONDS)


def prepare_dynamodb_client(region: Optional[str]):
    return boto3.client('dynamodb', region_name=region) if region else boto3.client('dynamodb')


def scan_dynamodb_table(dynamodb_client, table_name: str, attributes: List[str]) -> List[Dict]:
    paginator = dynamodb_client.get_paginator('scan')
    projection = ",".join(attributes) if attributes else None
    items: List[Dict] = []
    scan_kwargs = {}
    if projection:
        scan_kwargs['ProjectionExpression'] = projection
    try:
        for page in paginator.paginate(TableName=table_name, **scan_kwargs):
            items.extend(page.get('Items', []))
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


def convert_dynamodb_format(L: List[Dict]) -> List[Dict]:
    out: List[Dict] = []
    if not isinstance(L, list):
        return out
    for elem in L:
        if isinstance(elem, dict) and 'M' in elem:
            m = elem['M']
            try:
                sg = int(m.get('sg', {}).get('N')) if isinstance(m.get('sg'), dict) and 'N' in m.get('sg') else int(m.get('sg'))
            except Exception:
                sg = None
            try:
                sd = int(m.get('sd', {}).get('N')) if isinstance(m.get('sd'), dict) and 'N' in m.get('sd') else int(m.get('sd'))
            except Exception:
                sd = None
            out.append({'sg': sg, 'sd': sd})
        elif isinstance(elem, dict) and 'sg' in elem and 'sd' in elem:
            try:
                sg = int(elem.get('sg'))
            except Exception:
                sg = None
            try:
                sd = int(elem.get('sd'))
            except Exception:
                sd = None
            out.append({'sg': sg, 'sd': sd})
    return out


def transform_records(raw_items: List[Dict]) -> List[Dict]:
    out: List[Dict] = []
    for record in raw_items:
        try:
            rid = parse_dynamo_string(record.get('id', {})) or parse_dynamo_string(record.get('Id', {}))
            field = parse_dynamo_string(record.get('field', {})) or parse_dynamo_string(record.get('Field', {}))
            sgsd = record.get('symptomGroupSymptomDiscriminators') or record.get('symptomGroupSymptomDiscriminators')
            if isinstance(sgsd, dict) and 'L' in sgsd:
                sgsds = convert_dynamodb_format(sgsd['L'])
            else:
                sgsds = []
            out.append({'id': rid, 'field': field, 'sgsds': sgsds})
        except Exception as exc:
            log.debug('Skipping record due to parse error: %s', exc, exc_info=True)
    return out


def build_doc_id(record: Dict) -> str:
    return "{}|{}".format(record['id'], record['field'])


def build_doc_path(index_name: str, doc_id: str) -> str:
    return '/' + urlquote(index_name) + '/_doc/' + urlquote(doc_id)


def build_name_with_workspace(name: str, workspace: Optional[str]) -> str:
    ws = (workspace or "")
    if ws and not ws.startswith('-'):
        ws = "-" + ws
    return name + ws


def build_bulk_payload(index_name: str, records: List[Dict]) -> str:
    lines: List[str] = []
    for record in records:
        doc_id = build_doc_id(record)
        action = {"index": {"_index": index_name, "_id": doc_id}}
        lines.append(json.dumps(action))
        lines.append(json.dumps(record))
    return "\n".join(lines) + "\n"


def index_single_record(session: SignedRequestsSession, endpoint: str, index_name: str, record: Dict, aws_region: Optional[str]) -> Tuple[bool, int, str]:
    doc_id = build_doc_id(record)
    path = build_doc_path(index_name, doc_id)
    url = endpoint.rstrip('/') + path
    body = json.dumps(record)
    last_exc = None
    last_resp_text = ""
    for attempt in range(1, INDEXING_MAX_RETRIES + 1):
        try:
            resp = session.request('PUT', url, body)
            last_resp_text = resp.text or ''
            if resp.status_code in (200, 201, 202):
                return True, resp.status_code, last_resp_text
            if 400 <= resp.status_code < 500:
                return False, resp.status_code, last_resp_text
            log.warning('Transient failure indexing id=%s status=%s attempt=%d body=%s', doc_id, resp.status_code, attempt, last_resp_text)
        except requests.RequestException as exc:
            last_exc = exc
            log.warning('Request exception indexing id=%s attempt=%d: %s', doc_id, attempt, exc)
        time.sleep(2 ** (attempt - 1))
    if last_exc:
        raise last_exc
    return False, 500, last_resp_text


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
        except Exception:
            return 0, len(records)
    return 0, len(records)


def index_records(session: SignedRequestsSession, endpoint: str, index_name: str, records: List[Dict], aws_region: Optional[str], batch_size: int = 1, dry_run: bool = False) -> Tuple[int, int]:
    success_count = 0
    total = 0
    if dry_run:
        log.info('Dry run: would index %d records to %s', len(records), index_name)
        return 0, len(records)
    if batch_size <= 1:
        for record in records:
            total += 1
            if not record.get('id'):
                log.debug('Skipping record with missing id: %s', record)
                continue
            log.info('Indexing record ID: %s', record['id'])
            try:
                ok, status, body = index_single_record(session, endpoint, index_name, record, aws_region)
                if ok:
                    success_count += 1
                else:
                    log.error('Failed to index id=%s status=%s body=%s', record['id'], status, body)
            except Exception as exc:
                log.error('Exception indexing record id=%s: %s', record.get('id'), exc)
        return success_count, total
    for chunk_start in range(0, len(records), batch_size):
        chunk = records[chunk_start:chunk_start + batch_size]
        total += len(chunk)
        log.info('Bulk indexing %d records (chunk %d/%d)', len(chunk), chunk_start // batch_size + 1, (len(records) + batch_size - 1) // batch_size)
        ok, attempted = index_bulk(session, endpoint, index_name, chunk)
        success_count += ok
        if ok < attempted:
            log.error('Bulk chunk had %d failures out of %d', attempted - ok, attempted)
    return success_count, total


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    log.setLevel(getattr(logging, args.log_level.upper(), logging.INFO))

    try:
        validate_inputs(os.environ.get('OPEN_SEARCH_DOMAIN'), args.index or os.environ.get('INDEX'))
    except SystemExit as e:
        return int(e.code)

    open_search_domain = os.environ.get('OPEN_SEARCH_DOMAIN')
    index = args.index or os.environ.get('INDEX')
    aws_region = args.aws_region
    ddb_table = args.ddb_table
    workspace = args.workspace or os.environ.get('WORKSPACE', '')

    final_index = build_name_with_workspace(index, workspace) if index else index
    final_table = build_name_with_workspace(ddb_table, workspace) if ddb_table else ddb_table

    endpoint = build_endpoint(open_search_domain)

    dynamodb_client = prepare_dynamodb_client(aws_region)
    raw_items = scan_dynamodb_table(dynamodb_client, final_table, ['id', 'field', 'symptomGroupSymptomDiscriminators'])
    records = transform_records(raw_items)

    session = SignedRequestsSession(aws_region)
    success_count, total = index_records(session, endpoint, final_index, records, aws_region, batch_size=args.batch_size, dry_run=args.dry_run)

    log.info('Indexed %d/%d records', success_count, total)
    return 0


if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
