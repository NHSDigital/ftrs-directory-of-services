#!/usr/bin/env python3
from __future__ import annotations
import argparse
import os
from pathlib import Path
from typing import Dict, List
import re
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "requirements" / "user-stories" / "backlog" / "jira"


def basic_auth_header(user: str, token: str) -> Dict[str, str]:
    import base64
    raw = f"{user}:{token}".encode("utf-8")
    return {"Authorization": "Basic " + base64.b64encode(raw).decode("ascii")}


def bearer_auth_header(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def fetch_issue(base_url: str, key: str, headers: Dict[str, str]) -> Dict[str, object]:
    url = f"{base_url.rstrip('/')}/rest/api/2/issue/{key}"
    resp = requests.get(url, headers={**headers, "Accept": "application/json"}, params={"expand":"renderedFields"}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise ValueError(f"Unexpected response type for {key}: {type(data)}")
    return data


def issues_in_epic(base_url: str, headers: Dict[str, str], epic_key: str) -> List[Dict[str, object]]:
    # Prefer Agile API if available
    try:
        url = f"{base_url.rstrip('/')}/rest/agile/1.0/epic/{epic_key}/issue"
        resp = requests.get(url, headers={**headers, "Accept": "application/json"}, params={"maxResults": 1000}, timeout=30)
        if resp.status_code == 200:
            data = resp.json() or {}
            return list(data.get("issues", []) or [])
    except Exception:
        pass
    # Fallback: JQL using Epic Link
    url = f"{base_url.rstrip('/')}/rest/api/2/search"
    params = {"jql": f'"Epic Link" = {epic_key}', "maxResults": 1000}
    resp = requests.get(url, headers={**headers, "Accept": "application/json"}, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json() or {}
    return list(data.get("issues", []) or [])


def render_issues_section(issues: List[Dict[str, object]]) -> List[str]:
    lines: List[str] = []
    lines.append("## Issues in this Epic")
    lines.append("")
    if not issues:
        lines.append("(none)")
        lines.append("")
        return lines
    for it in issues:
        if not isinstance(it, dict):
            continue
        key = str(it.get("key", ""))
        fields = it.get("fields", {}) if isinstance(it.get("fields", {}), dict) else {}
        summary = str((fields.get("summary") or "").strip())
        issuetype = str(((fields.get("issuetype") or {}).get("name") or ""))
        status = str(((fields.get("status") or {}).get("name") or ""))
        lines.append(f"- [{key}](https://nhsd-jira.digital.nhs.uk/browse/{key}) – {summary} (Type: {issuetype}, Status: {status})")
    lines.append("")
    return lines


def insert_or_replace_section(md: str, section_lines: List[str]) -> str:
    # Replace existing "## Issues in this Epic" section if present, else append at end
    pattern = re.compile(r"^## Issues in this Epic\n(?:.*\n)*?(?=(^## |\Z))", re.MULTILINE)
    new_block = "\n".join(section_lines)
    if pattern.search(md):
        return pattern.sub(new_block + "\n", md)
    # Insert after Metadata section if present
    meta_pat = re.compile(r"^\*\*Metadata\*\*\n", re.MULTILINE)
    m = meta_pat.search(md)
    if m:
        # find end of metadata list (blank line after bullet list)
        end_idx = md.find("\n\n", m.end())
        if end_idx != -1:
            return md[:end_idx+2] + new_block + "\n" + md[end_idx+2:]
    # Else append
    if not md.endswith("\n"):
        md += "\n"
    return md + "\n" + new_block + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description="Annotate an epic's Markdown with a list of child issues")
    p.add_argument("--base-url", default=os.getenv("JIRA_BASE_URL", "https://nhsd-jira.digital.nhs.uk"))
    p.add_argument("--auth", choices=["basic", "bearer"], default=os.getenv("JIRA_AUTH", "basic"))
    p.add_argument("--user", default=os.getenv("JIRA_USER", ""))
    p.add_argument("--token", default=os.getenv("JIRA_TOKEN", ""))
    p.add_argument("--key", required=True, help="Epic key, e.g. FTRS-1365")
    p.add_argument("--output", help="Explicit path to the epic Markdown; defaults to jira/<KEY>.md")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    epic_key = args.key
    target = Path(args.output) if args.output else (OUT_DIR / f"{epic_key}.md")

    if not args.token:
        raise SystemExit("Missing --token (or JIRA_TOKEN)")
    headers = bearer_auth_header(args.token) if args.auth == "bearer" else basic_auth_header(args.user or "", args.token)
    base = args.base_url

    issues = issues_in_epic(base, headers, epic_key)
    section = render_issues_section(issues)

    # Ensure epic file exists: if missing, fetch epic and write baseline content
    if not target.exists():
        epic = fetch_issue(base, epic_key, headers)
        summary = str(((epic.get("fields") or {}).get("summary") or ""))
        md = f"# {epic_key} – {summary}\n\n**Metadata**\n\n- Key: {epic_key}\n\n"
    else:
        md = target.read_text(encoding="utf-8")

    updated = insert_or_replace_section(md, section)
    if args.dry_run:
        print(f"Would update {target}")
        print("--- New Section Preview ---")
        print("\n".join(section))
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(updated, encoding="utf-8")
    print(f"Updated {target} with {len(issues)} issues from epic {epic_key}")


if __name__ == "__main__":
    main()
