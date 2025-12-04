#!/usr/bin/env python3
"""Validate all domain NFR YAML files against the JSON Schema.

Usage:
        .venv/bin/python scripts/nfr/validate_nfrs_yaml.py

Exits with non-zero code if any validation error is found.
"""
from __future__ import annotations
from pathlib import Path
import sys
import json

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    sys.stderr.write("PyYAML is required. Install with: python3 -m pip install pyyaml\n")
    sys.exit(2)

try:
    from jsonschema import Draft202012Validator  # type: ignore
except ModuleNotFoundError:
    sys.stderr.write("jsonschema is required. Install with: python3 -m pip install jsonschema\n")
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "requirements/nfrs/schemas/nfrs.schema.json"
DOMAINS_DIR = ROOT / "requirements/nfrs"

def main() -> int:
    if not SCHEMA_PATH.exists():
        sys.stderr.write(f"Schema file not found: {SCHEMA_PATH}\n")
        return 2
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    errors: list[str] = []
    for yml in sorted(DOMAINS_DIR.glob("*/nfrs.yaml")):
        try:
            data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
        except Exception as e:
            errors.append(f"{yml}: YAML parse error: {e}")
            continue
        # Normalize fields that may parse as non-JSON-native types (e.g., datetime)
        if isinstance(data.get("generated"), (object,)):
            gen = data.get("generated")
            try:
                # datetime objects have isoformat
                iso = getattr(gen, "isoformat", None)
                if callable(iso):
                    data["generated"] = iso()
            except Exception:
                pass
        if "version" in data and not isinstance(data["version"], (str, int, float)):
            data["version"] = str(data["version"])
        # Schema validation
        for err in validator.iter_errors(data):
            path = "/".join(str(x) for x in err.path) or "."
            errors.append(f"{yml}: {err.message} at {path}")
        # Uniqueness check for NFR codes within file
        codes = [n.get("code") for n in (data.get("nfrs") or [])]
        duplicates = sorted({c for c in codes if c and codes.count(c) > 1})
        if duplicates:
            errors.append(f"{yml}: duplicate NFR codes found: {', '.join(duplicates)}")

    if errors:
        sys.stderr.write("Schema validation failed:\n")
        for e in errors:
            sys.stderr.write(f" - {e}\n")
        return 1
    else:
        print("All NFR YAML files are valid.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
