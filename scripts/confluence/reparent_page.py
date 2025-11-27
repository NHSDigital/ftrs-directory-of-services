#!/usr/bin/env python3
from __future__ import annotations
import argparse
import base64
import json
import os
import sys
from typing import Dict

import requests


def basic_auth_header(user: str, token: str) -> Dict[str, str]:
    raw = f"{user}:{token}".encode("utf-8")
    return {"Authorization": "Basic " + base64.b64encode(raw).decode("ascii")}


def bearer_auth_header(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def get_version(base_url: str, page_id: str, headers: Dict[str, str]) -> int:
    url = f"{base_url.rstrip('/')}/rest/api/content/{page_id}"
    r = requests.get(url, headers=headers, params={"expand": "version"}, timeout=30)
    r.raise_for_status()
    return int(r.json().get("version", {}).get("number", 1))


def set_parent(base_url: str, page_id: str, parent_id: str, headers: Dict[str, str]) -> None:
    version = get_version(base_url, page_id, headers)
    url = f"{base_url.rstrip('/')}/rest/api/content/{page_id}"
    payload = {
        "id": page_id,
        "type": "page",
        "version": {"number": version + 1},
        "ancestors": [{"id": str(parent_id)}],
        "minorEdit": True,
    }
    r = requests.put(url, headers={**headers, "Content-Type": "application/json"}, data=json.dumps(payload), timeout=60)
    r.raise_for_status()


def main() -> None:
    p = argparse.ArgumentParser(description="Reparent a Confluence page without changing content")
    p.add_argument("page_id", help="Page ID to move")
    p.add_argument("parent_id", help="Target parent page ID")
    p.add_argument("--base-url", default=os.getenv("CONFLUENCE_BASE_URL", ""), required=False)
    p.add_argument("--auth", choices=["basic", "bearer"], default=os.getenv("CONFLUENCE_AUTH", "basic"))
    p.add_argument("--user", default=os.getenv("CONFLUENCE_USER", ""))
    p.add_argument("--token", default=os.getenv("CONFLUENCE_TOKEN", ""))
    args = p.parse_args()

    if not args.base_url or not args.token or (args.auth == "basic" and not args.user):
        print("Missing required auth/base arguments. Set env vars or pass flags.", file=sys.stderr)
        p.print_help(sys.stderr)
        sys.exit(2)

    headers = bearer_auth_header(args.token) if args.auth == "bearer" else basic_auth_header(args.user or "", args.token)

    set_parent(args.base_url, args.page_id, args.parent_id, headers)
    print(f"Reparented page {args.page_id} under parent {args.parent_id}")


if __name__ == "__main__":
    main()
