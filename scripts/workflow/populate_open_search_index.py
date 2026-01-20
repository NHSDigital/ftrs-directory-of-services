#!/usr/bin/env python3.12

import argparse
import json
import logging
import os
import sys
from typing import Optional, Any, Mapping
from decimal import Decimal
import hashlib
from pathlib import Path

from urllib.parse import quote as urlquote
from urllib.parse import urlparse

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

DynamoDbItem = dict[str, Any]
DeserializedItem = dict[str, Any]
OpenSearchRecord = dict[str, Any]

INDEX_PROPERTIES: dict[str, Any] = (
    MAPPINGS_PAYLOAD.get("mappings", {}).get("properties", {})
    if isinstance(MAPPINGS_PAYLOAD, dict)
    else {}
)

NESTED_COLLECTION_FIELD = next(
    (
        name
        for name, spec in INDEX_PROPERTIES.items()
        if isinstance(spec, dict) and spec.get("type") == "nested"
    ),
    "sgsd",
)

PRIMARY_KEY_NAME = "primary_key"

TOP_LEVEL_OUTPUT_FIELDS: list[str] = [
    name
    for name in INDEX_PROPERTIES.keys()
    if name not in {NESTED_COLLECTION_FIELD, PRIMARY_KEY_NAME}
]

FIELD_KEY_ALIASES: dict[str, tuple[str, ...]] = {
    "primary_key": ("primary_key",),
}

DOC_ID_FIELDS: list[str] = ["primary_key"]
PRIMARY_KEY_TEMPLATE = "{primary_key}"

DEFAULT_SCHEMA_CONFIG: dict[str, Any] = {
    "primary_key_template": PRIMARY_KEY_TEMPLATE,
    "doc_id_fields": DOC_ID_FIELDS,
    "top_level": {
        "primary_key": ["primary_key", "id"],
    },
    "nested": {
        NESTED_COLLECTION_FIELD: {
            "source_attributes": ["symptomGroupSymptomDiscriminators"],
            "items": {
                "sg": "sg",
                "sd": "sd",
            },
        }
    },
}

_DESERIALIZER = TypeDeserializer()
_DEFAULT_DDB_TABLE_BASE = "ftrs-dos-local-database-healthcare-service"
DEFAULT_DDB_TABLE = _DEFAULT_DDB_TABLE_BASE
DDB_IGNORE_WORKSPACE_DEFAULT = True
INDEXING_TIMEOUT_SECONDS = 60
MAX_RETRIES = 2
RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Populate an OpenSearch Serverless index from a DynamoDB table")
    parser.add_argument("--final-index", dest="final_index", help="Final index name" )
    parser.add_argument("--endpoint", dest="endpoint", help="OpenSearch endpoint" )
    parser.add_argument(
        "--sigv4-service",
        dest="sigv4_service",
        default=os.environ.get("OS_SIGV4_SERVICE"),
        help="SigV4 service name to sign requests with ('aoss' for OpenSearch Serverless, 'es' for managed OpenSearch). If omitted, inferred from endpoint hostname.",
    )
    parser.add_argument("--workspace", dest="workspace", default=os.environ.get('WORKSPACE', ''), help="Terraform workspace suffix to append to index/table names (e.g. 'ftrs-856')")
    parser.add_argument("--aws-region", dest="aws_region", default=os.environ.get('AWS_REGION'), help="AWS region")
    parser.add_argument("--dynamodb-table", dest="ddb_table", default=os.environ.get('DYNAMODB_TABLE', DEFAULT_DDB_TABLE), help="DynamoDB table name")
    parser.add_argument("--batch-size", dest="batch_size", type=int, default=200, help="Number of records to send in one bulk request (1 = per-document PUT)")
    parser.add_argument(
        "--fail-fast",
        dest="fail_fast",
        action="store_true",
        default=False,
        help="Stop immediately on the first indexing failure",
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        default=os.environ.get('LOG_LEVEL', 'INFO'))
    parser.add_argument(
        "--schema-config",
        dest="schema_config",
        help="Path to JSON schema config that maps DynamoDB attributes to OpenSearch fields")
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


def _infer_sigv4_service_from_endpoint(endpoint: str) -> str:
    hostname = urlparse(endpoint).hostname or ""
    host = hostname.lower()
    if ".aoss." in host or host.endswith(".aoss.amazonaws.com"):
        return "aoss"
    if ".es." in host or host.endswith(".es.amazonaws.com"):
        return "es"
    return "aoss"


