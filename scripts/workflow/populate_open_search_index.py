#!/usr/bin/env python3.12

import argparse
import hashlib
import json
import logging
import os
import sys
from typing import Optional, Any
from decimal import Decimal
from pathlib import Path

from urllib.parse import quote as urlquote

import boto3
import botocore.exceptions
import botocore.session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.client import BaseClient
from botocore.credentials import ReadOnlyCredentials
from boto3.dynamodb.types import TypeDeserializer
import requests

try:
    from scripts.workflow.create_open_search_index import MAPPINGS_PAYLOAD
except ModuleNotFoundError:
    REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(REPO_ROOT) not in sys.path:
        sys.path.append(str(REPO_ROOT))
    from scripts.workflow.create_open_search_index import MAPPINGS_PAYLOAD

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("populate_open_search_index")

_DESERIALIZER = TypeDeserializer()
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
_DEFAULT_DDB_TABLE_BASE = "ftrs-dos-local-database-healthcare-service"
DEFAULT_DDB_TABLE = _DEFAULT_DDB_TABLE_BASE
DDB_IGNORE_WORKSPACE_DEFAULT = True
INDEXING_TIMEOUT_SECONDS = 60
INDEX_PROPERTIES = MAPPINGS_PAYLOAD.get('mappings', {}).get('properties', {})
PRIMARY_KEY_NAME = 'primary_key' if 'primary_key' in INDEX_PROPERTIES else None
NESTED_COLLECTION_FIELD = next((name for name, spec in INDEX_PROPERTIES.items() if spec.get('type') == 'nested'), 'sgsd')
TOP_LEVEL_OUTPUT_FIELDS = [name for name in INDEX_PROPERTIES.keys() if name not in {NESTED_COLLECTION_FIELD, PRIMARY_KEY_NAME}]
FIELD_KEY_ALIASES: dict[str, tuple[str, ...]] = {
    'primary_key': ('primary_key',),
}
DOC_ID_FIELDS: list[str] = ['primary_key']
PRIMARY_KEY_TEMPLATE = "{primary_key}"

DEFAULT_SCHEMA_CONFIG: dict[str, Any] = {
    "primary_key_template": PRIMARY_KEY_TEMPLATE,
    "doc_id_fields": DOC_ID_FIELDS,
    "top_level": {
        "primary_key": ["primary_key", "id"]
    },
    "nested": {
        NESTED_COLLECTION_FIELD: {
            "source_attributes": ["symptomGroupSymptomDiscriminators"],
            "items": {
                "sg": "sg",
                "sd": "sd"
            }
        }
    }
}

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Populate an OpenSearch Serverless index from a DynamoDB table")
    parser.add_argument("--final-index", dest="final_index", help="Final index name" )
    parser.add_argument("--endpoint", dest="endpoint", help="OpenSearch endpoint" )
    parser.add_argument("--workspace", dest="workspace", default=os.environ.get('WORKSPACE', ''), help="Terraform workspace suffix to append to index/table names (e.g. 'ftrs-856')")
    parser.add_argument("--aws-region", dest="aws_region", default=os.environ.get('AWS_REGION'), help="AWS region")
    parser.add_argument("--dynamodb-table", dest="ddb_table", default=os.environ.get('DYNAMODB_TABLE', DEFAULT_DDB_TABLE), help="DynamoDB table name")
    parser.add_argument("--batch-size", dest="batch_size", type=int, default=1, help="Number of records to send in one bulk request (1 = per-document PUT)")
    parser.add_argument("--log-level", dest="log_level", default=os.environ.get('LOG_LEVEL', 'INFO'))
    parser.add_argument("--schema-config", dest="schema_config", help="Path to JSON schema config that maps DynamoDB attributes to OpenSearch fields")
    parser.add_argument("--dynamodb-table-ignore-workspace", dest="ddb_ignore_workspace", default=str(DDB_IGNORE_WORKSPACE_DEFAULT),
                        help="true|false - when true do NOT append workspace to the DynamoDB table name (default: true)")
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

    def request(self, method: str, url: str, body: Optional[str]) -> requests.Response:
        payload_hash = compute_payload_hash(body)
        aws_req = build_aws_request(method, url, body, payload_hash)
        sign_aws_request(aws_req, self.credentials, self.service, self.aws_region)
        prepared = requests.Request(method=aws_req.method, url=aws_req.url, data=aws_req.body, headers=dict(aws_req.headers)).prepare()
        return self.session.send(prepared, timeout=INDEXING_TIMEOUT_SECONDS)

