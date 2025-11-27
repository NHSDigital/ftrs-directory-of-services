# NFR Scripts

This folder contains utilities for Non-Functional Requirements documentation and validation.

## Files

- `refresh_simplified_nfr_page.py` — Generates `docs/developer-guides/nfr-all-simplified.md` from the cross-reference matrix and any per-domain expectations registries found under `requirements/nfrs/**/expectations.yaml`.
- `validate_nfr_refs.py` — Validates that story front-matter `nfr_refs` codes exist in the cross-reference registry.

## Usage

### Refresh simplified NFR page

```python
python3 scripts/nfr/refresh_simplified_nfr_page.py
```

Outputs a Confluence-ready Markdown file summarising:

- All NFR codes grouped by domain from `requirements/nfrs/cross-references/nfr-matrix.md`
- Performance Expectations Registry Summary (per-operation targets)
- Domain Expectations Registry Summaries (Security, Observability, Reliability, Availability, Scalability, Interoperability, Accessibility, Cost, Governance, Compatibility)

The script auto-detects registries: if a file `requirements/nfrs/<domain>/expectations.yaml` exists, it gets rendered.

### Authoring registries

See `requirements/README.md` for the common schema and locations. When editing YAML:

- Quote values that contain comparison operators (e.g., ">= 95%").
- Keep mapping keys aligned (consistent indentation).
- Prefer lists for `environments` and `services`.

### Notes

- Timestamp uses timezone-aware UTC via `datetime.now(timezone.utc)`.
- Do not hand-edit `docs/developer-guides/nfr-all-simplified.md`; always regenerate via the script.
