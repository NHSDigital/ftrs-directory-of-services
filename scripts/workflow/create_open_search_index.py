#!/usr/bin/env python3
"""
    Create an OpenSearch Serverless index by signing a PUT request with SigV4
    Uses boto3/botocore to resolve collections (if a collection name is provided) and to sign the HTTP request.
    Reads configuration from environment variables (so it fits the GitHub Action composite step):
    OPEN_SEARCH_DOMAIN, INDEX, WORKSPACE, AWS_REGION, AWS_SERVICE

    Exits with non-zero code on error and prints helpful debug logs to stderr.
"""
import os
import sys
import json
import logging
from typing import Optional

import boto3
import botocore.session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("create_open_search_index")


def env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(name, default)


def fail(msg: str, code: int = 1) -> None:
    log.error(msg)
    sys.exit(code)


def resolve_serverless_collection(name: str, region: Optional[str]) -> Optional[str]:
    """Return endpoint URL (with https://) for a serverless collection by name, or None if not found."""
    try:
        kwargs = {}
        if region:
            kwargs["region_name"] = region
        client = boto3.client("opensearchserverless", **kwargs)

        # find collection id
        resp = client.list_collections()
        for cs in resp.get("collectionSummaries", []):
            if cs.get("name") == name:
                cid = cs.get("id")
                break
        else:
            return None

        resp2 = client.batch_get_collection(ids=[cid])
        # Log collection details for debugging (redact tokens if present)
        try:
            log.info("batch_get_collection response: {}".format(json.dumps(resp2, default=str)))
        except Exception:
            log.debug("Could not stringify collection details", exc_info=True)
        details = resp2.get("collectionDetails", [])
        if not details:
            return None
        # collectionEndpoint or endpoint
        ep = details[0].get("collectionEndpoint") or details[0].get("endpoint")
        return ep
    except Exception:
        log.debug("Failed to resolve collection via boto3", exc_info=True)
        return None


def sign_and_put(url: str, payload: str, region: Optional[str], service: str = "aoss") -> requests.Response:
    """Sign the HTTP request using botocore SigV4 and send via requests."""
    session = botocore.session.get_session()
    creds = session.get_credentials()
    if creds is None:
        raise RuntimeError("No AWS credentials available in the environment")
    frozen = creds.get_frozen_credentials()

    aws_request = AWSRequest(method="PUT", url=url, data=payload, headers={"Content-Type": "application/json"})
    SigV4Auth(frozen, service, region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "").add_auth(aws_request)

    # Log redacted signing headers for debugging (do not print secret keys)
    try:
        hdrs = dict(aws_request.headers)
        auth = hdrs.get('Authorization') or hdrs.get('authorization')
        if auth:
            # Redact the Signature value portion
            redacted_auth = auth
            if 'Signature=' in auth:
                parts = auth.split('Signature=')
                redacted_auth = parts[0] + 'Signature=<redacted>'
            log.info('Signed Authorization header: {}'.format(redacted_auth))
        if 'x-amz-security-token' in (k.lower() for k in hdrs.keys()):
            log.info('Signed request includes a session token (x-amz-security-token present)')
        if 'x-amz-date' in (k.lower() for k in hdrs.keys()):
            log.info('Signed request X-Amz-Date: {}'.format(hdrs.get('X-Amz-Date') or hdrs.get('x-amz-date')))
    except Exception:
        log.debug('Could not introspect signed headers', exc_info=True)

    prepared = requests.Request(method=aws_request.method, url=aws_request.url, data=aws_request.body, headers=dict(aws_request.headers)).prepare()
    s = requests.Session()
    resp = s.send(prepared, timeout=30)

    # Log response headers (redact any sensitive headers)
    try:
        hdrs = dict(resp.headers)
        # redact potentially sensitive headers
        redact_keys = {k.lower() for k in ['authorization', 'www-authenticate', 'set-cookie']}
        hdrs_safe = {k: (v if k.lower() not in redact_keys else '<redacted>') for k, v in hdrs.items()}
        log.info('Response headers: {}'.format(json.dumps(hdrs_safe, default=str)))
    except Exception:
        log.debug('Could not log response headers', exc_info=True)

    # If error, try to parse AOSS JSON and log useful fields (request-id, error.reason)
    try:
        text = resp.text
        if text:
            try:
                body = resp.json()
            except Exception:
                body = None
            if body and isinstance(body, dict):
                rid = body.get('request-id') or body.get('request_id') or body.get('requestId')
                err_obj = body.get('error') if 'error' in body else None
                if rid:
                    log.info('AOSS request-id: {}'.format(rid))
                if err_obj and isinstance(err_obj, dict):
                    reason = err_obj.get('reason') or err_obj.get('message')
                    typ = err_obj.get('type')
                    log.info('AOSS error: type={} reason={}'.format(typ, reason))
            else:
                # not JSON, log first 2k of body for context
                if resp.status_code >= 400:
                    log.info('Response body (first 2k): {}'.format(text[:2048]))
    except Exception:
        log.debug('Could not parse response body JSON', exc_info=True)

    if resp.status_code == 403:
        log.info('HTTP 403 received; ensure collection access policy includes the IAM role ARN and that Resource covers the target index')

    return resp


