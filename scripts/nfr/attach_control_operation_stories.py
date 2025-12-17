#!/usr/bin/env python3
"""Attach story IDs to controls and operations in domain nfrs.yaml files.

- Scans requirements/user-stories/backlog/*.md for front matter:
    - story_id: STORY-XXX-###
    - nfr_refs: [CODE,...]
- Derives a slug from filename after the story id, e.g.:
    STORY-SEC-008-port-scan-diagnostic-only.md -> control_id 'port-scan-diagnostic-only'
    FTRS-887-dos-search.md -> operation_id 'dos-search'

For each domain nfrs.yaml:
- If NFR code is in a story's nfr_refs, and a control_id matches the slug,
    append the story_id to that control's stories list (deduped).
- For performance domain, if any operation_id matches the slug, append story_id
    to that operation's stories list (deduped).

Idempotent and safe: preserves existing entries, only adds missing story_ids.
"""
from __future__ import annotations
from pathlib import Path
import sys
import re
from typing import Dict, List

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    sys.stderr.write("PyYAML is required. Install with: python3 -m pip install pyyaml\n")
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
BACKLOG_DIR = ROOT / "requirements/user-stories/backlog"
DOMAINS_DIR = ROOT / "requirements/nfrs"

RE_STORY_FILE = re.compile(r"^(STORY|FTRS)-([A-Z]+)-(\d+)-(.*)\.md$")


def parse_front_matter(text: str) -> Dict[str, List[str] | str]:
    """Minimal front matter parser for 'story_id' and 'nfr_refs'."""
    lines = text.splitlines()
    data: Dict[str, List[str] | str] = {}
    if not lines or not lines[0].strip().startswith("---"):
        return data
    i = 1
    while i < len(lines):
        ln = lines[i].strip()
        if ln.startswith("---"):
            break
        if ln.startswith("story_id:"):
            data["story_id"] = ln.split(":", 1)[1].strip()
        elif ln.startswith("nfr_refs:"):
            # collect subsequent '- CODE' items or inline list
            refs: List[str] = []
            if ": [" in ln:
                inside = ln.split("[", 1)[1].rsplit("]", 1)[0]
                refs = [t.strip() for t in inside.split(",") if t.strip()]
            else:
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith("-"):
                    refs.append(lines[j].strip().lstrip("-").strip())
                    j += 1
            data["nfr_refs"] = refs
        i += 1
    return data


def derive_slug_from_filename(fname: str) -> str | None:
    m = RE_STORY_FILE.match(fname)
    if not m:
        return None
    trailing = m.group(4)
    return trailing.strip() if trailing else None


def load_yaml(path: Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        sys.stderr.write(f"Failed to read {path}: {e}\n")
        return {}


def save_yaml(path: Path, data: dict) -> None:
    try:
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"Failed to write {path}: {e}\n")


def main() -> int:
    # Collect story mappings: list of (story_id, nfr_refs, slug)
    stories: List[Dict[str, object]] = []
    for md in sorted(BACKLOG_DIR.glob("*.md")):
        slug = derive_slug_from_filename(md.name)
        if not slug:
            continue
        fm = parse_front_matter(md.read_text(encoding="utf-8"))
        story_id = fm.get("story_id")  # type: ignore
        nfr_refs = fm.get("nfr_refs") or []  # type: ignore
        if not story_id:
            continue
        stories.append({"story_id": story_id, "nfr_refs": nfr_refs, "slug": slug})

    # Update domain YAML files
    updates = 0
    for yml in sorted(DOMAINS_DIR.glob("*/nfrs.yaml")):
        data = load_yaml(yml)
        domain = yml.parent.name
        changed = False
        for nfr in data.get("nfrs", []) or []:
            code = nfr.get("code")
            # Attach to controls when slug matches control_id and nfr code is referenced
            ctrls = nfr.get("controls", []) or []
            for ctrl in ctrls:
                cid = ctrl.get("control_id") or ""
                if not cid:
                    continue
                for s in stories:
                    refs = s["nfr_refs"]  # type: ignore
                    slug = s["slug"]  # type: ignore
                    if isinstance(refs, list) and code in refs and isinstance(slug, str) and slug == cid:
                        ctrl.setdefault("stories", [])
                        if s["story_id"] not in ctrl["stories"]:  # type: ignore
                            ctrl["stories"].append(s["story_id"])  # type: ignore
                            changed = True
            # Performance operations mapping by operation_id
            if domain.lower() == "performance":
                ops = nfr.get("operations", []) or []
                for op in ops:
                    oid = op.get("operation_id") or ""
                    if not oid:
                        continue
                    for s in stories:
                        refs = s["nfr_refs"]  # type: ignore
                        slug = s["slug"]  # type: ignore
                        if isinstance(refs, list) and code in refs and isinstance(slug, str) and slug == oid:
                            op.setdefault("stories", [])
                            if s["story_id"] not in op["stories"]:  # type: ignore
                                op["stories"].append(s["story_id"])  # type: ignore
                                changed = True
        if changed:
            save_yaml(yml, data)
            updates += 1
            print(f"Updated {yml}")
    print(f"Control/operation story attachment completed. Domains updated: {updates}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
