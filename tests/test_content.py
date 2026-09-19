from copy import deepcopy
import json
from pathlib import Path
import unittest

from killchain_lab.validate import validate_crosswalk, validate_repository, validate_scenario

ROOT = Path(__file__).resolve().parents[1]


class ContentIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.identifiers = json.loads((ROOT / "data/atlas-2026.01-identifiers.json").read_text())
        cls.crosswalk = json.loads((ROOT / "data/atlas-crosswalk.json").read_text())
        cls.scenario = json.loads((ROOT / "data/scenarios/01-code-review.json").read_text())

    def test_repository_links_identifiers_and_scenarios(self):
        self.assertEqual(validate_repository(), {"scenarios": 6, "tactics": 16, "references": 19})

    def test_incorrect_tactic_name_is_rejected(self):
        data = deepcopy(self.crosswalk)
        data["mappings"][0]["tactic_name"] = "Persistence"
        with self.assertRaisesRegex(ValueError, "name/id mismatch"):
            validate_crosswalk(data, self.identifiers)

    def test_duplicate_tactic_is_rejected(self):
        data = deepcopy(self.crosswalk)
        data["mappings"].append(data["mappings"][0])
        with self.assertRaisesRegex(ValueError, "duplicate tactic"):
            validate_crosswalk(data, self.identifiers)

    def test_release_drift_is_rejected(self):
        data = deepcopy(self.crosswalk)
        data["source_release"] = "unverified"
        with self.assertRaisesRegex(ValueError, "release mismatch"):
            validate_crosswalk(data, self.identifiers)

    def test_existing_authority_cannot_be_relabelled_as_escalation(self):
        data = deepcopy(self.scenario)
        data["checkpoints"][3]["status"] = "illustrated"
        with self.assertRaisesRegex(ValueError, "contradicts authority"):
            validate_scenario(data)

    def test_script_cannot_be_relabelled_as_model_evaluation(self):
        data = deepcopy(self.scenario)
        data["model_evaluated"] = True
        with self.assertRaisesRegex(ValueError, "no model evaluation"):
            validate_scenario(data)

    def test_attacker_visible_output_is_required(self):
        data = deepcopy(self.scenario)
        del data["threat_model"]["output"]
        with self.assertRaisesRegex(ValueError, "attacker-visible output"):
            validate_scenario(data)

    def test_unknown_stage_is_rejected(self):
        data = deepcopy(self.scenario)
        data["checkpoints"][0]["stage"] = "unmapped-stage"
        with self.assertRaisesRegex(ValueError, "order/id mismatch"):
            validate_scenario(data)


if __name__ == "__main__":
    unittest.main()
