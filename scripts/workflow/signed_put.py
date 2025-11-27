#!/usr/bin/env python3
"""
Small helper to perform a SigV4-signed PUT request to an OpenSearch endpoint using boto3 credentials.
Usage: signed_put.py <url> <payload-file>

This avoids depending on awscurl; it signs with current AWS credentials (boto3 session).
"""
import sys
import json
import logging
from urllib.parse import urlparse

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)


def mask_auth_header(auth_value: str) -> str:
    # Mask AWS Access Key and signature parts for safe logging
    # Authorization header looks like: AWS4-HMAC-SHA256 Credential=AKIA.../2025..., SignedHeaders=..., Signature=...
    try:
        parts = auth_value.split(',')
        masked_parts = []
        for p in parts:
            if 'Credential=' in p:
                cred = p.split('=')[1]
                # mask the access key id portion before the '/'
                ak, rest = cred.split('/', 1)
                masked_ak = ak[:4] + '...' + ak[-4:]
                masked_parts.append('Credential=' + masked_ak + '/' + rest)
            elif 'Signature=' in p:
                sig = p.split('=')[1]
                masked_sig = sig[:6] + '...' + sig[-6:]
                masked_parts.append('Signature=' + masked_sig)
            else:
                masked_parts.append(p)
        return ','.join(masked_parts)
    except Exception:
        return '<masked>'


def main():
    if len(sys.argv) < 3:
        print("Usage: signed_put.py <url> <payload-file>")
        sys.exit(2)

    url = sys.argv[1]
    payload_file = sys.argv[2]

    with open(payload_file, 'r') as fh:
        payload = fh.read()

    session = boto3.Session()
    creds = session.get_credentials()
    if creds is None:
        log.error('No AWS credentials available in boto3 session')
        sys.exit(3)

    # botocore credentials are lazy, get the frozen credentials
    frozen = creds.get_frozen_credentials()

    parsed = urlparse(url)
    service = 'aoss'  # service for OpenSearch Serverless
    host = parsed.netloc
    # Try to infer region from host (example: <id>.eu-west-2.aoss.amazonaws.com)
    region = None
    try:
        parts = parsed.netloc.split('.')
        # find the first segment that looks like a region (contains '-')
        for seg in parts:
            if '-' in seg and seg.count('-') >= 1:
                region = seg
                break
    except Exception:
        region = ''

    if not region:
        log.warning('Could not infer region from URL host; falling back to boto3 session region')
        region = session.region_name or ''

    request = AWSRequest(method='PUT', url=url, data=payload, headers={'Content-Type': 'application/json'})
    SigV4Auth(frozen, service, region).add_auth(request)
    prepared = request.prepare()

    # Transfer headers to requests format
    headers = dict(prepared.headers.items())

    # Diagnostic logging - mask sensitive parts
    log.info('Sending signed PUT to %s', url)
    auth_hdr = headers.get('Authorization', '<none>')
    masked_auth = mask_auth_header(auth_hdr) if auth_hdr != '<none>' else '<none>'
    log.info('Signed request region=%s service=%s host=%s', region, service, host)
    log.info('Authorization: %s', masked_auth)
    if 'x-amz-date' in headers:
        log.info('x-amz-date: %s', headers.get('x-amz-date'))
    if 'X-Amz-Date' in headers:
        log.info('X-Amz-Date: %s', headers.get('X-Amz-Date'))

    resp = requests.put(url, data=payload, headers=headers, timeout=30)
    log.info('Response: %s %s', resp.status_code, resp.text)
    if resp.status_code >= 400:
        log.error('Signed PUT failed with HTTP %s', resp.status_code)
        sys.exit(4)


if __name__ == '__main__':
    main()
