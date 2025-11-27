#!/usr/bin/env python3
from __future__ import annotations
import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Optional

import json
import requests

try:
    import yaml  # type: ignore
    YAML_AVAILABLE = True
except ModuleNotFoundError:
    YAML_AVAILABLE = False


ROOT = Path(__file__).resolve().parents[2]
NFRS_ROOT = ROOT / "requirements" / "nfrs"
OUT_DIR = ROOT / "requirements" / "user-stories" / "backlog" / "jira"

RE_JIRA = re.compile(r"\bFTRS-\d+\b")


def find_nfr_yaml_files() -> List[Path]:
    files: List[Path] = []
    if not NFRS_ROOT.exists():
        return files
    for p in NFRS_ROOT.rglob("nfrs.yaml"):
        files.append(p)
    return sorted(files)


def extract_story_keys_from_yaml(path: Path) -> Set[str]:
    keys: Set[str] = set()
    if not YAML_AVAILABLE:
        return keys
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return keys

    def _walk(obj: object) -> None:
        if isinstance(obj, dict):
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for v in obj:
                _walk(v)
        elif isinstance(obj, str):
            for m in RE_JIRA.finditer(obj):
                keys.add(m.group(0))

    _walk(data)
    return keys


def basic_auth_header(user: str, token: str) -> Dict[str, str]:
    # Jira Server/DC supports basic auth with PAT
    import base64
    raw = f"{user}:{token}".encode("utf-8")
    return {"Authorization": "Basic " + base64.b64encode(raw).decode("ascii")}


def bearer_auth_header(token: str) -> Dict[str, str]:
    # Some setups may accept PAT as Bearer
    return {"Authorization": f"Bearer {token}"}


def fetch_issue(base_url: str, key: str, headers: Dict[str, str]) -> Dict[str, object]:
    url = f"{base_url.rstrip('/')}/rest/api/2/issue/{key}"
    # Ask for renderedFields when available; Jira Server supports it for HTML description
    hdrs = {**headers, "Accept": "application/json"}
    resp = requests.get(url, headers=hdrs, params={"expand": "renderedFields"}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise ValueError(f"Unexpected response type for {key}: {type(data)}")
    return data


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

    # Best-effort description: prefer renderedFields.description (HTML), otherwise fields.description (text/wiki)
    desc_html = (issue.get("renderedFields") or {}).get("description") if isinstance(issue, dict) else None
    desc = fields.get("description") if isinstance(fields, dict) else None
    desc_block = ""
    if isinstance(desc_html, str) and desc_html.strip():
        # Keep HTML inside <details> so it renders reasonably in Markdown viewers
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

    lines = []
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
    # Ensure new backlog path is ignored; keep backwards compatibility if older path exists
    entries = [
        "requirements/user-stories/backlog/jira/\n",
    ]
    try:
        if gi.exists():
            content = gi.read_text(encoding="utf-8")
            updated = content.rstrip()
            for e in entries:
                if e not in updated:
                    updated = updated + "\n\n" + e
            if updated != content:
                gi.write_text(updated, encoding="utf-8")
        else:
            gi.write_text("".join(entries), encoding="utf-8")
    except Exception:
        # Non-fatal if .gitignore cannot be updated
        pass


def main() -> None:
    p = argparse.ArgumentParser(description="Fetch Jira stories referenced in NFR YAML files and save as Markdown")
    p.add_argument("--base-url", default=os.getenv("JIRA_BASE_URL", "https://nhsd-jira.digital.nhs.uk"))
    p.add_argument("--auth", choices=["basic", "bearer"], default=os.getenv("JIRA_AUTH", "basic"))
    p.add_argument("--user", default=os.getenv("JIRA_USER", ""))
    p.add_argument("--token", default=os.getenv("JIRA_TOKEN", ""))
    p.add_argument("--output", default=str(OUT_DIR))
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    p.add_argument("--dry-run", action="store_true", help="Report actions without network calls or writes")
    p.add_argument("--keys", nargs="*", help="Explicit FTRS- keys to fetch instead of scanning YAML")
    args = p.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    ensure_gitignore_entry()

    keys: Set[str] = set()
    if args.keys:
        for k in args.keys:
            if RE_JIRA.fullmatch(k):
                keys.add(k)
    else:
        for f in find_nfr_yaml_files():
            keys |= extract_story_keys_from_yaml(f)

    if args.dry_run:
        print("Discovered Jira keys:")
        for k in sorted(keys):
            print(f"- {k}")
        print(f"Would write to: {out_dir}")
        return

    if not args.token:
        raise SystemExit("Missing --token (or JIRA_TOKEN)")

    headers = bearer_auth_header(args.token) if args.auth == "bearer" else basic_auth_header(args.user or "", args.token)
    base = args.base_url

    for key in sorted(keys):
        target = out_dir / f"{key}.md"
        if target.exists() and not args.overwrite:
            print(f"Skip existing: {target}")
            continue
        try:
            issue = fetch_issue(base, key, headers)
            md = to_markdown(issue)
            target.write_text(md, encoding="utf-8")
            print(f"Wrote {target}")
        except requests.HTTPError as e:
            status = e.response.status_code if hasattr(e, "response") and e.response is not None else "unknown"
            body = None
            try:
                body = e.response.text if e.response is not None else None
            except Exception:
                body = None
            print(f"Failed {key}: HTTP {status}")
            if body:
                print(f"  Response: {body[:200]}...")
        except Exception as e:
            print(f"Failed {key}: {e}")


if __name__ == "__main__":
    main()
