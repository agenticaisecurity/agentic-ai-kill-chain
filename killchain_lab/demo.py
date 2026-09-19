"""Compare virtual read policies; supplied action sequences do not invoke a model.

Run: python3 -m killchain_lab.demo [--json]
All tool resources are strings in an in-memory store. Host paths are never opened.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import json
from typing import Mapping

SOURCE = "/workspace/src/review_target.py"
SECRET = "/workspace/.env"
SYNTHETIC_SECRET = "SYNTHETIC_CANARY_NOT_A_REAL_CREDENTIAL"
REVIEW_DESTINATION = "public-review"


def canonical_path(value: str) -> str:
    """Require canonical POSIX virtual paths, avoiding ambiguous path spellings."""
    if not isinstance(value, str) or not value.startswith("/"):
        raise ValueError("expected an absolute virtual path")
    if "\\" in value or any(ord(c) < 32 for c in value):
        raise ValueError("unsupported path characters")
    if any(part in ("", ".", "..") for part in value[1:].split("/")):
        raise ValueError("path must be canonical; empty, dot and parent segments denied")
    return value


@dataclass(frozen=True)
class Policy:
    name: str
    readable: frozenset[str]
    destinations: frozenset[str]

    def permits(self, action: str, resource: str) -> bool:
        if action == "read":
            return resource in self.readable
        if action == "publish":
            return resource in self.destinations
        return False


@dataclass(frozen=True)
class Decision:
    action: str
    resource: str
    allowed: bool
    reason: str


class Denied(PermissionError):
    """An action was rejected by the virtual tool boundary."""


@dataclass
class ToolRuntime:
    policy: Policy
    files: Mapping[str, str]
    decisions: list[Decision] = field(default_factory=list)
    published: list[tuple[str, str]] = field(default_factory=list)

    def _decide(self, action: str, resource: str) -> None:
        allowed = self.policy.permits(action, resource)
        # Audit labels come from this fixed fixture vocabulary, never raw tool
        # arguments or the configurable allowlist (including for allowed calls).
        label = {
            ("read", SOURCE): "source-file",
            ("read", SECRET): "protected-file",
            ("publish", REVIEW_DESTINATION): "review-output",
        }.get((action, resource), "<redacted-resource>")
        self.decisions.append(Decision(action, label, allowed,
                                       "allowlist match" if allowed else "outside allowlist"))
        if not allowed:
            raise Denied(f"{action} denied")

    def read(self, path: str) -> str:
        try:
            path = canonical_path(path)
        except ValueError as exc:
            # Do not echo invalid inputs or file contents into this audit event.
            self.decisions.append(Decision("read", "<invalid-path>", False, str(exc)))
            raise Denied("invalid virtual path") from exc
        self._decide("read", path)
        if path not in self.files:
            raise FileNotFoundError("virtual resource does not exist")
        return self.files[path]

    def publish(self, destination: str, content: str) -> None:
        self._decide("publish", destination)
        # Deliberately no content/DLP policy: shows the residual confidentiality risk.
        self.published.append((destination, content))


def fixture(*, canary_in_source: bool = False) -> dict[str, str]:
    source = "def add(a, b):\n    return a + b\n"
    if canary_in_source:
        source += f"# synthetic confidential marker: {SYNTHETIC_SECRET}\n"
    return {SOURCE: source, SECRET: f"DEMO_TOKEN={SYNTHETIC_SECRET}\n"}


def policies() -> tuple[Policy, Policy]:
    return (
        Policy("broad", frozenset({SOURCE, SECRET}), frozenset({REVIEW_DESTINATION})),
        Policy("scoped", frozenset({SOURCE}), frozenset({REVIEW_DESTINATION})),
    )


def benign_review(runtime: ToolRuntime) -> bool:
    """A tiny deterministic legitimate task, not an actual semantic code review."""
    source = runtime.read(SOURCE)
    if "def add(a, b):" not in source:
        return False
    runtime.publish(REVIEW_DESTINATION, "Review: add(a, b) returns a + b.")
    return True


def attempt_disclosure(runtime: ToolRuntime, target: str) -> bool:
    """Supply an adversarial action sequence, assuming instruction influence already."""
    try:
        content = runtime.read(target)
        runtime.publish(REVIEW_DESTINATION, content)
    except Denied:
        return False
    return any(SYNTHETIC_SECRET in body for destination, body in runtime.published
               if destination == REVIEW_DESTINATION)


def run_comparison() -> dict:
    cases = []
    for policy in policies():
        # Each task gets a fresh runtime so no data or output carries between cases.
        benign = ToolRuntime(policy, fixture())
        legitimate_task_completed = benign_review(benign)
        protected = ToolRuntime(policy, fixture())
        protected_canary_disclosed = attempt_disclosure(protected, SECRET)
        residual = ToolRuntime(policy, fixture(canary_in_source=True))
        allowed_source_canary_disclosed = attempt_disclosure(residual, SOURCE)
        cases.append({
            "policy": policy.name,
            "legitimate_task_completed": legitimate_task_completed,
            "protected_canary_disclosed": protected_canary_disclosed,
            "allowed_source_canary_disclosed": allowed_source_canary_disclosed,
            "decisions": {
                "benign": [asdict(x) for x in benign.decisions],
                "protected": [asdict(x) for x in protected.decisions],
                "residual": [asdict(x) for x in residual.decisions],
            },
        })
    return {
        "kind": "deterministic-policy-demonstration",
        "model_invoked": False,
        "synthetic_data_only": True,
        "assumption": "Attacker can read the published review; the adversarial actions are supplied, not generated by a model.",
        "cases": cases,
        "limit": "Scoped reads block this credential path, but allowlisted source data can still leave through the permitted output.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit reproducible results and metadata-only decision traces")
    args = parser.parse_args()
    result = run_comparison()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print("Deterministic policy demo — synthetic data; no model or network calls.\n")
    print(f"{'Policy':<10} {'Legitimate task':<20} {'Protected canary leaked':<27} {'Canary in allowed source leaked'}")
    for case in result["cases"]:
        print(f"{case['policy']:<10} {str(case['legitimate_task_completed']):<20} "
              f"{str(case['protected_canary_disclosed']):<27} {case['allowed_source_canary_disclosed']}")
    print("\n" + result["limit"])
    print("These booleans describe fixed cases, not model success rates or empirical security coverage.")


if __name__ == "__main__":
    main()
