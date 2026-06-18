"""Tests for the Keel scaffolder and interview engine.

Run with: python -m unittest discover -s keel/tests
"""

import io
import json
import os
import sys
import tempfile
import unittest

# Make the keel package importable when running from the repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from keel import interview, scaffold, templates  # noqa: E402


def _load(name):
    path = os.path.join(os.path.dirname(__file__), "..", "examples", name)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


class ScaffoldTests(unittest.TestCase):
    def test_operator_workspace_has_expected_files(self):
        answers = _load("austin.operator.json")
        with tempfile.TemporaryDirectory() as tmp:
            written = scaffold.write_workspace(answers, tmp)
            rels = {os.path.relpath(p, tmp) for p in written}
            self.assertIn(os.path.join("00_Global_Context", "START_HERE.md"), rels)
            self.assertIn(
                os.path.join("00_Global_Context", "WHO_I_AM_AND_HOW_I_WORK.md"), rels
            )
            self.assertIn(os.path.join("00_Global_Context", "BOOTSTRAP_PROMPT.md"), rels)
            self.assertIn(os.path.join("Coaching", "CHAT_SUMMARY.md"), rels)
            self.assertIn(os.path.join("skills", "data-dump", "SKILL.md"), rels)

    def test_business_uses_who_we_are_and_voice(self):
        answers = _load("local-business.json")
        with tempfile.TemporaryDirectory() as tmp:
            scaffold.write_workspace(answers, tmp)
            who = os.path.join(tmp, "00_Global_Context", "WHO_WE_ARE.md")
            self.assertTrue(os.path.exists(who))
            with open(who, encoding="utf-8") as handle:
                body = handle.read()
            self.assertIn("Our voice", body)
            self.assertIn("Riverside Family Dental", body)

    def test_no_em_dashes_in_generated_output(self):
        answers = _load("local-business.json")
        for _rel, content in scaffold.build_files(answers):
            self.assertNotIn("—", content, "generated output must avoid em dashes")

    def test_refuses_overwrite_without_force(self):
        answers = _load("austin.operator.json")
        with tempfile.TemporaryDirectory() as tmp:
            scaffold.write_workspace(answers, tmp)
            with self.assertRaises(FileExistsError):
                scaffold.write_workspace(answers, tmp)
            # force=True succeeds
            scaffold.write_workspace(answers, tmp, force=True)

    def test_bootstrap_references_identity_file(self):
        answers = _load("austin.operator.json")
        prompt = templates.bootstrap_prompt(answers, ["Coaching"])
        self.assertIn("WHO_I_AM_AND_HOW_I_WORK.md", prompt)
        self.assertIn("Coaching", prompt)


class InterviewTests(unittest.TestCase):
    def test_interview_preset_skips_prompts(self):
        captured = []
        answers = interview.run_interview(
            "operator",
            input_fn=lambda _p: self.fail("should not prompt when preset is complete"),
            output_fn=captured.append,
            preset={
                "name": "Test",
                "role": "Role",
                "summary": "Summary",
                "how_you_work": "a; b",
                "principles": "p1; p2",
                "output_standard": "",
                "goals": "g1",
                "tools": "t1, t2",
                "projects": "Alpha, Beta",
            },
        )
        self.assertEqual(answers["name"], "Test")
        self.assertEqual(answers["profile"], "operator")

    def test_interview_collects_from_input(self):
        responses = iter(["Jane", "Founder", "I build things", "fast", "", "", "", "", ""])
        answers = interview.run_interview(
            "operator",
            input_fn=lambda _p: next(responses),
            output_fn=lambda _m: None,
        )
        self.assertEqual(answers["name"], "Jane")
        self.assertEqual(answers["role"], "Founder")


if __name__ == "__main__":
    unittest.main()
