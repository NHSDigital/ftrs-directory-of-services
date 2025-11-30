#!/usr/bin/env python3

import os
import sys
import json
import logging
from typing import Optional, Tuple, Dict
import hashlib
import argparse

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
    return next((cs.get("id") for cs in resp.get("collectionSummaries", []) if cs.get("name") == collection_name), None)


def get_collection_endpoint_by_id(client, collection_id: str) -> Optional[str]:
    resp = client.batch_get_collection(ids=[collection_id])
    details = resp.get("collectionDetails", [])
    if not details:
        return None
    return next((d.get("collectionEndpoint") or d.get("endpoint") for d in details if d), None)


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
    try:
        caller_info = boto3.client('sts').get_caller_identity()
        log.info('Caller ARN: %s', caller_info.get('Arn'))
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as exc:
        log.debug('Could not get caller identity via STS: %s', exc, exc_info=True)
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
    if resp.status_code in (400, 409) and (
        "already exists" in body_text or "resource_already_exists_exception" in body_text):
        log.info('Index %s already exists; continuing', final_index)
        return 0
    if resp.status_code == 403:
        log.error(
            'Index creation failed with status 403 Forbidden: ensure collection access policy allows the IAM role ARN and resource')
        return 4
    log.error('Index creation failed with status %s', resp.status_code)
    return 4

def get_inputs_from_args(args: argparse.Namespace) -> Tuple[Optional[str], Optional[str], str, Optional[str]]:
    open_search_domain = args.open_search_domain or get_env("OPEN_SEARCH_DOMAIN")
    index = args.index or get_env("INDEX")
    workspace = args.workspace or get_env("WORKSPACE") or ""
    aws_region = args.aws_region or get_env("AWS_REGION")
    return open_search_domain, index, workspace, aws_region

def write_github_output(mapping: Dict[str, str]) -> None:
    gh_out = os.environ.get('GITHUB_OUTPUT')
    if not gh_out:
        return
    try:
        with open(gh_out, 'a') as f:
            for k, v in mapping.items():
                f.write("{}={}\n".format(k, v))
    except Exception as exc:
        log.debug('Failed to write outputs to GITHUB_OUTPUT: %s', exc, exc_info=True)

class IndexCreator:

    def __init__(self, open_search_domain: str, index: str, workspace: Optional[str], aws_region: Optional[str]):
        self.open_search_domain = open_search_domain
        self.index = index
        self.workspace = workspace or ""
        self.aws_region = aws_region

    def create_index(self) -> int:
        resolved = self.open_search_domain if '.' in self.open_search_domain else resolve_collection_endpoint(self.open_search_domain, self.aws_region)
        if not resolved:
            log.error('Could not resolve collection %s', self.open_search_domain)
            return 3
        endpoint = build_endpoint(resolved)
        final_index = build_index_name(self.index, self.workspace)
        url = endpoint.rstrip('/') + '/' + final_index

        payload = prepare_payload()
        log.info('Creating index using URL: %s', url)
        resp = sign_request_and_put(url, payload, self.aws_region, 'aoss')
        result_code = handle_response(resp, final_index)
        if result_code == 0:
            write_github_output({"endpoint": endpoint, "final_index": final_index})
        return result_code

def create_index(open_search_domain: str, index: str, workspace: str, aws_region: Optional[str]) -> int:
    creator = IndexCreator(open_search_domain, index, workspace, aws_region)
    return creator.create_index()

def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Create OpenSearch Serverless index')
    p.add_argument('--open-search-domain', help='OpenSearch collection name or full endpoint URL')
    p.add_argument('--index', help='Index name (base) to create')
    p.add_argument('--workspace', help='Workspace suffix to append to index')
    p.add_argument('--aws-region', help='AWS region to use')
    p.add_argument('--debug', action='store_true', help='Enable debug logging')
    return p.parse_args(argv)

def main(argv=None) -> int:
    args = parse_args(argv)
    if args.debug:
        log.setLevel(logging.DEBUG)
    open_search_domain, index, workspace, aws_region = get_inputs_from_args(args)
    if not open_search_domain or not index:
        log.error('OPEN_SEARCH_DOMAIN and INDEX must be set (via args or env)')
        return 2
    try:
        return create_index(open_search_domain, index, workspace, aws_region)
    except (RuntimeError, requests.RequestException) as exc:
        log.error('Exception during index creation: %s', exc)
        return 5

if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
