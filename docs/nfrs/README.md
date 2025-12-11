# FtRS NFRs – Generated Pages

This folder contains auto-generated non-functional requirement views.

- `nfr-by-domain.md`: Summary index of domains linking to pages in `nfr-by-domain/`
- `nfr-by-domain/`: Per-domain pages (e.g., security.md, accessibility.md) derived from the NFR matrix and expectations registries
- `nfr-by-service.md`: Summary index of services linking to pages in `nfr-by-service/`
- `nfr-by-service/`: Per-service pages, grouped controls and requirements for each service

## Refresh Order

1. Generate domain pages and domain summary:

```zsh
make nfrs-by-domain
```

1. Generate service pages and service summary (depends on domain pages):

```zsh
make nfrs-by-service
```

## Notes

- These files are auto-generated; please do not hand-edit.
- The domain generator (`scripts/nfr/refresh_simplified_nfr_page.py`) requires PyYAML. If you see `ModuleNotFoundError: No module named 'yaml'`, install it in a virtual environment:

```zsh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pyyaml
make nfrs-by-domain
make nfrs-by-service
```
