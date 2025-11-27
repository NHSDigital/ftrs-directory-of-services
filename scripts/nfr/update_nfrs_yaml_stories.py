#!/usr/bin/env python3
"""Update requirements/nfrs/*/nfrs.yaml stories from user story backlog.

- Scans requirements/user-stories/backlog/*.md for front matter:
    - story_id
    - nfr_refs: [CODE,...]
- Builds code -> [story_ids]
- For each domain nfrs.yaml, set nfrs[i].stories to sorted unique story_ids for that code.
"""
from __future__ import annotations
from pathlib import Path
import sys
import re

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    sys.stderr.write("PyYAML is required. Install with: python3 -m pip install pyyaml\n")
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
BACKLOG = ROOT / "requirements" / "user-stories" / "backlog"
DOMAINS = ROOT / "requirements" / "nfrs"

FM_START = re.compile(r"^---\s*$")
FM_END = re.compile(r"^---\s*$")
RE_KEYVAL = re.compile(r"^([a-zA-Z_]+):\s*(.*)\s*$")


def parse_front_matter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or not FM_START.match(lines[0]):
        return {}
    i = 1
    data: dict = {}
    while i < len(lines) and not FM_END.match(lines[i]):
        m = RE_KEYVAL.match(lines[i])
        if m:
            key, val = m.groups()
            data[key.strip()] = val.strip()
        i += 1
    # parse nfr_refs list which may be like: [CODE, CODE]
    raw = data.get('nfr_refs', '')
    codes: list[str] = []
    if raw.startswith('[') and raw.endswith(']'):
        inner = raw[1:-1]
        for part in inner.split(','):
            part = part.strip().strip("'\"")
            if part:
                codes.append(part)
    elif raw:
        codes = [c.strip() for c in raw.split(',') if c.strip()]
    data['nfr_refs'] = codes
    return data


def collect_story_map() -> dict[str, list[str]]:
    code_to_stories: dict[str, list[str]] = {}
    for md in BACKLOG.glob('STORY-*-*.md'):
        text = md.read_text(encoding='utf-8')
        fm = parse_front_matter(text)
        sid = fm.get('story_id')
        for code in fm.get('nfr_refs', []) or []:
            bucket = code_to_stories.setdefault(code, [])
            if sid and sid not in bucket:
                bucket.append(sid)
    # sort story ids per code
    for code, arr in code_to_stories.items():
        arr.sort()
    return code_to_stories


def update_domain_yaml(path: Path, code_map: dict[str, list[str]]) -> bool:
    try:
        data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    except Exception as e:
        sys.stderr.write(f"Failed to read {path}: {e}\n")
        return False
    nfrs = data.get('nfrs') or []
    changed = False
    for n in nfrs:
        code = n.get('code')
        if not code:
            continue
        stories = code_map.get(code, [])
        if stories and (n.get('stories') or []) != stories:
            n['stories'] = stories
            changed = True
    if changed:
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding='utf-8')
        print(f"Updated stories in {path}")
    return changed


def main() -> int:
    code_map = collect_story_map()
    changed = 0
    for yml in sorted(DOMAINS.glob('*/nfrs.yaml')):
        if update_domain_yaml(yml, code_map):
            changed += 1
    print(f"Updated {changed} domain files")
    return 0

if __name__ == '__main__':
    sys.exit(main())
