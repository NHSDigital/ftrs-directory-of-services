#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re

TARGET_DIR = Path("docs/nfrs/nfr-by-domain")

MD_TABLE_OR_HEADING = re.compile(r"^(#|##|###|\|).*")


def collapse_multiple_blank_lines(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    for line in lines:
        if line.strip() == "":
            if not out or out[-1].strip() != "":
                out.append("")
            else:
                # skip extra blank
                continue
        else:
            out.append(line)
    # ensure single trailing newline
    while out and out[-1].strip() == "":
        out.pop()
    out.append("")
    return "\n".join(out)


def strip_trailing_code_fence(text: str) -> str:
    lines = text.splitlines()
    while lines and lines[-1].strip() in ("", "```"):
        lines.pop()
    lines.append("")
    return "\n".join(lines)


def process_file(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    cleaned = strip_trailing_code_fence(original)
    cleaned = collapse_multiple_blank_lines(cleaned)
    if cleaned != original:
        path.write_text(cleaned, encoding="utf-8")
        print(f"Cleaned: {path}")


def main() -> None:
    if not TARGET_DIR.exists():
        return
    for md in sorted(TARGET_DIR.glob("*.md")):
        process_file(md)

if __name__ == "__main__":
    main()
