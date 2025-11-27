#!/usr/bin/env python3
from __future__ import annotations
import argparse
import os
from pathlib import Path
from typing import Dict, List
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "requirements" / "user-stories" / "backlog" / "jira"


def basic_auth_header(user: str, token: str) -> Dict[str, str]:
    import base64
    raw = f"{user}:{token}".encode("utf-8")
    return {"Authorization": "Basic " + base64.b64encode(raw).decode("ascii")}


def bearer_auth_header(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def to_markdown(issue: Dict[str, object]) -> str:
    fields = issue.get("fields", {}) if isinstance(issue, dict) else {}
    if not isinstance(fields, dict):
        fields = {}
    def _get(name: str, default: str = "") -> str:
        v = fields.get(name) if isinstance(fields, dict) else None
        if isinstance(v, dict) and "name" in v:
            return str(v.get("name") or default)
        if v is None:
            return default
        return str(v)

    key = str(issue.get("key", ""))
    summary = _get("summary")
    issuetype = (fields.get("issuetype") or {}).get("name", "") if isinstance(fields, dict) else ""
    status = (fields.get("status") or {}).get("name", "") if isinstance(fields, dict) else ""
    priority = (fields.get("priority") or {}).get("name", "") if isinstance(fields, dict) else ""
    assignee = (fields.get("assignee") or {}).get("displayName", "") if isinstance(fields, dict) else ""
    reporter = (fields.get("reporter") or {}).get("displayName", "") if isinstance(fields, dict) else ""
    labels = ", ".join(fields.get("labels", []) or []) if isinstance(fields, dict) else ""
    components = ", ".join([c.get("name", "") for c in (fields.get("components", []) or [])]) if isinstance(fields, dict) else ""
    created = _get("created")
    updated = _get("updated")

    # Prefer rendered description if available
    desc_html = (issue.get("renderedFields") or {}).get("description") if isinstance(issue, dict) else None
    desc = fields.get("description") if isinstance(fields, dict) else None
    desc_block = ""
    if isinstance(desc_html, str) and desc_html.strip():
        desc_block = "\n".join([
            "## Description (HTML)",
            "",
            "<details>",
            "<summary>Rendered from Jira</summary>",
            desc_html,
            "</details>",
            "",
        ])
    elif isinstance(desc, str) and desc.strip():
        desc_block = "\n".join([
            "## Description",
            "",
            "```",
            desc,
            "```",
            "",
        ])

    lines: List[str] = []
    lines.append(f"# {key} – {summary}")
    lines.append("")
    lines.append("**Metadata**")
    lines.append("")
    lines.append(f"- Key: {key}")
    lines.append(f"- Type: {issuetype}")
    lines.append(f"- Status: {status}")
    lines.append(f"- Priority: {priority}")
    lines.append(f"- Assignee: {assignee}")
    lines.append(f"- Reporter: {reporter}")
    lines.append(f"- Labels: {labels}")
    lines.append(f"- Components: {components}")
    lines.append(f"- Created: {created}")
    lines.append(f"- Updated: {updated}")
    lines.append("")
    if desc_block:
        lines.append(desc_block)
    return "\n".join(lines).rstrip() + "\n"


def ensure_gitignore_entry() -> None:
    gi = ROOT / ".gitignore"
    entry = "requirements/user-stories/backlog/jira/\n"
    try:
        if gi.exists():
            content = gi.read_text(encoding="utf-8")
            if entry not in content:
                gi.write_text(content.rstrip() + "\n\n" + entry, encoding="utf-8")
        else:
            gi.write_text(entry, encoding="utf-8")
    except Exception:
        pass


def main() -> None:
    p = argparse.ArgumentParser(description="Fetch ALL Jira issues from the FTRS project and save as Markdown")
    p.add_argument("--base-url", default=os.getenv("JIRA_BASE_URL", "https://nhsd-jira.digital.nhs.uk"))
    p.add_argument("--auth", choices=["basic", "bearer"], default=os.getenv("JIRA_AUTH", "basic"))
    p.add_argument("--user", default=os.getenv("JIRA_USER", ""))
    p.add_argument("--token", default=os.getenv("JIRA_TOKEN", ""))
    p.add_argument("--output", default=str(OUT_DIR))
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    p.add_argument("--dry-run", action="store_true", help="List keys without writing files")
    args = p.parse_args()

    if not args.token:
        raise SystemExit("Missing --token (or JIRA_TOKEN)")

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    ensure_gitignore_entry()

    headers = bearer_auth_header(args.token) if args.auth == "bearer" else basic_auth_header(args.user or "", args.token)

    # Paginate through all issues in the FTRS project
    start_at = 0
    max_results = 100
    base = args.base_url.rstrip('/')
    keys: List[str] = []
    while True:
        url = f"{base}/rest/api/2/search"
        jql = "project = FTRS ORDER BY created ASC"
        params = {"jql": jql, "startAt": start_at, "maxResults": max_results, "expand": "renderedFields"}
        resp = requests.get(url, headers={**headers, "Accept": "application/json"}, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json() or {}
        issues = data.get("issues", []) or []
        if not issues:
            break
        for issue in issues:
            key = str(issue.get("key", ""))
            if not key:
                continue
            if args.dry_run:
                keys.append(key)
                continue
            target = out_dir / f"{key}.md"
            if target.exists() and not args.overwrite:
                # skip existing
                continue
            md = to_markdown(issue)
            target.write_text(md, encoding="utf-8")
            print(f"Wrote {target}")
        start_at += len(issues)
    if args.dry_run:
        print("Discovered Jira keys:")
        for k in keys:
            print(f"- {k}")
        print(f"Would write to: {out_dir}")


if __name__ == "__main__":
    main()
