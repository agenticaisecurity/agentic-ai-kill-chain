# Limitations and questions for reviewers

## What is the contribution?

An explanatory organization of existing security ideas, accompanied by structured assumptions and one runnable policy example. There is no claim of a new attack class, optimal stage count, exhaustive taxonomy or improved threat-modeling effectiveness.

## Why a chain if attacks branch or skip stages?

The labels support teaching. Actual assessments should use paths or graphs that preserve branches and loops. An overprivileged agent can disclose data without escalation; an attacker with configuration-write access can begin with persistence. Fraud, destruction, resource exhaustion and unsafe physical actions require additional impact-specific analysis.

## Are the mappings official?

No. The identifier extract comes from ATLAS release 2026.01. The crosswalk is the author's interpretation. Its validator checks identifier/name consistency and required rationale, not whether the proposed association is the best conceptual mapping. Tactics, techniques and teaching stages are different kinds of categories.

Collection is not exfiltration; credential access is not automatically escalation; lateral movement need not increase privilege; command and control does not require persistence. The crosswalk records those caveats.

## Do these tests validate model security?

No. Tests validate this small implementation and content invariants. Scenario transcripts are predetermined. No LLM runs, adaptive attacks, multi-model comparison, detector evaluation or attack-success measurement have been performed. A published benchmark citation is not a benchmark reproduction.

## Is reading a secret privilege escalation?

Only if the relevant principal gains effective authority it did not already have. The implemented broad policy already grants read access, so its misuse is not escalation. The documented multi-agent scenario describes a different case: inducing a higher-privilege deputy to act without caller-scoped authorization.

## Does path scoping prevent disclosure?

It can block the illustrated out-of-scope read. The included residual case demonstrates that sensitive material inside the allowed source can still be disclosed through a permitted output. Resource permissions, data authorization, destination policy and task intent are related but distinct controls.

## Do signatures, schema validation or prompt instructions make content safe?

No. Provenance is not benign intent, structurally valid arguments can request harmful actions, and system messages do not replace execution-time authorization. A trusted writer can store malicious content; an integrity check can faithfully preserve it.

## What is needed before empirical claims?

A versioned agent implementation, model/tool configuration, explicit attacker-controlled inputs and outputs, benign task criteria, repeated trials, adaptive attempts, utility and attack-success measures, raw traces with synthetic data, uncertainty estimates and independently reproducible commands. Report failed attacks, successful attacks, benign failures and exclusions. These are future work.

## Is this a physical AI security framework?

No. There is no robotics implementation, hardware validation, controller analysis or physical-safety evidence here. Extending this work to robots requires a separate threat model and experiments.

## Has anyone endorsed or independently reviewed it?

No MITRE, OWASP, employer or independent peer-review endorsement is claimed. Public-source checks, local unit tests and editorial corrections do not constitute such endorsement. Good-faith counterexamples are welcome.