def prepare_dynamodb_client(region: Optional[str]) -> BaseClient:
    return boto3.client('dynamodb', region_name=region) if region else boto3.client('dynamodb')

def scan_dynamodb_table(dynamodb_client: BaseClient, table_name: str, attributes: list[str]) -> list[dict]:
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

def parse_dynamo_string(attr: dict) -> Optional[str]:
    if not isinstance(attr, dict):
        return None
    if 'S' in attr:
        return attr['S']
    if 'N' in attr:
        return str(attr['N'])
    return None

def _deserialize_attr(attr: Any) -> Any:
    if not isinstance(attr, dict):
        return attr
    if len(attr) == 1 and next(iter(attr.keys())) in {"S", "N", "M", "L", "BOOL", "NULL", "SS", "NS", "BS"}:
        try:
            return _DESERIALIZER.deserialize(attr)
        except (TypeError, ValueError) as exc:
            log.debug('TypeDeserializer failed for %s: %s', attr, exc)
            return attr
    return attr

def _normalize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value

def convert_dynamodb_format(items: list[dict]) -> list[dict[str, Any]]:
    def _parse(entry: Any) -> Optional[dict[str, Any]]:
        deserialized = _normalize(_deserialize_attr(entry))
        if not isinstance(deserialized, dict):
            return None
        sg = deserialized.get('sg')
        sd = deserialized.get('sd')
        if isinstance(sg, dict) or isinstance(sd, dict):
            return {'sg': sg, 'sd': sd}
        return None

    if not isinstance(items, list):
        return []
    return [parsed for parsed in (_parse(item) for item in items) if parsed]

def extract_field(record: dict, aliases: tuple[str, ...]) -> Optional[str]:
    for k in aliases:
        v = record.get(k)
        if v is None:
            continue
        val = parse_dynamo_string(v) or (str(v) if not isinstance(v, dict) else None)
        if val is not None:
            return val
    return None

def extract_nested_from_record(record: dict, schema_config: dict[str, Any]) -> list[dict[str, Any]]:
    nested_cfg = _get_nested_config(schema_config)
    for attr_name in nested_cfg.get('source_attributes', []):
        value = record.get(attr_name)
        items = convert_nested_items(value, nested_cfg)
        if items:
            return items
    return []

def parse_record_to_doc(record: dict, schema_config: dict[str, Any]) -> Optional[dict[str, Any]]:
    try:
        doc: dict[str, Any] = {}
        if TOP_LEVEL_OUTPUT_FIELDS:
            top_fields = TOP_LEVEL_OUTPUT_FIELDS
        elif PRIMARY_KEY_NAME:
            top_fields = [PRIMARY_KEY_NAME]
        else:
            top_fields = []
        for field_name in top_fields:
            aliases = _get_aliases(field_name, schema_config)
            value = extract_field(record, aliases)
            if value is None:
                return None
            doc[field_name] = value

        doc[NESTED_COLLECTION_FIELD] = extract_nested_from_record(record, schema_config)
        if not doc[NESTED_COLLECTION_FIELD]:
            log.debug('Record %s missing %s data', doc.get(PRIMARY_KEY_NAME, '<missing>'), NESTED_COLLECTION_FIELD)

        if PRIMARY_KEY_NAME:
            try:
                template = schema_config.get('primary_key_template', PRIMARY_KEY_TEMPLATE)
                doc_id = template.format(**{k: doc.get(k, '') for k in schema_config.get('doc_id_fields', DOC_ID_FIELDS)})
                doc[PRIMARY_KEY_NAME] = doc_id
            except KeyError:
                log.debug('Failed to build primary key for record=%s', doc)

        return doc
    except (TypeError, ValueError, KeyError):
        log.exception('Error parsing record into document; re-raising')
        raise

def transform_records(raw_items: list[dict], schema_config: Optional[dict[str, Any]] = None) -> list[dict]:
    config = schema_config or DEFAULT_SCHEMA_CONFIG
    if not isinstance(raw_items, list):
        return []
    return [r for r in (parse_record_to_doc(item, config) for item in raw_items) if r]

