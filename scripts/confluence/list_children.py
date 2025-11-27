#!/usr/bin/env python3
from __future__ import annotations
import argparse
import base64
import os
from typing import Dict

import requests


def basic_auth_header(user: str, token: str) -> Dict[str, str]:
    raw = f"{user}:{token}".encode("utf-8")
    return {"Authorization": "Basic " + base64.b64encode(raw).decode("ascii")}


def bearer_auth_header(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def main() -> None:
    p = argparse.ArgumentParser(description="List child page titles under a Confluence parent")
    p.add_argument("parent_id", help="Parent page ID")
    p.add_argument("--base-url", default=os.getenv("CONFLUENCE_BASE_URL", ""))
    p.add_argument("--auth", choices=["basic", "bearer"], default=os.getenv("CONFLUENCE_AUTH", "basic"))
    p.add_argument("--user", default=os.getenv("CONFLUENCE_USER", ""))
    p.add_argument("--token", default=os.getenv("CONFLUENCE_TOKEN", ""))
    args = p.parse_args()

    headers = bearer_auth_header(args.token) if args.auth == "bearer" else basic_auth_header(args.user or "", args.token)
    url = f"{args.base_url.rstrip('/')}/rest/api/content/{args.parent_id}/child/page"
    r = requests.get(url, headers=headers, params={"limit": 500}, timeout=30)
    r.raise_for_status()
    for item in r.json().get("results", []):
        print(f"{item.get('id')}: {item.get('title')}")


if __name__ == "__main__":
    main()