def inspect_iam_role_permissions(role_arn: str) -> None:
    """Log attached and inline policies for the given IAM role and whether they mention aoss/opensearch actions."""
    try:
        iam = boto3.client('iam')
        role_name = role_arn.split('/')[-1]
        log.info('Inspecting IAM role: {}'.format(role_arn))

        attached = iam.list_attached_role_policies(RoleName=role_name).get('AttachedPolicies', [])
        log.info('Attached managed policies: {}'.format([p.get('PolicyName') for p in attached]))
        for p in attached:
            try:
                pol = iam.get_policy(PolicyArn=p.get('PolicyArn'))
                ver = iam.get_policy_version(PolicyArn=p.get('PolicyArn'), VersionId=pol['Policy']['DefaultVersionId'])
                doc = ver['PolicyVersion']['Document']
                s = json.dumps(doc)
                found = any(k in s for k in ['aoss', 'opensearch', 'opensearchserverless', 'osis'])
                log.info('Managed policy {} mentions aoss/opensearch keywords: {}'.format(p.get('PolicyName'), found))
            except Exception:
                log.debug('Could not retrieve managed policy {}'.format(p.get('PolicyArn')), exc_info=True)

        inline = iam.list_role_policies(RoleName=role_name).get('PolicyNames', [])
        log.info('Inline policies: {}'.format(inline))
        for name in inline:
            try:
                doc = iam.get_role_policy(RoleName=role_name, PolicyName=name)['PolicyDocument']
                s = json.dumps(doc)
                found = any(k in s for k in ['aoss', 'opensearch', 'opensearchserverless', 'osis'])
                log.info('Inline policy {} mentions aoss/opensearch keywords: {}'.format(name, found))
            except Exception:
                log.debug('Could not retrieve inline policy {}'.format(name), exc_info=True)
    except Exception:
        log.debug('IAM role inspection failed', exc_info=True)


def inspect_opensearch_security_policies(collection_name: str, region: Optional[str]) -> None:
    """Attempt to list security/access policies for OpenSearch Serverless and log any that mention principals or resources of interest."""
    try:
        kwargs = {}
        if region:
            kwargs['region_name'] = region
        osc = boto3.client('opensearchserverless', **kwargs)

        # Try a few API calls that different SDK versions might expose
        tried = []
        for method_name in ('list_security_policies', 'list_access_policies', 'list_policies', 'list_security_configs'):
            if hasattr(osc, method_name):
                try:
                    tried.append(method_name)
                    fn = getattr(osc, method_name)
                    res = fn()
                    log.info('opensearchserverless.%s result keys: %s' % (method_name, list(res.keys())))
                    try:
                        log.info('%s content (truncated): %s' % (method_name, json.dumps(res, default=str)[:4000]))
                    except Exception:
                        pass
                except Exception:
                    log.debug('Call %s failed' % method_name, exc_info=True)

        # As a fallback, try to fetch policies by known ids/names if available via batch_get (no-op here)
        if not tried:
            log.debug('No list_* security policy methods available on opensearchserverless client')
    except Exception:
        log.debug('OpenSearch security policy inspection failed', exc_info=True)


