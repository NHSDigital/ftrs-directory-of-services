#!/usr/bin/env python3

import os
import sys
import json
import logging
from typing import Optional
import hashlib

import boto3
import botocore.session
import botocore.exceptions
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("create_open_search_index")


def env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(name, default)


def resolve_serverless_collection(name: str, region: Optional[str]) -> Optional[str]:
    try:
        kwargs = {}
        if region:
            kwargs["region_name"] = region
        client = boto3.client("opensearchserverless", **kwargs)
        resp = client.list_collections()
        for cs in resp.get("collectionSummaries", []):
            if cs.get("name") == name:
                cid = cs.get("id")
                break
        else:
            return None
        resp2 = client.batch_get_collection(ids=[cid])
        details = resp2.get("collectionDetails", [])
        if not details:
            return None
        ep = details[0].get("collectionEndpoint") or details[0].get("endpoint")
        return ep
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as exc:
        log.debug('Failed to resolve collection via boto3: %s', exc, exc_info=True)
        return None


def sign_and_send_put(url: str, body: str, region: Optional[str], service: str = "aoss") -> requests.Response:
    session = botocore.session.get_session()
    creds = session.get_credentials()
    if creds is None:
        raise RuntimeError("AWS credentials not found")
    frozen = creds.get_frozen_credentials()
    payload_sha256 = hashlib.sha256(body.encode("utf-8")).hexdigest() if body else "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    headers = {"Content-Type": "application/json", "x-amz-content-sha256": payload_sha256}
    aws_request = AWSRequest(method="PUT", url=url, data=body, headers=headers)
    SigV4Auth(frozen, service, region or os.environ.get("AWS_REGION") or "").add_auth(aws_request)
    hdrs = dict(aws_request.headers)
    auth = hdrs.get('Authorization') or hdrs.get('authorization')
    if auth:
        redacted_auth = auth
        if 'Signature=' in auth:
            parts = auth.split('Signature=')
            redacted_auth = parts[0] + 'Signature=<redacted>'
        log.info('Signed Authorization header: %s', redacted_auth)
    if any(k.lower() == 'x-amz-content-sha256' for k in hdrs.keys()):
        log.info('Signed request includes payload hash')
    prepared = requests.Request(method=aws_request.method, url=aws_request.url, data=aws_request.body, headers=dict(aws_request.headers)).prepare()
    s = requests.Session()
    try:
        resp = s.send(prepared, timeout=30)
    except requests.RequestException as exc:
        log.error('HTTP request failed: %s', exc)
        raise
    try:
        hdrs = dict(resp.headers)
        redact_keys = {k.lower() for k in ['authorization', 'www-authenticate', 'set-cookie']}
        hdrs_safe = {k: (v if k.lower() not in redact_keys else '<redacted>') for k, v in hdrs.items()}
        log.info('Response headers: %s', json.dumps(hdrs_safe, default=str))
    except (TypeError, ValueError, AttributeError) as exc:
        log.debug('Could not log response headers: %s', exc, exc_info=True)
    return resp


def main() -> int:
    open_search_domain = env("OPEN_SEARCH_DOMAIN")
    index = env("INDEX")
    workspace = env("WORKSPACE") or ""
    aws_region = env("AWS_REGION")
    if not open_search_domain or not index:
        log.error('OPEN_SEARCH_DOMAIN and INDEX must be set')
        return 2
    if '.' not in open_search_domain:
        resolved = resolve_serverless_collection(open_search_domain, aws_region)
        if resolved:
            open_search_domain = resolved
            log.info('Resolved collection endpoint: %s', open_search_domain)
        else:
            log.error('Could not resolve collection %s', open_search_domain)
            return 3
    if open_search_domain.startswith('https://'):
        endpoint = open_search_domain.rstrip('/')
    else:
        endpoint = 'https://' + open_search_domain.rstrip('/')
    if workspace and not workspace.startswith('-'):
        workspace = '-' + workspace
    final_index = "{}{}".format(index, workspace)
    url = "{}/{}".format(endpoint, final_index)
    payload = json.dumps({
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
    })
    log.info('Creating index using URL: %s', url)
    try:
        resp = sign_and_send_put(url, payload, aws_region, 'aoss')
        log.info('Response: %s %s', resp.status_code, resp.reason)
        try:
            log.info('Response body: %s', resp.text)
        except (UnicodeDecodeError, AttributeError) as exc:
            log.debug('Could not read response body: %s', exc)
        if resp.status_code in (200, 201):
            log.info('Index %s created or already exists', final_index)
            return 0
        else:
            log.error('Index creation failed with status %s', resp.status_code)
            return 4
    except (RuntimeError, requests.RequestException) as exc:
        log.error('Exception during index creation: %s', exc)
        return 5

if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
