# Contributing

Contributions should improve a concrete explanation, assumption, mapping, implementation or reproducibility issue.

For a conceptual correction, include the passage or data entry, the problem, a proposed correction, and a primary source or counterexample. Distinguish factual errors from alternative organizational choices.

For code changes, state what behavior changes and run:

```sh
python3 -m killchain_lab.validate
python3 -m unittest discover -s tests -v
```

Use synthetic data. Scenario payloads must remain inert strings unless a separate, explicitly documented test harness executes them inside an appropriate isolated environment. This project currently makes no external requests and uses no model credentials.

Keep these distinctions visible:

- Scripted explanation versus measured behavior.
- Existing-permission misuse versus expanded effective authority.
- Input delivery versus behavioral influence versus consequential impact.
- Public-source attribution versus endorsement or independent validation.

Do not change expected results merely to make a failing test pass. Explain any changed policy or workload and preserve benign-task checks and residual failure cases.

Original-material licensing is still pending in this private draft. Resolve the license before accepting external contributions or publishing a public release.
