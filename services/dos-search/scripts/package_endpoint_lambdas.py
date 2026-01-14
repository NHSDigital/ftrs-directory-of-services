"""Build Lambda zip artefacts for dos-search.

Goal
- Produce one ZIP per Lambda, with deterministic contents.
- Each endpoint Lambda ZIP includes shared code from `functions/libraries`.

Lambda sources
- Endpoint lambdas live under `functions/<lambda_name>/handler.py`.
- `_status` is implemented as a legacy entrypoint under `lambdas/status_get/handler.py`.

Artefacts
- Zip name:  ftrs-dos-dos-search-<lambda_name>-lambda-<application_tag>.zip
- Internal paths are arranged so Terraform handlers like:
    functions/<lambda_name>/handler.lambda_handler
  resolve correctly.

Notes
- Third-party dependencies are provided via the dependency layer.
- These zips package only source code: endpoint handlers + shared modules.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

SERVICE = "dos-search"
ARTEFACT_PREFIX = "ftrs-dos-dos-search"

ARC_FUNCTIONS_LIBRARIES = "functions/libraries"
ARC_HEALTH_CHECK = "health_check"

FUNCTIONS_DIRNAME = "functions"
LIBRARIES_DIRNAME = "libraries"
LEGACY_LAMBDAS_DIRNAME = "lambdas"


@dataclass(frozen=True)
class LambdaPackage:
    name: str
    roots: list[Path]
    arc_prefixes: list[str]


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
    if len(roots) != len(arc_prefixes):
        raise ValueError

    zip_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for root, arc_prefix in zip(roots, arc_prefixes, strict=True):
            if not root.exists():
                raise FileNotFoundError(str(root))

            for file_path in _iter_files(root):
                rel = file_path.relative_to(root)
                arcname = str(Path(arc_prefix) / rel)
                zf.write(file_path, arcname)


def _zip_name(lambda_name: str, application_tag: str) -> str:
    return f"{ARTEFACT_PREFIX}-{lambda_name}-lambda-{application_tag}.zip"


def _artifact_name_from_folder(folder_name: str) -> str:
    """Convert a `functions/<folder_name>` into the artefact/lambda name.

    Convention:
    - Python folders use snake_case (e.g. triage_code)
    - Artefacts / terraform lambda_name use kebab-case (e.g. triage-code)

    Special-case:
    - `organisation` folder maps to `organization` (terraform naming)
    """

    if folder_name == "organisation":
        return "organization"
    return folder_name.replace("_", "-")


def _discover_function_lambdas(service_root: Path) -> list[LambdaPackage]:
    """Discover endpoint lambdas under `functions/<name>/handler.py`.

    We purposely ignore:
    - functions/libraries (shared code)
    - any folder without a handler.py
    """

    functions_dir = service_root / FUNCTIONS_DIRNAME
    libraries_dir = functions_dir / LIBRARIES_DIRNAME

    packages: list[LambdaPackage] = []

    for child in sorted(p for p in functions_dir.iterdir() if p.is_dir()):
        if child.name == LIBRARIES_DIRNAME:
            continue

        handler = child / "handler.py"
        if not handler.exists():
            continue

        package_name = _artifact_name_from_folder(child.name)

        packages.append(
            LambdaPackage(
                name=package_name,
                roots=[child, libraries_dir],
                arc_prefixes=[f"functions/{child.name}", ARC_FUNCTIONS_LIBRARIES],
            )
        )

    return packages


def _legacy_status_lambda(service_root: Path) -> LambdaPackage:
    """Package the legacy `_status` lambda which lives under `lambdas/status_get`."""

    functions_dir = service_root / FUNCTIONS_DIRNAME
    libraries_dir = functions_dir / LIBRARIES_DIRNAME

    return LambdaPackage(
        name="status-get",
        roots=[
            service_root / LEGACY_LAMBDAS_DIRNAME / "status_get",
            libraries_dir,
            service_root / "health_check",
        ],
        arc_prefixes=[
            LEGACY_LAMBDAS_DIRNAME,
            ARC_FUNCTIONS_LIBRARIES,
            ARC_HEALTH_CHECK,
        ],
    )


def build_all(out_dir: Path, application_tag: str) -> dict[str, Path]:
    service_root = Path(__file__).resolve().parents[1]

    packages = [
        _legacy_status_lambda(service_root),
        *_discover_function_lambdas(service_root),
    ]

    outputs: dict[str, Path] = {}
    for pkg in packages:
        out_zip = out_dir / _zip_name(pkg.name, application_tag)
        _zip_paths(out_zip, roots=pkg.roots, arc_prefixes=pkg.arc_prefixes)
        outputs[pkg.name] = out_zip

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

    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="Output format for generated artefacts (table|json)",
    )

    args = parser.parse_args()

    # Fail fast on obviously-invalid output locations.
    # (Also ensures this CLI has meaningful non-zero exit codes.)
    if not args.out.parent.exists():
        print(f"ERROR: parent directory does not exist: {args.out.parent}")
        return 3

    try:
        outputs = build_all(out_dir=args.out, application_tag=args.application_tag)
    except Exception as exc:
        print(f"ERROR: failed to build lambda artefacts: {exc}")
        return 1

    if not outputs:
        print("ERROR: no Lambda artefacts were built")
        return 2

    if args.format == "json":
        payload = {
            "service": SERVICE,
            "application_tag": args.application_tag,
            "out_dir": str(args.out),
            "artefacts": {name: str(path) for name, path in sorted(outputs.items())},
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    # Default: human-readable table
    print(
        f"Built {len(outputs)} Lambda artefact(s) for {SERVICE} (application_tag={args.application_tag})"
    )
    print(f"Output directory: {args.out}")
    print()
    for name, path in sorted(outputs.items()):
        print(f"- {name:18} {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
