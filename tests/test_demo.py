import json
from pathlib import Path
import unittest
from unittest.mock import patch

from killchain_lab.demo import (
    Denied, Policy, SOURCE, SECRET, SYNTHETIC_SECRET, REVIEW_DESTINATION,
    ToolRuntime, attempt_disclosure, benign_review, fixture, policies, run_comparison,
)


class PolicyDemoTests(unittest.TestCase):
    def test_benign_task_works_under_both_policies(self):
        for policy in policies():
            with self.subTest(policy=policy.name):
                runtime = ToolRuntime(policy, fixture())
                self.assertTrue(benign_review(runtime))
                self.assertEqual(runtime.published, [(REVIEW_DESTINATION, "Review: add(a, b) returns a + b.")])

    def test_broad_access_discloses_protected_canary(self):
        runtime = ToolRuntime(policies()[0], fixture())
        self.assertTrue(attempt_disclosure(runtime, SECRET))
        self.assertIn(SYNTHETIC_SECRET, runtime.published[0][1])

    def test_scoped_access_blocks_read_before_publish(self):
        runtime = ToolRuntime(policies()[1], fixture())
        self.assertFalse(attempt_disclosure(runtime, SECRET))
        self.assertEqual(runtime.published, [])
        self.assertEqual([(d.action, d.allowed) for d in runtime.decisions], [("read", False)])

    def test_allowlisted_source_can_still_leak(self):
        runtime = ToolRuntime(policies()[1], fixture(canary_in_source=True))
        self.assertTrue(attempt_disclosure(runtime, SOURCE))

    def test_destination_scope_is_enforced_independently(self):
        runtime = ToolRuntime(policies()[0], fixture())
        with self.assertRaises(Denied):
            runtime.publish("unapproved-recipient", "synthetic report")
        self.assertEqual(runtime.published, [])

    def test_unscoped_path_aliases_do_not_expand_permissions(self):
        runtime = ToolRuntime(policies()[1], fixture())
        for path in ("../.env", "/workspace/src/../.env", "/workspace/src-other/review_target.py",
                     "/workspace/src//review_target.py", "/workspace/src/./review_target.py",
                     "/workspace/src/review_target.py/", "C:\\workspace\\src\\review_target.py",
                     "/workspace/src/\0secret", "/etc/passwd", "/workspace/src/%2e%2e/.env"):
            with self.subTest(path=path), self.assertRaises(Denied):
                runtime.read(path)

    def test_unknown_actions_are_denied(self):
        for policy in policies():
            self.assertFalse(policy.permits("shell", SOURCE))
            self.assertFalse(policy.permits("write", SOURCE))

    def test_allowlist_does_not_create_a_resource(self):
        runtime = ToolRuntime(Policy("missing", frozenset({SOURCE}), frozenset()), {})
        with self.assertRaises(FileNotFoundError):
            runtime.read(SOURCE)

    def test_demo_uses_no_host_file_or_network_io(self):
        with patch("builtins.open", side_effect=AssertionError("host file access")), \
             patch("socket.socket", side_effect=AssertionError("network access")):
            run_comparison()

    def test_results_are_repeatable_and_do_not_contain_canary_contents(self):
        first = run_comparison()
        self.assertEqual(first, run_comparison())
        self.assertNotIn(SYNTHETIC_SECRET, json.dumps(first))
        self.assertFalse(first["model_invoked"])

    def test_checked_in_results_reproduce_exactly(self):
        path = Path(__file__).resolve().parents[1] / "examples/expected-results.json"
        self.assertEqual(json.loads(path.read_text()), run_comparison())


if __name__ == "__main__":
    unittest.main()
