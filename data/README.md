# Structured companion data

All data files are UTF-8 JSON. They require no parser dependencies beyond the Python standard library.

## Scenario definitions

`scenarios/*.json` contains six **scripted illustrations**, each with:

- `schema_version`, `id`, `title` and explicit evidence/implementation status.
- `threat_model`: attacker-controlled inputs, victim access, attacker-visible output and authority classification.
- `briefing`: context and prerequisites carried from the reviewed article.
- Six `checkpoints`: category, static narration, and status. A checkpoint may be skipped or denied; its presence does not mean that stage occurred.
- `limitations` and source-edition provenance.

The supported authority classifications are `existing-permission-misuse`, `confused-deputy`, and `denied-at-access-boundary`. Existing-permission misuse must mark the escalation checkpoint `skipped-existing-authority`.

Narration is data, including any example instructions or tool strings. The loader does not execute it. Do not describe these objects as recorded model traces or attack results.

## ATLAS identifiers and crosswalk

`atlas-2026.01-identifiers.json` retains 16 tactic identifier/name pairs and six technique identifier/name pairs from the dated official ATLAS release. It records the source URL and SHA-256 fingerprint of the full upstream bytes used for extraction. The full upstream dataset is not bundled; the fingerprint is provenance, not a claim that a local copy is being independently rechecked on every run.

`atlas-crosswalk.json` adds author-assigned associations with one or more teaching stages, a rationale and a caveat. Those associations are not endorsed by MITRE. An identifier match is not proof that a mapping is conceptually sound or complete.

`references.json` lists the article's 19 external source URLs. Runtime validation checks their presence and format, not current remote availability or the correctness of every assertion attributed to them.

Run `python3 -m killchain_lab.validate` from the repository root to check these invariants. The Python validator is the executable format specification for this initial draft. If the format evolves, update its version, documentation and compatibility tests together.