def _require_region(region: Optional[str]) -> str:
    region_value = (region or os.environ.get("AWS_REGION") or "").strip()
    if region_value:
        return region_value
    try:
        session = botocore.session.get_session()
        resolved = (session.get_config_variable("region") or "").strip()
        if resolved:
            return resolved
    except (botocore.exceptions.BotoCoreError, AttributeError, TypeError, ValueError):
        pass
    raise RuntimeError("AWS region is required for SigV4 signing (set --aws-region or AWS_REGION)")

def get_aws_signing_credentials() -> ReadOnlyCredentials:
    session = botocore.session.get_session()
    creds = session.get_credentials()
    if creds is None:
        raise RuntimeError("AWS credentials not found")
    return creds.get_frozen_credentials()

def build_aws_request(method: str, url: str, body: Optional[str]) -> AWSRequest:
    payload = body or ""
    payload_hash = (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        if not payload
        else hashlib.sha256(payload.encode("utf-8")).hexdigest()
    )
    headers = {
        "Content-Type": "application/json",
        "x-amz-content-sha256": payload_hash,
    }
    return AWSRequest(method=method, url=url, data=payload, headers=headers)

def sign_aws_request(aws_req: AWSRequest, credentials: ReadOnlyCredentials, service: str, region: Optional[str]) -> None:
    SigV4Auth(credentials, service, _require_region(region)).add_auth(aws_req)

class SignedRequestsSession:
    def __init__(self, aws_region: Optional[str], service: str = "aoss") -> None:
        self.aws_region = aws_region
        self.service = service
        self.session = requests.Session()
        self.credentials = get_aws_signing_credentials()

    def request(self, method: str, url: str, body: Optional[str]) -> requests.Response:
        aws_req = build_aws_request(method, url, body)
        sign_aws_request(aws_req, self.credentials, self.service, self.aws_region)
        prepared = requests.Request(method=aws_req.method, url=aws_req.url, data=aws_req.body, headers=dict(aws_req.headers)).prepare()
        return self.session.send(prepared, timeout=INDEXING_TIMEOUT_SECONDS)

def prepare_dynamodb_client(region: Optional[str]) -> BaseClient:
    return boto3.client('dynamodb', region_name=region) if region else boto3.client('dynamodb')

def scan_dynamodb_table(
    dynamodb_client: BaseClient, table_name: str, attributes: list[str]
) -> list[DynamoDbItem]:
    paginator = dynamodb_client.get_paginator('scan')
    projection = ",".join(attributes) if attributes else None
    scan_kwargs = {}
    if projection:
        scan_kwargs['ProjectionExpression'] = projection
    try:
        items: list[DynamoDbItem] = [
            item
            for page in paginator.paginate(TableName=table_name, **scan_kwargs)
            for item in page.get('Items', [])
        ]
    except botocore.exceptions.ClientError as exc:
        log.error('DynamoDB scan failed: %s', exc)
        raise
    return items


def _normalize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value

def deserialize_dynamodb_item(item: Any) -> Optional[DeserializedItem]:
    if not isinstance(item, dict):
        return None
    try:
        deserialized = _DESERIALIZER.deserialize({"M": item})
        normalized = _normalize(deserialized)
        return normalized if isinstance(normalized, dict) else None
    except (TypeError, ValueError) as exc:
        log.debug("Failed to deserialize DynamoDB item: %s", exc, exc_info=True)
        return None

def deserialize_dynamodb_items(items: list[dict]) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        return []
    out: list[DeserializedItem] = []
    for item in items:
        parsed = deserialize_dynamodb_item(item)
        if parsed is not None:
            out.append(parsed)
    return out

def _to_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    return None

def extract_field(record: Mapping[str, Any], aliases: tuple[str, ...]) -> Optional[str]:
    for k in aliases:
        v = record.get(k)
        if v is None:
            continue
        val = _to_str(v)
        if val is not None:
            return val
    return None

def extract_nested_from_record(
    record: Mapping[str, Any], schema_config: dict[str, Any]
) -> list[dict[str, Any]]:
    nested_cfg = _get_nested_config(schema_config)
    for attr_name in nested_cfg.get('source_attributes', []):
        value = record.get(attr_name)
        items = convert_nested_items(value, nested_cfg)
        if items:
            return items
    return []

