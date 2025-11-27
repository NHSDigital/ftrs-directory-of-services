#!/usr/bin/env python3
"""Validate that all nfr_refs in user story front matter exist in the canonical registry (index.yaml).
Exit codes:
    0 = success
    1 = unknown NFR code(s) referenced
    2 = parsing error
Usage: python scripts/nfr/validate_nfr_refs.py
"""
from __future__ import annotations
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "requirements" / "nfrs" / "cross-references" / "index.yaml"
STORIES_DIR = ROOT / "requirements" / "user-stories" / "backlog"

FRONT_MATTER_RE = re.compile(r"^---$")
CODE_LINE_RE = re.compile(r"^\s*-\s*([A-Z]+-[0-9]{3})\s*$")
NFR_CODE_RE = re.compile(r"^\s*- code: (\S+)\s*$")


def load_registry_codes() -> set[str]:
    codes: set[str] = set()
    if not REGISTRY.exists():
        print(f"Registry file not found: {REGISTRY}", file=sys.stderr)
        return codes
    for line in REGISTRY.read_text().splitlines():
        m = NFR_CODE_RE.match(line)
        if m:
            codes.add(m.group(1).strip())
    return codes


def parse_front_matter(text: str) -> dict[str, list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return {}
    # find end of front matter
    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_index = i
            break
    if end_index is None:
        raise ValueError('Front matter not closed with ---')
    fm_lines = lines[1:end_index]
    nfr_refs: list[str] = []
    in_refs = False
    for ln in fm_lines:
        if ln.strip().startswith('nfr_refs:'):
            in_refs = True
            continue
        if in_refs:
            if ln.strip().startswith('-'):
                m = CODE_LINE_RE.match(ln)
                if m:
                    nfr_refs.append(m.group(1))
                else:
                    # Stop if line format changes (e.g. next field)
                    if not ln.strip():
                        continue
            else:
                # End of nfr_refs list
                in_refs = False
    return {'nfr_refs': nfr_refs}


def collect_story_refs() -> dict[pathlib.Path, list[str]]:
    mapping: dict[pathlib.Path, list[str]] = {}
    if not STORIES_DIR.exists():
        return mapping
    for path in STORIES_DIR.glob('STORY-*.md'):
        try:
            fm = parse_front_matter(path.read_text())
            refs = fm.get('nfr_refs', [])
            mapping[path] = refs
        except Exception as e:
            print(f"Error parsing {path}: {e}", file=sys.stderr)
            sys.exit(2)
    return mapping


def validate():
    registry = load_registry_codes()
    if not registry:
        print('No registry codes loaded.', file=sys.stderr)
        sys.exit(2)
    story_refs = collect_story_refs()
    unknown: dict[pathlib.Path, list[str]] = {}
    for path, refs in story_refs.items():
        missing = [c for c in refs if c not in registry]
        if missing:
            unknown[path] = missing
    if unknown:
        print('Unknown NFR codes found:')
        for path, codes in unknown.items():
            print(f"  {path.name}: {', '.join(codes)}")
        sys.exit(1)
    print(f"Validation passed. {len(story_refs)} stories checked; {len(registry)} registry codes available.")


if __name__ == '__main__':
    validate()
