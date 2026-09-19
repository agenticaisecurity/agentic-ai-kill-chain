"""Offline content-integrity checks; these do not validate attack efficacy or mappings."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGES = ("recon", "inject", "hijack", "escalate", "exfiltrate", "persist")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def nonempty(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_scenario(data: dict) -> None:
    require(isinstance(data, dict), "scenario must be an object")
    require(data.get("schema_version") == "1.0", "unknown scenario version")
    require(nonempty(data.get("id")) and re.fullmatch(r"[a-z][a-z0-9-]*", data["id"]), "invalid scenario id")
    require(nonempty(data.get("title")), "missing title")
    require(data.get("evidence_kind") == "scripted-illustration", "do not relabel scripts as experimental evidence")
    require(data.get("model_evaluated") is False, "no model evaluation was performed")
    threat = data.get("threat_model")
    require(isinstance(threat, dict), "missing threat model")
    for key in ("attacker_control", "victim_access"):
        require(isinstance(threat.get(key), list) and bool(threat[key]) and all(nonempty(v) for v in threat[key]), f"missing {key}")
    require(nonempty(threat.get("output")), "attacker-visible output must be explicit")
    require(threat.get("authority") in ("existing-permission-misuse", "confused-deputy", "denied-at-access-boundary"), "unknown authority classification")
    points = data.get("checkpoints")
    require(isinstance(points, list) and len(points) == 6, "six checkpoints required")
    for i, (point, stage) in enumerate(zip(points, STAGES), 1):
        require(isinstance(point, dict), "checkpoint must be an object")
        require(point.get("position") == i and point.get("stage") == stage, "checkpoint order/id mismatch")
        require(nonempty(point.get("label")), "missing checkpoint label")
        lines = point.get("narration")
        require(isinstance(lines, list) and bool(lines) and all(isinstance(v, str) for v in lines), "missing static narration")
        expected = "illustrated"
        if threat["authority"] == "existing-permission-misuse" and stage == "escalate":
            expected = "skipped-existing-authority"
        elif threat["authority"] == "denied-at-access-boundary" and i >= 4:
            expected = "denied"
        require(point.get("status") == expected, "checkpoint status contradicts authority classification")
    require(data.get("implementation") in ("documentation-only", "narrow-policy-demo-only"), "invalid implementation scope")
    require(isinstance(data.get("limitations"), list) and bool(data["limitations"]), "missing limitations")


def validate_crosswalk(data: dict, identifiers: dict) -> None:
    require(data.get("source_release") == identifiers["source"]["release"] == "2026.01", "ATLAS release mismatch")
    require(data.get("endorsed_by_mitre") is False, "no institutional endorsement is claimed")
    require(data.get("relationship") == "illustrative-author-association-not-taxonomy-equivalence", "mapping scope missing")
    mappings = data.get("mappings")
    require(isinstance(mappings, list), "missing mappings")
    seen = set()
    for mapping in mappings:
        tactic = mapping.get("tactic_id")
        require(tactic in identifiers["tactics"], f"unknown tactic: {tactic}")
        require(tactic not in seen, f"duplicate tactic: {tactic}")
        seen.add(tactic)
        require(mapping.get("tactic_name") == identifiers["tactics"][tactic], f"name/id mismatch: {tactic}")
        stages = mapping.get("stages")
        require(isinstance(stages, list) and bool(stages) and len(stages) == len(set(stages)) and all(x in STAGES for x in stages), "invalid mapped stages")
        require(nonempty(mapping.get("rationale")) and nonempty(mapping.get("caveat")), "mapping requires rationale and caveat")
    require(seen == set(identifiers["tactics"]), "crosswalk must account for every tactic in the pinned identifier extract")


def validate_article(article: str, identifiers: dict, refs: list[dict]) -> None:
    """Check pinned IDs and numbered citation bindings, not semantic truth."""
    known = set(identifiers["tactics"]) | set(identifiers["techniques"])
    mentioned = set(re.findall(r"\bAML\.T[A-Za-z0-9]*(?:\.[A-Za-z0-9]+)*", article))
    for identifier in sorted(mentioned):
        require(identifier in known, f"article ATLAS identifier absent from pinned extract: {identifier}")
    require([x["id"] for x in refs] == list(range(1, len(refs) + 1)), "reference ids must be sequential and unique")
    for ref in refs:
        require(nonempty(ref.get("citation")), f"reference {ref['id']} missing citation identity")
        require(isinstance(ref.get("url"), str) and ref["url"].startswith("https://"), "reference URL must use HTTPS")
    entries = re.findall(r"^\[(\d+)\] \[([^\]\n]+)\]\((https://[^\s]+)\)$", article, re.MULTILINE)
    expected = [(str(ref["id"]), ref["citation"], ref["url"]) for ref in refs]
    require(entries == expected, "article numbered citation identity/URL mismatch")


def validate_repository(root: Path = ROOT) -> dict[str, int]:
    load = lambda path: json.loads((root / path).read_text(encoding="utf-8"))
    identifiers = load("data/atlas-2026.01-identifiers.json")
    require(re.fullmatch(r"[0-9a-f]{64}", identifiers["source"]["sha256"]) is not None, "invalid source fingerprint")
    validate_crosswalk(load("data/atlas-crosswalk.json"), identifiers)
    scenarios = list((root / "data/scenarios").glob("*.json"))
    require(bool(scenarios), "no scenario definitions")
    seen = set()
    for path in scenarios:
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_scenario(data)
        require(data["id"] not in seen, "duplicate scenario id")
        seen.add(data["id"])
    refs = load("data/references.json")["references"]
    article = (root / "docs/article.md").read_text(encoding="utf-8")
    validate_article(article, identifiers, refs)
    for relative in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", article):
        target = (root / "docs" / relative).resolve()
        require(target.is_relative_to((root / "docs").resolve()) and target.is_file(), "missing or out-of-tree article image")
    return {"scenarios": len(scenarios), "tactics": len(identifiers["tactics"]), "references": len(refs)}


def main() -> None:
    try:
        counts = validate_repository()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Content check failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    print("Content checks passed: " + ", ".join(f"{v} {k}" for k, v in counts.items()))
    print("Checks establish internal consistency, not empirical validity or institutional endorsement.")


if __name__ == "__main__":
    main()