def build_doc_id(record: dict, schema_config: Optional[dict[str, Any]] = None) -> str:
    config = schema_config or DEFAULT_SCHEMA_CONFIG
    fields = config.get('doc_id_fields', DOC_ID_FIELDS)
    try:
        parts = [str(record[f]) for f in fields]
    except KeyError as exc:
        missing = exc.args[0]
        raise KeyError(f"Missing field {missing} required for document ID") from exc
    separator = config.get('primary_key_template', PRIMARY_KEY_TEMPLATE)
    if '{' in separator:
        return separator.format(**record)
    return "|".join(parts)

def build_doc_path(index_name: str, doc_id: str) -> str:
    return '/' + urlquote(index_name) + '/_doc/' + urlquote(doc_id)

def build_name_with_workspace(name: str, workspace: Optional[str]) -> str:
    ws_raw = (workspace or "").strip()
    if not ws_raw:
        return name
    ws_normalized = ws_raw.lstrip('-')
    suffix = f"-{ws_normalized}" if ws_normalized else ""
    if suffix:
        if name.endswith(suffix):
            return name
        return name + suffix
    return name + ws_raw

def build_bulk_payload(index_name: str, records: list[dict]) -> str:
    lines = [line for record in records for line in (json.dumps({"index": {"_index": index_name, "_id": build_doc_id(record)}}), json.dumps(record))]
    return "\n".join(lines) + "\n"

def index_single_record(session: SignedRequestsSession, endpoint: str, index_name: str, record: dict) -> tuple[bool, int, str]:
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
        return False, status, resp_text
    except requests.RequestException as exc:
        log.error('Request exception indexing id=%s: %s', doc_id, exc)
        return False, 500, str(exc)
    except Exception as exc:
        log.error('Unexpected exception indexing id=%s: %s', doc_id, exc)
        return False, 500, str(exc)

def index_bulk(session: SignedRequestsSession, endpoint: str, index_name: str, records: list[dict]) -> tuple[int, int]:
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
        except ValueError:
            log.debug('Could not parse bulk response JSON; treating as failures')
            return 0, len(records)
    return 0, len(records)

# Helpers extracted from inside index_records to reduce cognitive complexity
def _attempt_index_record(record: dict, session: SignedRequestsSession, endpoint: str, index_name: str) -> int:
    try:
        _ = build_doc_id(record)
    except KeyError:
        log.debug('Skipping record with missing document id fields: %s', record)
        return 0
    key_display = record.get(PRIMARY_KEY_NAME, '<missing>')
    log.info('Indexing record ID: %s', key_display)
    try:
        ok, status, body = index_single_record(session, endpoint, index_name, record)
        if ok:
            return 1
        log.error('Failed to index id=%s status=%s body=%s', key_display, status, body)
        return 0
    except requests.RequestException as exc:
        log.error('Request exception indexing record id=%s: %s', key_display, exc)
        return 0
    except Exception as exc:
        log.error('Unexpected exception indexing record id=%s: %s', key_display, exc)
        return 0


def _process_bulk_chunk(chunk: list[dict], idx: int, total_chunks: int, session: SignedRequestsSession, endpoint: str, index_name: str) -> tuple[int, int]:
    attempted = len(chunk)
    log.info('Bulk indexing %d records (chunk %d/%d)', attempted, idx + 1, total_chunks)
    ok, attempted_returned = index_bulk(session, endpoint, index_name, chunk)
    if ok < attempted_returned:
        log.error('Bulk chunk had %d failures out of %d', attempted_returned - ok, attempted_returned)
    return ok, attempted_returned

def index_records(session: SignedRequestsSession, endpoint: str, index_name: str, records: list[dict], batch_size: int = 1) -> tuple[int, int]:
    success_count = 0
    total = 0
    if batch_size <= 1:
        total = len(records)
        success_count = sum(_attempt_index_record(rec, session, endpoint, index_name) for rec in records)
        return success_count, total
    # bulk path
    if not records:
        return 0, 0
    chunks = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
    total_chunks = len(chunks)
    results = [
        _process_bulk_chunk(chunk, idx, total_chunks, session, endpoint, index_name)
        for idx, chunk in enumerate(chunks)
    ]
    success_count += sum(r[0] for r in results)
    total += sum(r[1] for r in results)
    return success_count, total

def load_schema_config(path: Optional[str]) -> dict[str, Any]:
    if not path:
        return DEFAULT_SCHEMA_CONFIG.copy()
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            loaded = json.load(fh)
    except (OSError, ValueError) as exc:
        log.error('Failed to read or parse schema config %s: %s; falling back to defaults', path, exc)
        return DEFAULT_SCHEMA_CONFIG.copy()
    return loaded

