"""Build per-endpoint (and per-role) Lambda zip artifacts for dos-search.

This supports:
- one Lambda per endpoint
- a set of Lambdas behind an endpoint (router + worker)

Notes:
- Third-party dependencies are provided via the Lambda dependency layer.
- These zips package only source code: lambdas + shared modules.

"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def _iter_files(base_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in base_dir.rglob("*"):
        if path.is_dir():
            continue
        if "__pycache__" in path.parts:
            continue
        if path.suffix == ".pyc":
            continue
        files.append(path)
    return files


def _zip_paths(zip_path: Path, roots: list[Path], arc_prefixes: list[str]) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for root, arc_prefix in zip(roots, arc_prefixes, strict=True):
            for file_path in _iter_files(root):
                rel = file_path.relative_to(root)
                arcname = str(Path(arc_prefix) / rel)
                zf.write(file_path, arcname)


def build_all(out_dir: Path, application_tag: str) -> dict[str, Path]:
    service_root = Path(__file__).resolve().parents[1]

    # Map artifact key -> lambda source folder
    endpoint_defs: dict[str, Path] = {
        # One-lambda endpoint
        "status-get": service_root / "lambdas" / "status_get",
        # Optional router for /_status (only when enabled)
        "status-get-router": service_root / "lambdas" / "status_get_router",
        # Default /Organization single-lambda endpoint
        "organization-get": service_root / "functions",
        # Set-of-lambdas endpoint (optional)
        "organization-get-router": service_root / "lambdas" / "organization_get_router",
        "organization-get-worker": service_root / "lambdas" / "organization_get_worker",
        # Example additional internal workers (spike)
        "organization-get-worker-2": service_root
        / "lambdas"
        / "organization_get_worker",
        "organization-get-worker-3": service_root
        / "lambdas"
        / "organization_get_worker",
    }

    outputs: dict[str, Path] = {}

    for name, endpoint_root in endpoint_defs.items():
        zip_name = f"ftrs-dos-dos-search-{name}-lambda-{application_tag}.zip"
        out_zip = out_dir / zip_name

        if name == "organization-get":
            roots = [
                service_root / "functions",
            ]
            arc_prefixes = [
                "functions",
            ]
        else:
            roots = [
                endpoint_root,
                service_root / "functions",
                service_root / "health_check",
            ]
            arc_prefixes = [
                "lambdas",
                "functions",
                "health_check",
            ]

        _zip_paths(out_zip, roots=roots, arc_prefixes=arc_prefixes)
        outputs[name] = out_zip

    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output directory where zip artifacts will be written",
    )
    parser.add_argument(
        "--application-tag",
        default=os.environ.get("APPLICATION_TAG", "latest"),
        help="Application tag used in artifact file names",
    )

    args = parser.parse_args()

    outputs = build_all(out_dir=args.out, application_tag=args.application_tag)
    for name, path in outputs.items():
        print(f"built {name}: {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
