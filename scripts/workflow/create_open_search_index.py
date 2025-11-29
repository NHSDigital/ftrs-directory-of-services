#!/usr/bin/env python3

import os
import sys
import json
import logging
from typing import Optional, Tuple, Dict
import hashlib

import boto3
import botocore.session
import botocore.exceptions
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("create_open_search_index")

MAPPINGS_PAYLOAD = {
    "mappings": {
        "properties": {
            "primary_key": {"type": "keyword"},
            "sgsd": {
                "type": "nested",
                "properties": {
                    "sg": {"type": "integer"},
                    "sd": {"type": "integer"}
                }
            }
        }
    }
}

def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(name, default)

def find_collection_id_by_name(client, collection_name: str) -> Optional[str]:
    resp = client.list_collections()
    for cs in resp.get("collectionSummaries", []):
        if cs.get("name") == collection_name:
            return cs.get("id")
    return None

def get_collection_endpoint_by_id(client, collection_id: str) -> Optional[str]:
    resp = client.batch_get_collection(ids=[collection_id])
    details = resp.get("collectionDetails", [])
    if not details:
        return None
    return details[0].get("collectionEndpoint") or details[0].get("endpoint")

def resolve_collection_endpoint(collection_name: str, region: Optional[str]) -> Optional[str]:
    try:
        kwargs = {}
        if region:
            kwargs["region_name"] = region
        client = boto3.client("opensearchserverless", **kwargs)
        cid = find_collection_id_by_name(client, collection_name)
        if cid is None:
            return None
        return get_collection_endpoint_by_id(client, cid)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as exc:
        log.debug("Failed to resolve collection via boto3: %s", exc, exc_info=True)
        return None

def build_endpoint(raw: str) -> str:
    if raw.startswith("https://"):
        return raw.rstrip('/')
    return "https://" + raw.rstrip('/')

def build_index_name(index: str, workspace: Optional[str]) -> str:
    ws = (workspace or "")
    if ws and not ws.startswith('-'):
        ws = "-" + ws
    return index + ws

def prepare_payload() -> str:
    return json.dumps(MAPPINGS_PAYLOAD)

def get_index_url(open_search_domain: str, index: str, workspace: str, aws_region: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    resolved = open_search_domain if '.' in open_search_domain else resolve_collection_endpoint(open_search_domain, aws_region)
    if not resolved:
        return None, None
    endpoint = build_endpoint(resolved)
    final_index = build_index_name(index, workspace)
    url = endpoint + '/' + final_index
    return url, final_index

def get_aws_signing_credentials():
    session = botocore.session.get_session()
    creds = session.get_credentials()
    if creds is None:
        raise RuntimeError("AWS credentials not found")
    return creds.get_frozen_credentials()

def compute_payload_hash(body: str) -> str:
    if not body:
        return "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    return hashlib.sha256(body.encode("utf-8")).hexdigest()

def build_aws_request(method: str, url: str, body: str, payload_hash: str) -> AWSRequest:
    headers = {"Content-Type": "application/json", "x-amz-content-sha256": payload_hash}
    return AWSRequest(method=method, url=url, data=body, headers=headers)

def sign_aws_request(aws_req: AWSRequest, credentials, service: str, region: Optional[str]) -> None:
    SigV4Auth(credentials, service, region or get_env("AWS_REGION") or "").add_auth(aws_req)

def redact_auth_header(headers: Dict[str, str]) -> str:
    auth_hdr = headers.get('Authorization') or headers.get('authorization') or ''
    if not auth_hdr:
        return ''
    if 'Signature=' in auth_hdr:
        parts = auth_hdr.split('Signature=')
        return parts[0] + 'Signature=<redacted>'
    return auth_hdr

def send_prepared_request(aws_req: AWSRequest, timeout: int = 30) -> requests.Response:
    prepared = requests.Request(method=aws_req.method, url=aws_req.url, data=aws_req.body, headers=dict(aws_req.headers)).prepare()
    session_http = requests.Session()
    try:
        return session_http.send(prepared, timeout=timeout)
    except requests.RequestException as exc:
        log.error('HTTP request failed: %s', exc)
        raise

def log_response_headers(resp: requests.Response) -> None:
    try:
        hdrs = dict(resp.headers)
        redact_keys = {k.lower() for k in ['authorization', 'www-authenticate', 'set-cookie']}
        hdrs_safe = {k: (v if k.lower() not in redact_keys else '<redacted>') for k, v in hdrs.items()}
        log.info('Response headers: %s', json.dumps(hdrs_safe, default=str))
    except (TypeError, ValueError, AttributeError) as exc:
        log.debug('Could not log response headers: %s', exc, exc_info=True)

def sign_request_and_put(url: str, body: str, region: Optional[str], service: str = "aoss") -> requests.Response:
    credentials = get_aws_signing_credentials()
    payload_hash = compute_payload_hash(body)
    aws_req = build_aws_request("PUT", url, body, payload_hash)
    sign_aws_request(aws_req, credentials, service, region)
    signed_headers = dict(aws_req.headers)
    redacted = redact_auth_header(signed_headers)
    if redacted:
        log.info('Signed Authorization header: %s', redacted)
    if any(k.lower() == 'x-amz-content-sha256' for k in signed_headers.keys()):
        log.info('Signed request includes payload hash')
    resp = send_prepared_request(aws_req)
    log_response_headers(resp)
    return resp

def parse_response_body(resp: requests.Response) -> str:
    try:
        return resp.text or ""
    except (UnicodeDecodeError, AttributeError):
        return ""

def handle_response(resp: requests.Response, final_index: str) -> int:
    body_text = parse_response_body(resp)
    log.info('Response: %s %s', resp.status_code, resp.reason)
    log.info('Response body: %s', body_text)
    if resp.status_code in (200, 201):
        log.info('Index %s created or already exists', final_index)
        return 0
    if resp.status_code in (400, 409) and ("already exists" in body_text or "resource_already_exists_exception" in body_text):
        log.info('Index %s already exists; continuing', final_index)
        return 0
    log.error('Index creation failed with status %s', resp.status_code)
    return 4

def get_inputs() -> Tuple[str, str, str, Optional[str]]:
    open_search_domain = get_env("OPEN_SEARCH_DOMAIN")
    index = get_env("INDEX")
    workspace = get_env("WORKSPACE") or ""
    aws_region = get_env("AWS_REGION")
    return open_search_domain, index, workspace, aws_region

def resolve_endpoint_if_needed(open_search_domain: str, aws_region: Optional[str]) -> Optional[str]:
    if '.' in open_search_domain:
        return open_search_domain
    return resolve_collection_endpoint(open_search_domain, aws_region)

def create_index(open_search_domain: str, index: str, workspace: str, aws_region: Optional[str]) -> int:
    url, final_index = get_index_url(open_search_domain, index, workspace, aws_region)
    if not url:
        log.error('Could not resolve collection %s', open_search_domain)
        return 3
    payload = prepare_payload()
    log.info('Creating index using URL: %s', url)
    resp = sign_request_and_put(url, payload, aws_region, 'aoss')
    return handle_response(resp, final_index)

def main() -> int:
    open_search_domain, index, workspace, aws_region = get_inputs()
    if not open_search_domain or not index:
        log.error('OPEN_SEARCH_DOMAIN and INDEX must be set')
        return 2
    try:
        return create_index(open_search_domain, index, workspace, aws_region)
    except (RuntimeError, requests.RequestException) as exc:
        log.error('Exception during index creation: %s', exc)
        return 5

if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
