#!/usr/bin/env python3
"""Format newly generated user stories to satisfy markdownlint rules.
- Ensure first content heading is H1 with the story title
- Ensure blank line after headings
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
BACKLOG = ROOT / "requirements" / "user-stories" / "backlog"

def process(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    changed = False
    # Extract title from front matter
    title = None
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            if lines[i].startswith("title:"):
                title = lines[i].split(":",1)[1].strip()
            i += 1
        end_front = i if i < len(lines) else 0
        # After front matter, ensure H1 heading
        insert_pos = end_front + 1 if end_front < len(lines) else len(lines)
        # If next non-empty line starts with '#', consider ok
        j = end_front + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines) or not lines[j].lstrip().startswith('#'):
            h1 = f"# {title or path.stem}"
            lines.insert(insert_pos, h1)
            changed = True
    # Ensure blank line after any heading
    i = 0
    while i < len(lines):
        if re.match(r"^#{1,6} \S", lines[i]) is not None:
            # If next line exists and isn't blank, insert blank
            if i+1 < len(lines) and lines[i+1].strip() != "":
                lines.insert(i+1, "")
                changed = True
                i += 1
        i += 1
    if changed:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


def main():
    changed = 0
    for md in sorted(BACKLOG.glob("STORY-*-*.md")):
        if process(md):
            print(f"Formatted {md}")
            changed += 1
    print(f"Changed {changed} files")

if __name__ == "__main__":
    main()
