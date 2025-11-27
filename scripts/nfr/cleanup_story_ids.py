#!/usr/bin/env python3
from __future__ import annotations
import shutil
from pathlib import Path
from datetime import datetime
import sys

try:
    import yaml
except ModuleNotFoundError:
    print("PyYAML required. Activate venv and install pyyaml.", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
NFR_ROOT = ROOT / "requirements" / "nfrs"

def ts() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def rel(path: Path) -> Path:
    try:
        return path.relative_to(NFR_ROOT)
    except Exception:
        return path

def filter_story_list(val):
    if not isinstance(val, list):
        return val
    kept = [str(x) for x in val if not (isinstance(x, str) and x.strip().upper().startswith("STORY-"))]
    return kept

def process_nfrs_yaml(path: Path) -> bool:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    changed = False
    nfrs = data.get("nfrs")
    if isinstance(nfrs, list):
        for n in nfrs:
            if isinstance(n, dict):
                if "stories" in n and isinstance(n["stories"], list):
                    filtered = filter_story_list(n["stories"])
                    if filtered != n["stories"]:
                        n["stories"] = filtered
                        changed = True
                ops = n.get("operations")
                if isinstance(ops, list):
                    for op in ops:
                        if isinstance(op, dict) and isinstance(op.get("stories"), list):
                            filtered = filter_story_list(op["stories"])
                            if filtered != op["stories"]:
                                op["stories"] = filtered
                                changed = True
                # Also scrub stories on embedded controls, if present in nfrs.yaml
                ctrls = n.get("controls")
                if isinstance(ctrls, list):
                    for c in ctrls:
                        if isinstance(c, dict) and isinstance(c.get("stories"), list):
                            filtered = filter_story_list(c["stories"])
                            if filtered != c["stories"]:
                                c["stories"] = filtered
                                changed = True
    if changed:
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return changed

def process_expectations_yaml(path: Path) -> bool:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    changed = False
    # controls list
    controls = data.get("controls")
    if isinstance(controls, list):
        for c in controls:
            if isinstance(c, dict) and isinstance(c.get("stories"), list):
                filtered = filter_story_list(c["stories"])
                if filtered != c["stories"]:
                    c["stories"] = filtered
                    changed = True
    # operations list (in case expectations hold perf ops)
    ops = data.get("operations")
    if isinstance(ops, list):
        for op in ops:
            if isinstance(op, dict) and isinstance(op.get("stories"), list):
                filtered = filter_story_list(op["stories"])
                if filtered != op["stories"]:
                    op["stories"] = filtered
                    changed = True
    if changed:
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return changed

def main() -> int:
    backup_dir = NFR_ROOT / f"_backups/remove_story_ids_{ts()}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    changed_files: list[Path] = []
    for dirpath in NFR_ROOT.iterdir():
        if not dirpath.is_dir():
            continue
        nfrs_yaml = dirpath / "nfrs.yaml"
        if nfrs_yaml.exists():
            # backup
            dst = backup_dir / rel(nfrs_yaml)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(nfrs_yaml, dst)
            if process_nfrs_yaml(nfrs_yaml):
                changed_files.append(nfrs_yaml)
        expectations_yaml = dirpath / "expectations.yaml"
        if expectations_yaml.exists():
            dst = backup_dir / rel(expectations_yaml)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(expectations_yaml, dst)
            if process_expectations_yaml(expectations_yaml):
                changed_files.append(expectations_yaml)

    print(f"Backups stored under: {backup_dir}")
    if changed_files:
        print("Updated files:")
        for f in changed_files:
            print(f" - {rel(f)}")
    else:
        print("No STORY-* references found to remove.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