def parse_record_to_doc(
    record: Mapping[str, Any], schema_config: dict[str, Any]
) -> Optional[OpenSearchRecord]:
    doc: OpenSearchRecord = {}
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
    if PRIMARY_KEY_NAME:
        template = schema_config.get('primary_key_template', PRIMARY_KEY_TEMPLATE)
        doc_id = template.format(**{k: doc.get(k, '') for k in schema_config.get('doc_id_fields', DOC_ID_FIELDS)})
        doc[PRIMARY_KEY_NAME] = doc_id

    return doc

def transform_records(
    raw_items: Any, schema_config: Optional[dict[str, Any]] = None
) -> list[OpenSearchRecord]:
    config = schema_config or DEFAULT_SCHEMA_CONFIG
    if not isinstance(raw_items, list):
        return []
    return [r for r in (parse_record_to_doc(item, config) for item in raw_items) if r]

def build_doc_id(record: Mapping[str, Any], schema_config: Optional[dict[str, Any]] = None) -> str:
    config = schema_config or DEFAULT_SCHEMA_CONFIG
    fields = config.get('doc_id_fields', DOC_ID_FIELDS)
    separator = config.get('primary_key_template', PRIMARY_KEY_TEMPLATE)
    if '{' in separator:
        try:
            return separator.format(**record)
        except KeyError as exc:
            missing = exc.args[0]
            raise KeyError(f"Missing field {missing} required for document ID") from exc

    try:
        parts = [str(record[f]) for f in fields]
    except KeyError as exc:
        missing = exc.args[0]
        raise KeyError(f"Missing field {missing} required for document ID") from exc
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

def build_bulk_payload(index_name: str, records: list[OpenSearchRecord]) -> str:
    lines = [line for record in records for line in (json.dumps({"index": {"_index": index_name, "_id": build_doc_id(record)}}), json.dumps(record))]
    return "\n".join(lines) + "\n"

def _safe_response_text(resp: requests.Response) -> str:
    try:
        return resp.text or ""
    except (requests.RequestException, UnicodeDecodeError, AttributeError):
        return ""

def _safe_response_json(resp: requests.Response) -> dict[str, Any] | None:
    try:
        value = resp.json()
    except (requests.RequestException, ValueError, TypeError, AttributeError):
        return None
    return value if isinstance(value, dict) else None

def _is_success_status(status: int) -> bool:
    return status in (200, 201, 202)

def _should_retry_status(status: int) -> bool:
    return status in RETRYABLE_STATUS_CODES

def _send_with_retries(
    session: "SignedRequestsSession",
    method: str,
    url: str,
    body: Optional[str],
    *,
    max_retries: int = MAX_RETRIES,
) -> requests.Response:
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            resp = session.request(method, url, body)
        except Exception as exc:
            last_exc = exc
            if attempt >= max_retries:
                raise
            continue
        if _should_retry_status(resp.status_code) and attempt < max_retries:
            continue
        return resp
    raise RuntimeError(str(last_exc) if last_exc else "request failed")

def index_single_record(
    session: SignedRequestsSession,
    endpoint: str,
    index_name: str,
    record: OpenSearchRecord,
) -> tuple[bool, int, str]:
    doc_id = build_doc_id(record)
    path = build_doc_path(index_name, doc_id)
    url = endpoint.rstrip('/') + path
    body = json.dumps(record)

    try:
        resp = _send_with_retries(session, 'PUT', url, body)
        resp_text = _safe_response_text(resp)
        status = resp.status_code
        if _is_success_status(status):
            return True, status, resp_text
        return False, status, resp_text
    except Exception as exc:
        log.error('Exception indexing id=%s: %s', doc_id, exc)
        return False, 500, str(exc)

def index_bulk(
    session: SignedRequestsSession,
    endpoint: str,
    index_name: str,
    records: list[OpenSearchRecord],
) -> tuple[int, int]:
    if not records:
        return 0, 0
    payload = build_bulk_payload(index_name, records)
    url = endpoint.rstrip('/') + '/_bulk'
    try:
        resp = _send_with_retries(session, 'POST', url, payload)
    except Exception as exc:
        log.error('Exception bulk indexing %d records: %s', len(records), exc)
        return 0, len(records)
    if not _is_success_status(resp.status_code):
        return 0, len(records)

    body_dict = _safe_response_json(resp)
    if not body_dict:
        return 0, len(records)

    items = body_dict.get('items', [])
    if not isinstance(items, list):
        return 0, len(records)

    success = 0
    for it in items:
        if not isinstance(it, dict) or 'index' not in it:
            continue
        index_obj = it.get('index')
        if not isinstance(index_obj, dict):
            continue
        status = index_obj.get('status', 500)
        if isinstance(status, int) and 200 <= status < 300:
            success += 1

    return success, len(records)

