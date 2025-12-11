#!/usr/bin/env python3
"""Validate service specs and user story markdown artifacts.

Checks:
- Story files in requirements/user-stories/backlog/ have required front matter keys.
- Acceptance Criteria section has ≥3 numbered items.
- nfr_refs codes appear in the matrix (if matrix file exists).
- Service spec template copies include mandatory section headers.

Exit codes:
0 = all good
1 = validation errors found
"""
import re
import sys
import yaml
from pathlib import Path

RE_FRONT_MATTER = re.compile(r'^---\n(.*?)\n---', re.DOTALL)
RE_AC_ITEM = re.compile(r'^\s*\d+\.\s+.+')
RE_STORY_FILE = re.compile(r'STORY-\d+.*\.md$')
RE_NFR_CODE = re.compile(r'[A-Z]{3,5}-\d{3}')

REQUIRED_STORY_KEYS = {"story_id","title","role","goal","value","nfr_refs","status"}
MANDATORY_SPEC_SECTIONS = [
    '## 1. Overview','## 2. Scope','## 3. Domain Context','## 4. Functional Flows',
    '## 5. Data Model','## 6. Interfaces / Endpoints','## 7. Non-Functional Requirements Mapping'
]

MATRIX_PATH = Path('requirements/nfrs/cross-references/nfr-matrix.md')

# Collect known NFR codes from matrix (simple table scan)
def load_matrix_codes():
    if not MATRIX_PATH.exists():
        return set()
    codes = set()
    for line in MATRIX_PATH.read_text().splitlines():
        for match in RE_NFR_CODE.findall(line):
            codes.add(match)
    return codes

KNOWN_CODES = load_matrix_codes()
errors = []

# Validate stories
story_dir = Path('requirements/user-stories/backlog')
for path in sorted(story_dir.glob('STORY-*')):
    if path.is_dir():
        continue
    if not RE_STORY_FILE.search(path.name):
        continue
    text = path.read_text()
    fm_match = RE_FRONT_MATTER.search(text)
    if not fm_match:
        errors.append(f"Missing front matter: {path}")
        continue
    try:
        front = yaml.safe_load(fm_match.group(1)) or {}
    except yaml.YAMLError as e:
        errors.append(f"YAML error in {path}: {e}")
        continue
    missing = REQUIRED_STORY_KEYS - set(front.keys())
    if missing:
        errors.append(f"Missing keys {missing} in {path}")
    # nfr_refs validation
    nfr_refs = front.get('nfr_refs', []) or []
    unknown = [c for c in nfr_refs if KNOWN_CODES and c not in KNOWN_CODES]
    if unknown:
        errors.append(f"Unknown nfr_refs {unknown} in {path}")
    # Acceptance criteria count
    ac_section = re.split(r'## Acceptance Criteria', text, flags=re.IGNORECASE)
    if len(ac_section) < 2:
        errors.append(f"No Acceptance Criteria section in {path}")
    else:
        after = ac_section[1]
        count = sum(1 for l in after.splitlines() if RE_AC_ITEM.match(l))
        if count < 3:
            errors.append(f"Fewer than 3 acceptance criteria ({count}) in {path}")

# Validate spec copies
spec_dir = Path('requirements/service-specs')
for path in sorted(spec_dir.glob('*.md')):
    if path.name == '_template.md':
        continue
    content = path.read_text()
    for header in MANDATORY_SPEC_SECTIONS:
        if header not in content:
            errors.append(f"Spec {path.name} missing mandatory section: {header}")

if errors:
    print("Validation errors found:")
    for e in errors:
        print(f" - {e}")
    sys.exit(1)
else:
    print("All artifacts validated successfully.")
