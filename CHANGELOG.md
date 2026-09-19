# Changelog

## Unreleased — review corrections, September 19, 2026

- Reproduced disclosure of attacker-supplied identifiers in denied read and publish audit events; replaced raw audit resource fields with fixed fixture labels or a constant redaction marker, including on allowed calls.
- Added direct regression cases for denied, allowed and invalid resource arguments, plus syntax-versus-authorization attribution for path variants. Audit event selection remains a possible information channel; this is not a noninterference claim.
- Added article-level pinned ATLAS tactic/technique membership checks, including sub-techniques, and mutation tests for unknown identifiers.
- Bound numbered references to citation labels and URLs; added missing/duplicate and identity/URL swap tests. Remote source identity and semantic support remain human-review responsibilities.
- Corrected the Hardy explanation and documented that the lab uses configured authority rather than caller-supplied capabilities.
- Regenerated expected traces; the three workload outcomes and the unfiltered publication control remain unchanged. No live-agent evaluation or release-license decision was added.

## Unreleased — initial local draft

- Added article, static diagrams, six scenario definitions and 19 references.
- Added a dated ATLAS identifier extract and an author crosswalk with per-mapping caveats.
- Added a deterministic in-memory read/publication policy demonstration.
- Added benign-task and residual-disclosure cases, expected JSON, tests and CI configuration.
- Clarified that the material does not report live-model evaluations, full scenario execution or institutional endorsement.