def _attempt_index_record(
    record: OpenSearchRecord,
    session: SignedRequestsSession,
    endpoint: str,
    index_name: str,
) -> int:
    try:
        _ = build_doc_id(record)
    except KeyError:
        return 0
    key_display = record.get(PRIMARY_KEY_NAME, '<missing>')
    log.info('Indexing record ID: %s', key_display)
    ok, status, body = index_single_record(session, endpoint, index_name, record)
    if ok:
        return 1
    log.error('Failed to index id=%s status=%s body=%s', key_display, status, body)
    return 0


def _process_bulk_chunk(
    chunk: list[OpenSearchRecord],
    idx: int,
    total_chunks: int,
    session: SignedRequestsSession,
    endpoint: str,
    index_name: str,
) -> tuple[int, int]:
    attempted = len(chunk)
    log.info('Bulk indexing %d records (chunk %d/%d)', attempted, idx + 1, total_chunks)
    ok, attempted_returned = index_bulk(session, endpoint, index_name, chunk)
    if ok < attempted_returned:
        log.error('Bulk chunk had %d failures out of %d', attempted_returned - ok, attempted_returned)
    return ok, attempted_returned

def index_records(
    session: SignedRequestsSession,
    endpoint: str,
    index_name: str,
    records: list[OpenSearchRecord],
    batch_size: int = 1,
) -> tuple[int, int]:
    return _index_records_impl(session, endpoint, index_name, records, batch_size, fail_fast=False)


def _index_records_impl(
    session: SignedRequestsSession,
    endpoint: str,
    index_name: str,
    records: list[OpenSearchRecord],
    batch_size: int,
    *,
    fail_fast: bool,
) -> tuple[int, int]:
    success_count = 0
    total = 0
    if batch_size <= 1:
        total = len(records)
        for rec in records:
            ok = _attempt_index_record(rec, session, endpoint, index_name)
            success_count += ok
            if fail_fast and not ok:
                return success_count, total
        return success_count, total
    if not records:
        return 0, 0
    chunks = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
    total_chunks = len(chunks)
    for idx, chunk in enumerate(chunks):
        ok, attempted = _process_bulk_chunk(chunk, idx, total_chunks, session, endpoint, index_name)
        success_count += ok
        total += attempted
        if fail_fast and ok < attempted:
            return success_count, total
    return success_count, total

def load_schema_config(path: Optional[str]) -> dict[str, Any]:
    if not path:
        return DEFAULT_SCHEMA_CONFIG.copy()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
    except (OSError, ValueError) as exc:
        log.error("Failed to read or parse schema config %s: %s; falling back to defaults", path, exc)
        return DEFAULT_SCHEMA_CONFIG.copy()
    return loaded

def _get_aliases(field_name: str, schema_config: dict[str, Any]) -> tuple[str, ...]:
    configured = schema_config.get("top_level", {}).get(field_name, [])
    generated = (
        field_name,
        field_name.capitalize(),
        field_name.lower(),
        field_name.upper(),
        field_name.replace("-", ""),
        field_name.replace("_", ""),
        field_name.title(),
    )
    aliases: list[str] = []
    for candidate in list(configured) + list(FIELD_KEY_ALIASES.get(field_name, ())) + list(generated):
        if candidate and candidate not in aliases:
            aliases.append(candidate)
    return tuple(aliases)

def _get_nested_config(schema_config: dict[str, Any]) -> dict[str, Any]:
    nested = schema_config.get("nested", {})
    return nested.get(NESTED_COLLECTION_FIELD, {})

def _resolve_attr_path(data: Any, path: str) -> Any:
    if not path:
        return data
    current = data
    for part in path.split("."):
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
    for target_field in nested_config.get("items", {}).keys():
        mapped[target_field] = deserialized
    return mapped

