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
    region = parsed.netloc.split('.')[-4] if parsed.netloc else ''

    request = AWSRequest(method='PUT', url=url, data=payload, headers={'Content-Type': 'application/json'})
    SigV4Auth(frozen, service, region).add_auth(request)
    prepared = request.prepare()

    # Transfer headers to requests format
    headers = dict(prepared.headers.items())

    log.info('Sending signed PUT to %s', url)
    resp = requests.put(url, data=payload, headers=headers, timeout=30)
    log.info('Response: %s %s', resp.status_code, resp.text)
    if resp.status_code >= 400:
        sys.exit(4)


if __name__ == '__main__':
    main()