def _get_aliases(field_name: str, schema_config: dict[str, Any]) -> tuple[str, ...]:
    configured = schema_config.get('top_level', {}).get(field_name, [])
    generated = (
        field_name,
        field_name.capitalize(),
        field_name.lower(),
        field_name.upper(),
        field_name.replace('-', ''),
        field_name.replace('_', ''),
        field_name.title()
    )
    aliases: list[str] = []
    for candidate in list(configured) + list(FIELD_KEY_ALIASES.get(field_name, ())) + list(generated):
        if candidate and candidate not in aliases:
            aliases.append(candidate)
    return tuple(aliases)

def _get_nested_config(schema_config: dict[str, Any]) -> dict[str, Any]:
    nested = schema_config.get('nested', {})
    return nested.get(NESTED_COLLECTION_FIELD, {})

def _resolve_attr_path(data: Any, path: str) -> Any:
    if not path:
        return data
    current = data
    for part in path.split('.'):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current

def _coerce_str_value(value: str) -> Any:
    try:
        if value.isdigit():
            return int(value)
        f = float(value)
        return int(f) if f.is_integer() else f
    except (ValueError, TypeError):
        return value

def _map_non_dict_item(deserialized: Any, nested_config: dict[str, Any]) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    for target_field in nested_config.get('items', {}).keys():
        mapped[target_field] = deserialized
    return mapped

def _map_dict_item(deserialized: dict, nested_config: dict[str, Any]) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    for target_field, source_path in nested_config.get('items', {}).items():
        value = _resolve_attr_path(deserialized, source_path)
        if value is None:
            continue
        if isinstance(value, str):
            value = _coerce_str_value(value)
        mapped[target_field] = value
    return mapped

def convert_nested_items(attr: Any, nested_config: dict[str, Any]) -> list[dict[str, Any]]:
    if not attr:
        return []
    if isinstance(attr, dict) and 'L' in attr:
        items = attr['L']
    elif isinstance(attr, list):
        items = attr
    else:
        return []

    results: list[dict[str, Any]] = []
    for entry in items:
        deserialized = _normalize(_deserialize_attr(entry))
        if not isinstance(deserialized, dict):
            mapped = _map_non_dict_item(deserialized, nested_config)
            if mapped:
                results.append(mapped)
            continue

        mapped = _map_dict_item(deserialized, nested_config)
        if mapped:
            results.append(mapped)

    return results

def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    log.setLevel(getattr(logging, args.log_level.upper(), logging.INFO))

    try:
        validate_inputs(args.endpoint or os.environ.get('OS_ENDPOINT'),
                        args.final_index or os.environ.get('OS_FINAL_INDEX'))
    except SystemExit as e:
        return int(e.code)

    endpoint_input = args.endpoint or os.environ.get('OS_ENDPOINT')
    endpoint = build_endpoint(endpoint_input) if endpoint_input else None

    aws_region = args.aws_region
    ddb_table = args.ddb_table
    workspace = args.workspace or os.environ.get('WORKSPACE', '')

    ddb_ignore_workspace = str(args.ddb_ignore_workspace).strip().lower() in ("1", "true", "yes")

    final_table = ddb_table if ddb_ignore_workspace or not ddb_table else build_name_with_workspace(ddb_table, workspace)

    base_index = args.final_index or os.environ.get('OS_FINAL_INDEX') or "triage_code"
    final_index = build_name_with_workspace(base_index, workspace)

    log.info('Using configuration:')
    log.info('  Endpoint: %s', endpoint)
    log.info('  Final index: %s', final_index)
    log.info('  AWS region: %s', aws_region)
    log.info('  DynamoDB table: %s', final_table)
    log.info('  Workspace: %s', workspace)

    schema_config = load_schema_config(args.schema_config)
    session = SignedRequestsSession(aws_region)

    try:
        log.info('Scanning DynamoDB table...')
        raw_items = scan_dynamodb_table(prepare_dynamodb_client(aws_region), final_table, ['id', 'primary_key', 'symptomGroupSymptomDiscriminators'])
        log.info('Transforming records...')
        transformed = transform_records(raw_items, schema_config)
        if transformed:
            log.debug('Sample transformed record: %s', json.dumps(transformed[0], default=str))
        log.info('Indexing records...')
        success, total = index_records(session, endpoint, final_index, transformed, args.batch_size)
        log.info('Indexing complete: %d successful, %d total records', success, total)
    except Exception as exc:
        log.error('Unexpected error: %s', exc)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