def _map_dict_item(deserialized: Mapping[str, Any], nested_config: dict[str, Any]) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    for target_field, source_path in nested_config.get("items", {}).items():
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
    if not isinstance(attr, list):
        return []

    results: list[dict[str, Any]] = []
    for entry in attr:
        deserialized = _normalize(entry)
        if not isinstance(deserialized, dict):
            mapped = _map_non_dict_item(deserialized, nested_config)
            if mapped:
                results.append(mapped)
            continue

        mapped = _map_dict_item(deserialized, nested_config)
        if mapped:
            results.append(mapped)

    return results


def _resolve_sigv4_service(endpoint: Optional[str], explicit_service: Optional[str]) -> str:
    explicit = (explicit_service or "").strip()
    if explicit:
        return explicit
    if endpoint:
        return _infer_sigv4_service_from_endpoint(endpoint)
    return "aoss"


def _resolve_workspace(workspace: Optional[str]) -> str:
    return (workspace or os.environ.get("WORKSPACE") or "").strip()


def _resolve_final_table(ddb_table: str, workspace: str, ignore_workspace: bool) -> str:
    if ignore_workspace or not ddb_table:
        return ddb_table
    return build_name_with_workspace(ddb_table, workspace)


def _resolve_final_index(final_index: Optional[str], workspace: str) -> str:
    base_index = final_index or os.environ.get("OS_FINAL_INDEX") or "triage_code"
    return build_name_with_workspace(base_index, workspace)


def _log_configuration(
    *,
    endpoint: Optional[str],
    final_index: str,
    aws_region: Optional[str],
    sigv4_service: str,
    final_table: str,
    workspace: str,
) -> None:
    log.info('Using configuration:')
    log.info('  Endpoint: %s', endpoint)
    log.info('  Final index: %s', final_index)
    log.info('  AWS region: %s', aws_region)
    log.info('  SigV4 service: %s', sigv4_service)
    log.info('  DynamoDB table: %s', final_table)
    log.info('  Workspace: %s', workspace)


def _run_population(
    *,
    aws_region: Optional[str],
    final_table: str,
    endpoint: str,
    final_index: str,
    schema_config: dict[str, Any],
    session: SignedRequestsSession,
    batch_size: int,
    fail_fast: bool,
 ) -> None:
    log.info('Scanning DynamoDB table...')
    raw_items = scan_dynamodb_table(
        prepare_dynamodb_client(aws_region),
        final_table,
        ['id', 'primary_key', 'symptomGroupSymptomDiscriminators'],
    )
    deserialized_items = deserialize_dynamodb_items(raw_items)

    log.info('Transforming records...')
    transformed = transform_records(deserialized_items, schema_config)

    log.info('Indexing records...')
    success, total = _index_records_impl(session, endpoint, final_index, transformed, batch_size, fail_fast=fail_fast)
    log.info('Indexing complete: %d successful, %d total records', success, total)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    log.setLevel(getattr(logging, args.log_level.upper(), logging.INFO))

    validate_inputs(args.endpoint or os.environ.get('OS_ENDPOINT'),
                    args.final_index or os.environ.get('OS_FINAL_INDEX'))

    endpoint_input = args.endpoint or os.environ.get('OS_ENDPOINT')
    endpoint = build_endpoint(endpoint_input) if endpoint_input else None

    aws_region = args.aws_region
    sigv4_service = _resolve_sigv4_service(endpoint, args.sigv4_service)

    ddb_table = args.ddb_table
    workspace = _resolve_workspace(args.workspace)

    ddb_ignore_workspace = str(args.ddb_ignore_workspace).strip().lower() in ("1", "true", "yes")

    final_table = _resolve_final_table(ddb_table, workspace, ddb_ignore_workspace)
    final_index = _resolve_final_index(args.final_index, workspace)

    _log_configuration(
        endpoint=endpoint,
        final_index=final_index,
        aws_region=aws_region,
        sigv4_service=sigv4_service,
        final_table=final_table,
        workspace=workspace,
    )

    schema_config = load_schema_config(args.schema_config)
    session = SignedRequestsSession(aws_region, sigv4_service)

    try:
        if endpoint is None:
            raise RuntimeError("OpenSearch endpoint is missing")
        _run_population(
            aws_region=aws_region,
            final_table=final_table,
            endpoint=endpoint,
            final_index=final_index,
            schema_config=schema_config,
            session=session,
            batch_size=args.batch_size,
            fail_fast=args.fail_fast,
        )
    except (RuntimeError, botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError, requests.RequestException) as exc:
        log.error('Unexpected error: %s', exc)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
