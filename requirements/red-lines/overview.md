# Red Lines Overview

# Red Lines Overview

This document normalizes the PDF content into concise tables, separating core statements from noisy multi-column artefacts. The raw extract is preserved below for audit.

Cross-reference: See the NFR/control mapping in `requirements/red-lines/mapping/red-lines-to-nfr.md`.

Verification Checklist (update in mapping file):
- [ ] Every Ref has at least one Proposed NFR/Control ID
- [ ] Status advanced from `proposed` to `agreed` or `verified`
- [ ] Owner/team recorded per Ref
- [ ] Evidence links (dashboards / ADRs / CI) captured
- [ ] Last review date within past quarter
- [ ] Exceptions documented where applicability is partial

### Cloud / Infrastructure

| Ref | Summary | Related Principles/Patterns |
|-----|---------|-----------------------------|
| Cloud-1 | New services run on public cloud with product-owned accounts; AWS within NHS AWS Landing Zone; Azure within NHSE-LZ-Root; internet-first; autoscale down ≥40%; blue/green for gold/platinum; DR restore tested in isolation | Overproduction principle; Cloud practices; Deployments pattern |
| Cloud-2 | Backup and restore: immutable backups with annual restore validation; additional measures if RPO=0 required | Cloud backups blueprint |
| Cloud-3 | Active-passive services must swap active/passive at least every 12 months | Cloud practices |
| Cloud-4 | Use mandatory cloud blueprints (AWS/Azure) for backups and DR | Cloud backups blueprint |
| Cloud-5 | Inventory and utilization: infrastructure should be fully utilized; services auto-scale | Inventory principle; Cloud practices |
| Cloud-6 | Test scenarios aligned to Cloud-5/6 for resilience | Deployments pattern |
| Cloud-7 | Cloud backups must be defined and tested | Cloud backups blueprint |
| Cloud-8 | No standing write access to production; only time-bound (≤24h) elevation with human approval; use AWS CCOE solution / Azure PIM | Security practices |

### Using Shared Services

| Ref | Summary | Related Principles/Patterns |
|-----|---------|-----------------------------|
| Reuse-1 | Use NHS Notify for citizen communications | Overproduction principle |
| Reuse-2 | PDS is single source of truth for demographics | Data governance |
| Reuse-3 | Citizen auth must use NHS login (proxy access currently excluded) | Identity & Access |
| Reuse-4 | If IAL3 required use CIS2; otherwise use CIS2 or NHS.net | Identity Assurance (NIST IAL) |
| Reuse-5 | Consult FDP/CDP for analytics; don’t build new analytics platforms; use cloud-native tools for simple analysis | Overproduction principle |
| Reuse-6 | National cohorting must use Cohorting As A Service | Reuse-first |
| Reuse-7 | Align UIs with `nhsuk-frontend` and NHS Design System; contribute new components; use `nhsuk-react-components` per WG | Design System |

### Software Development Lifecycle

| Ref | Summary | Related Principles/Patterns |
|-----|---------|-----------------------------|
| SDLC-1 | Use NHS GitHub Enterprise; comply with securing-repositories and engineering dashboards | Code security; Governance |
| SDLC-2 | Primary branch builds use SonarCloud; pass 4 quality gates; total unit test coverage >50% | Accessing SonarCloud; Quality gates |
| SDLC-3 | Build and deploy to production at least quarterly | Little and often pattern |
| SDLC-4 | All planned production deployments must be automated | Automate everything pattern |
| SDLC-5 | Under active development: build daily, deploy at least every two weeks outside freeze | Flow efficiency |
| SDLC-6 | Apply architect-for-flow: deliver changes per bounded context in independently deployable components | Architect-for-flow pattern |

### Software Management

| Ref | Summary | Related Principles/Patterns |
|-----|---------|-----------------------------|
| Soft-1 | External APIs follow published API guidance; use Digital Onboarding Service (DOS); no SCALs | API Policies & Best Practice |
| Soft-2 | Maintain Software Bill of Materials (SBOM) via central approach | SBOM; What Good Looks Like |
| Soft-3 | Do not use end-of-life software; keep non-policy versions updated ≤6 months; apply patches per CVM | Cyber Vulnerability Management |
| Soft-4 | Quarterly team maturity review using Software Quality Framework | Team self-assessment |
| Soft-5 | Align with Tech Radar; migration away from AVOID; approval required for CONTAIN/PROPOSED/AVOID in production and for platform use | Tech Radar |
| Soft-6 | Comply with mandatory engineering blueprints within 6 months of mandate | Blueprints |
| Soft-7 | No dependencies on services/APIs within 6 months of retirement unless service retires first | Dependency hygiene |
| Soft-8 | No network dependencies relying on security protocols within 6 months of retirement unless service retires first | Protocol hygiene |

### Team-Specific (Spine)

| Ref | Summary | Related Principles/Patterns |
|-----|---------|-----------------------------|
| Spine-1 | Riak database type is deprecated; retire in Spine by end of 2027 | Tech Radar |

---
### Appendix: Raw Extract (sanitised)

The following is the sanitized raw text extracted from the PDF for auditability.

```text
<< Raw extract omitted here for brevity — retained in version history >>
```
#### SDLC-1
