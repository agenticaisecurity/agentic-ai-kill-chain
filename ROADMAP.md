# Development roadmap

## Initial local draft — implemented

- [x] Full article and five diagrams, with editable SVGs.
- [x] Six structured scenario definitions with explicit prerequisites.
- [x] Versioned ATLAS identifier extract and caveated crosswalk.
- [x] Deterministic policy demonstration with benign, protected-file and residual-disclosure cases.
- [x] Reproducible expected JSON and local unit/content checks.
- [x] GitHub Actions configuration for Python 3.11–3.13.

## Next: prepare the first public release

- [ ] Select a license for the original code and writing; retain upstream notices.
- [x] Review the staged repository contents and create its first commit.
- [x] Create the private GitHub repository under `agenticaisecurity` and push only this companion.
- [x] Confirm the Python 3.11–3.13 CI matrix passes on GitHub (initial run: https://github.com/agenticaisecurity/agentic-ai-kill-chain/actions/runs/35427034310).
- [ ] Ask for specific mapping or threat-model feedback; record corrections in the changelog.

## Then: one real agent experiment

- [ ] Choose a single agent implementation and model version.
- [ ] Replace the supplied adversarial action sequence with a controlled retrieved-input experiment.
- [ ] Record task success, attack-goal success, refusals and tool-policy denials separately.
- [ ] Use the same tasks and fixtures under broad and scoped policies; preserve the residual case.
- [ ] Run repeated trials and adaptive variants; publish configuration, raw counts, limitations and uncertainty.
- [ ] Test clean-environment reproduction before claiming measured results.

Do not expand to all six scenarios or robotics until this small experiment is reproducible and its boundaries are understood. Future work is not evidence for current claims.
