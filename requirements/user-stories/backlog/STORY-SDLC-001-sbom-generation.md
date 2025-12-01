---
code: STORY-SDLC-001
as_a: DevSecOps_Engineer
i_want: generate_sbom_for_every_build
so_that: we_have_transparency_into_component_risks
business_value: Enables rapid vulnerability impact assessment
nfr_refs: [NFR-SDLC-SBOM-01]
nfr_tags: [sdlc, security]
acceptance_criteria:
  - GIVEN build pipeline WHEN artifact produced THEN SBOM generated in SPDX or CycloneDX format
  - GIVEN vulnerability scan WHEN performed THEN SBOM used to correlate affected components
  - GIVEN missing SBOM WHEN detected THEN build fails with actionable error
out_of_scope:
  - Manual SBOM curation outside automation
notes: |
  Evidence: pipeline logs, SBOM file sample, failing build example.
---
# Summary
Automated SBOM generation integrated into build pipeline.

## Detail
Adds automated SBOM (SPDX or CycloneDX) generation to build pipeline, failing builds without SBOM presence and enabling rapid correlation during vulnerability scans. Ensures traceability of components for risk assessment.

## Deriving Acceptance Criteria from NFRs
- NFR-SDLC-SBOM-01: SBOM produced for each artifact; used in vulnerability correlation; missing SBOM fails build.

## INVEST Checklist
- Independent: Does not depend on quality gate enforcement.
- Negotiable: Chosen SBOM format specifics.
- Valuable: Speeds vulnerability impact evaluation.
- Estimable: Pipeline step + validation logic tasks.
- Small: Single build stage addition.
- Testable: Pipeline logs, SBOM sample, failing build example.
