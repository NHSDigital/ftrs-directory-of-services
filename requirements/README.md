# Requirements Workspace

This workspace holds product User Stories and Non-Functional Requirements (NFRs) in source-controlled form so Copilot (and later MCP-linked tooling) can:

- Suggest acceptance criteria based on tagged NFRs
- Generate story boilerplate and traceability links
- Provide cross-references for compliance, audit and release readiness

## Structure

```
requirements/
  README.md                      Overview
  nfrs/
    areas/                       Top-level NFR domains
      security/
      performance/
      reliability/
      scalability/
      operability/
      maintainability/
      accessibility/
      privacy/
      compliance/
      cost/
    cross-references/            Matrices & linkage files
      index.yaml                 Canonical NFR registry
      nfr-matrix.md              Table linking domains → stories
      tags.md                    Tagging & coding conventions
  user-stories/
    templates/                   Story & acceptance criteria templates
    backlog/                     New / unprioritised stories
    in-progress/                 Active development
    done/                        Accepted & merged stories
```

## Conventions

### File Naming
- NFR high-level domain overviews: `overview.md` inside each domain directory.
- Atomic NFRs (testable statements): `NFR-CODE.md` (e.g. `PERF-001.md`).
- User stories: `STORY-<increment>-<slug>.md` (e.g. `STORY-042-search-gp-endpoints.md`).

### Codes
| Domain | Prefix |
|--------|--------|
| Security | SEC |
| Performance | PERF |
| Reliability | REL |
| Scalability | SCALE |
| Operability | OPER |
| Maintainability | MAINT |
| Accessibility | A11Y |
| Privacy | PRIV |
| Compliance | COMP |
| Cost Optimisation | COST |

Each atomic NFR increments (e.g. `SEC-001`, `SEC-002`). Do not recycle codes.

### Linking Stories → NFRs
In a story front-matter block include `nfr_refs: [SEC-003, PERF-002]`. Copilot can then surface acceptance criteria scaffolds.

### Story Template Keys
- `as_a`
- `i_want`
- `so_that`
- `business_value`
- `nfr_refs` (array)
- `acceptance_criteria`
- `out_of_scope`
- `notes`

## Cross Reference Flow
1. Add or refine an atomic NFR in the relevant domain.
2. Update `nfrs/cross-references/index.yaml` registry.
3. Reference the NFR code(s) in story front-matter.
4. Generate acceptance criteria using template - Copilot can expand by pulling test phrases aligned to each NFR.

## Next Steps
- Populate each domain with initial NFRs.
- Add story examples referencing them.
- Automate validation (lint) to ensure referenced NFR codes exist.
