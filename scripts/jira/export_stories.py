#!/usr/bin/env python3
"""Export backlog stories to plain text blocks for Jira paste.

Creates output directory: .jira-export
For each STORY-*.md in requirements/user-stories/backlog/ produce a .txt file with:
- Summary (title)
- Body (Description + Acceptance Criteria + Non-Functional Acceptance)
- NFR refs list
Skips internal sections (Implementation Notes, Risks & Mitigation, Open Questions) unless needed.
"""
from pathlib import Path
import re
import yaml
import textwrap

STORY_DIR = Path('requirements/user-stories/backlog')
OUT_DIR = Path('.jira-export')
OUT_DIR.mkdir(exist_ok=True)

RE_FRONT_MATTER = re.compile(r'^---\n(.*?)\n---', re.DOTALL)

def extract_sections(md: str):
    # Simple split by headers
    sections = {}
    current = None
    for line in md.splitlines():
        if line.startswith('## '):
            current = line[3:].strip()
            sections[current] = []
        elif current:
            sections[current].append(line)
    return {k: '\n'.join(v).strip() for k,v in sections.items()}

for path in sorted(STORY_DIR.glob('STORY-*.md')):
    text = path.read_text()
    fm_match = RE_FRONT_MATTER.search(text)
    if not fm_match:
        print(f"Skipping {path.name}: no front matter")
        continue
    front = yaml.safe_load(fm_match.group(1)) or {}
    body_without_fm = text[fm_match.end():].strip()
    sections = extract_sections(body_without_fm)

    summary = front.get('title','(no title)')
    description = sections.get('Description','')
    acceptance = sections.get('Acceptance Criteria','')
    nonfunc = sections.get('Non-Functional Acceptance','')
    nfr_refs = front.get('nfr_refs', []) or []

    export_text = textwrap.dedent(f"""
    Summary: {summary}

    Description:
    {description}

    Acceptance Criteria:
    {acceptance}

    Non-Functional Acceptance:
    {nonfunc}

    NFR References: {', '.join(nfr_refs)}
    Story ID: {front.get('story_id')}
    Status: {front.get('status')}
    """).strip() + "\n"

    out_file = OUT_DIR / f"{path.stem}.txt"
    out_file.write_text(export_text)
    print(f"Exported {out_file}")

print("Export complete.")
