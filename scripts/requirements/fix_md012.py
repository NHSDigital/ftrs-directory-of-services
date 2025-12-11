import re
from pathlib import Path


def fix_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    new_lines = []
    blank_streak = 0
    for ln in lines:
        # Treat lines with only whitespace as blank
        if ln.strip() == "":
            blank_streak += 1
            # Allow at most one blank line in a row
            if blank_streak == 1:
                new_lines.append("\n")
            else:
                # skip additional blank lines
                continue
        else:
            blank_streak = 0
            new_lines.append(ln)

    content = "".join(new_lines)
    if content != original:
        path.write_text(content, encoding="utf-8")
        return True
    return False


def main() -> None:
    # __file__ = scripts/requirements/fix_md012.py; repo root is two levels up
    repo_root = Path(__file__).resolve().parents[2]
    # Focus on the folders with reported MD012 violations
    targets = [
        repo_root / "docs/nfrs/nfr-by-domain.md",
        repo_root / "docs/nfrs/nfr-by-domain",
        repo_root / "requirements/user-stories/backlog",
    ]

    changed = 0
    for t in targets:
        if t.is_file() and t.suffix == ".md":
            changed += 1 if fix_file(t) else 0
        elif t.is_dir():
            for p in t.rglob("*.md"):
                changed += 1 if fix_file(p) else 0

    print(f"Fixed MD012 in {changed} files")


if __name__ == "__main__":
    main()