def main() -> int:
    OPEN_SEARCH_DOMAIN = env("OPEN_SEARCH_DOMAIN")
    INDEX = env("INDEX")
    WORKSPACE = env("WORKSPACE") or ""
    AWS_REGION = env("AWS_REGION") or env("AWS_DEFAULT_REGION")
    AWS_SERVICE = env("AWS_SERVICE") or "aoss"

    if not OPEN_SEARCH_DOMAIN:
        fail("OPEN_SEARCH_DOMAIN not set", 2)
    if not INDEX:
        fail("INDEX not set", 2)

    log.info("AWS_REGION: {}".format(AWS_REGION or '<unset>'))
    if env("AWS_DEFAULT_REGION"):
        log.info("AWS_DEFAULT_REGION: {}".format(env('AWS_DEFAULT_REGION')))

    # Print STS caller identity for debugging
    try:
        sts_kwargs = {}
        if AWS_REGION:
            sts_kwargs["region_name"] = AWS_REGION
        sts = boto3.client("sts", **sts_kwargs)
        who = sts.get_caller_identity()
        caller_arn = who.get('Arn')
        log.info("Caller ARN: {}".format(caller_arn))
        log.info("AWS Account: {}".format(who.get('Account')))

        role_arn = None
        if caller_arn and ':assumed-role/' in caller_arn:
            try:
                parts = caller_arn.split(':', 5)
                # parts[4] is account id, parts[5] is 'assumed-role/RoleName/session'
                account_id = parts[4]
                assumed_part = parts[5]
                # extract role name between assumed-role/ and next '/'
                role_name = assumed_part.split('/', 2)[1]
                role_arn = 'arn:aws:iam::{}:role/{}'.format(account_id, role_name)
                log.info("Derived role ARN for collection policy: {}".format(role_arn))

                # Run IAM simulation for several aoss actions to help debug 403
                try:
                    iam = boto3.client('iam')
                    actions = [
                        'aoss:CreateIndex',
                        'aoss:DescribeIndex',
                        'aoss:UpdateIndex',
                        'aoss:DeleteIndex',
                        'aoss:ReadDocument',
                        'aoss:WriteDocument',
                        'aoss:BatchGetCollection',
                        'aoss:ListCollections'
                    ]
                    sim = iam.simulate_principal_policy(PolicySourceArn=role_arn, ActionNames=actions)
                    for res in sim.get('EvaluationResults', []):
                        action_name = res.get('EvalActionName')
                        decision = res.get('EvalDecision')
                        log.info('IAM simulation for {} => {}'.format(action_name, decision))
                except Exception:
                    log.debug('IAM simulation failed', exc_info=True)

                # Inspect attached and inline IAM policies for the derived role
                inspect_iam_role_permissions(role_arn)

                # Attempt to inspect OpenSearch Serverless security/access policies (best-effort)
                try:
                    inspect_opensearch_security_policies(OPEN_SEARCH_DOMAIN, AWS_REGION)
                except Exception:
                    log.debug('Failed to inspect OpenSearch security policies', exc_info=True)

            except Exception:
                log.debug("Failed to derive role ARN from caller ARN", exc_info=True)
    except Exception:
        log.warning("Could not call STS to get caller identity", exc_info=True)

    # Resolve serverless collection to endpoint if needed
    if "." not in OPEN_SEARCH_DOMAIN:
        log.info("Resolving serverless collection '{}' via AWS API".format(OPEN_SEARCH_DOMAIN))
        resolved = resolve_serverless_collection(OPEN_SEARCH_DOMAIN, AWS_REGION)
        if resolved:
            OPEN_SEARCH_DOMAIN = resolved
            log.info("AWS lookup found endpoint: {}".format(OPEN_SEARCH_DOMAIN))
        else:
            fail("Could not resolve serverless collection '{}'".format(OPEN_SEARCH_DOMAIN), 3)

    # Normalize domain
    if OPEN_SEARCH_DOMAIN.startswith("https://"):
        OPEN_SEARCH_DOMAIN = OPEN_SEARCH_DOMAIN[len("https://"):]

    # Special-case: do not append workspace suffix for certain index names
    # (e.g., 'organisation' is managed as a single index across workspaces)
    if INDEX == "organisation":
        WORKSPACE = ""
    else:
        if WORKSPACE and not WORKSPACE.startswith("-"):
            WORKSPACE = "-{}".format(WORKSPACE)

    FINAL_INDEX = "{}{}".format(INDEX, WORKSPACE)

    payload = {
        "mappings": {
            "properties": {
                "primary_key": {"type": "keyword"},
                "sgsd": {
                    "type": "nested",
                    "properties": {"sg": {"type": "integer"}, "sd": {"type": "integer"}}
                },
            }
        }
    }

    url = "https://{}/{}".format(OPEN_SEARCH_DOMAIN, FINAL_INDEX)

    try:
        body = json.dumps(payload)
        log.info("Creating index using URL: {}".format(url))
        resp = sign_and_put(url, body, AWS_REGION, AWS_SERVICE)
        log.info("Response: {} {}".format(resp.status_code, resp.reason))
        try:
            log.info("Response body: {}".format(resp.text))
        except Exception:
            log.debug("Could not read response body", exc_info=True)

        if resp.status_code in (200, 201):
            log.info("Index {} created or already exists".format(FINAL_INDEX))
            return 0
        else:
            log.error("Index creation failed with status {}".format(resp.status_code))
            return 4
    except Exception:
        log.error("Exception during index creation", exc_info=True)
        return 5


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
