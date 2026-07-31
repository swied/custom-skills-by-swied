import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY_ROOT / "skills" / "swied-resume-consultant"


class ResumeConsultantSkillTests(unittest.TestCase):
    def test_required_skill_resources_exist(self):
        expected_paths = [
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "agents" / "openai.yaml",
            SKILL_ROOT / "references" / "interview-playbook.md",
            SKILL_ROOT / "references" / "research-and-connectors.md",
            SKILL_ROOT / "templates" / "my-career-profile.md",
            SKILL_ROOT / "templates" / "dr-bailey-report.md",
            SKILL_ROOT / "templates" / "new-resume.md",
        ]

        for path in expected_paths:
            with self.subTest(path=path):
                self.assertTrue(path.is_file())

    def test_skill_preserves_required_deliverable_names_and_order(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        profile_index = text.index("`my-career-profile.md`")
        report_index = text.index("`dr-bailey-report.md`")
        resume_index = text.index("`new-resume.md`")

        self.assertLess(profile_index, report_index)
        self.assertLess(report_index, resume_index)
        self.assertIn("Only after those two documents are settled", text)

    def test_resume_template_is_single_column(self):
        text = (SKILL_ROOT / "templates" / "new-resume.md").read_text(
            encoding="utf-8"
        )

        self.assertFalse(any(line.startswith("|") for line in text.splitlines()))
        for heading in (
            "## Professional Summary",
            "## Core Skills",
            "## Professional Experience",
            "## Education",
        ):
            self.assertIn(heading, text)


if __name__ == "__main__":
    unittest.main()
