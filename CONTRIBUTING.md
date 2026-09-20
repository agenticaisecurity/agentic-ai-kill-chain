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

By intentionally submitting original material for inclusion, you agree to license your contribution under the applicable terms in [LICENSE.md](LICENSE.md): MIT for code and CC BY 4.0 for original prose, diagrams and explanatory data. Identify third-party material and preserve its notices. Submit only material you are authorized to contribute.
