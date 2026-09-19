from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from killchain_lab.validate import validate_article, validate_crosswalk, validate_repository, validate_scenario

ROOT = Path(__file__).resolve().parents[1]


class ContentIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.identifiers = json.loads((ROOT / "data/atlas-2026.01-identifiers.json").read_text())
        cls.crosswalk = json.loads((ROOT / "data/atlas-crosswalk.json").read_text())
        cls.scenario = json.loads((ROOT / "data/scenarios/01-code-review.json").read_text())

    def test_repository_validator_checks_article_prose(self):
        original_read = Path.read_text
        def changed_article(path, *args, **kwargs):
            text = original_read(path, *args, **kwargs)
            return text.replace("AML.T0051", "AML.T9999") if path == ROOT / "docs/article.md" else text
        with patch.object(Path, "read_text", changed_article):
            with self.assertRaisesRegex(ValueError, "absent from pinned extract"):
                validate_repository()

    def test_unknown_article_identifiers_are_rejected(self):
        article = (ROOT / "docs/article.md").read_text()
        refs = json.loads((ROOT / "data/references.json").read_text())["references"]
        for original, replacement in (("AML.T0051", "AML.T9999"),
                                      ("AML.T0080.000", "AML.T0080.999"),
                                      ("AML.TA0000", "AML.TA9999")):
            with self.subTest(replacement=replacement):
                self.assertIn(original, article)
                with self.assertRaisesRegex(ValueError, "absent from pinned extract"):
                    validate_article(article.replace(original, replacement), self.identifiers, refs)

    def test_article_reference_url_swap_is_rejected(self):
        article = (ROOT / "docs/article.md").read_text()
        refs = json.loads((ROOT / "data/references.json").read_text())["references"]
        first, second = refs[0]["url"], refs[1]["url"]
        mutated = article.replace(first, "SWAP_URL").replace(second, first).replace("SWAP_URL", second)
        self.assertIn(first, mutated)
        self.assertIn(second, mutated)
        with self.assertRaisesRegex(ValueError, "citation identity/URL mismatch"):
            validate_article(mutated, self.identifiers, refs)

    def test_article_reference_identity_swap_is_rejected(self):
        article = (ROOT / "docs/article.md").read_text()
        refs = json.loads((ROOT / "data/references.json").read_text())["references"]
        first, second = refs[0]["citation"], refs[1]["citation"]
        mutated = article.replace(first, "SWAP_TITLE").replace(second, first).replace("SWAP_TITLE", second)
        with self.assertRaisesRegex(ValueError, "citation identity/URL mismatch"):
            validate_article(mutated, self.identifiers, refs)

    def test_missing_or_duplicate_article_reference_is_rejected(self):
        article = (ROOT / "docs/article.md").read_text()
        refs = json.loads((ROOT / "data/references.json").read_text())["references"]
        ref = refs[0]
        entry = f"[{ref['id']}] [{ref['citation']}]({ref['url']})"
        for mutated in (article.replace(entry, ""), article + "\n" + entry + "\n"):
            with self.subTest(article_length=len(mutated)):
                with self.assertRaisesRegex(ValueError, "citation identity/URL mismatch"):
                    validate_article(mutated, self.identifiers, refs)

    def test_reference_metadata_change_is_rejected(self):
        article = (ROOT / "docs/article.md").read_text()
        refs = json.loads((ROOT / "data/references.json").read_text())["references"]
        refs[0]["url"] = refs[1]["url"]
        with self.assertRaisesRegex(ValueError, "citation identity/URL mismatch"):
            validate_article(article, self.identifiers, refs)

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
