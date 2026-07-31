import tempfile
import unittest
from pathlib import Path

from scripts.validate_skills import load_profiles, validate_skill


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PROFILES_PATH = REPOSITORY_ROOT / "config" / "frontmatter-compatibility.yml"
FIXTURES = REPOSITORY_ROOT / "tests" / "fixtures" / "harness-frontmatter"


class SkillValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles = load_profiles(PROFILES_PATH)

    def test_repository_skills_follow_portable_specification(self):
        skill_dirs = sorted(path.parent for path in (REPOSITORY_ROOT / "skills").glob("*/SKILL.md"))
        self.assertTrue(skill_dirs)
        for skill_dir in skill_dirs:
            with self.subTest(skill=skill_dir.name):
                self.assertEqual([], validate_skill(skill_dir, profiles=self.profiles))

    def test_rejects_name_that_does_not_match_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "correct-name"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: wrong-name\ndescription: Test validation.\n---\n",
                encoding="utf-8",
            )
            errors = validate_skill(skill_dir, profiles=self.profiles)
        self.assertTrue(any("must match parent directory" in error for error in errors))

    def test_vendor_fields_are_rejected_without_compatibility_profile(self):
        skill_dir = FIXTURES / "copilot" / "copilot-extension"
        errors = validate_skill(skill_dir, profiles=self.profiles)
        self.assertTrue(any("argument-hint" in error for error in errors))

    def test_documented_vendor_frontmatter_profiles(self):
        fixtures = {
            "claude-code": FIXTURES / "claude" / "claude-extension",
            "github-copilot": FIXTURES / "copilot" / "copilot-extension",
            "factory-droid": FIXTURES / "factory" / "factory-extension",
            "qwen-code": FIXTURES / "qwen" / "qwen-extension",
            "kimi-code": FIXTURES / "kimi" / "kimi-extension",
            "openhands": FIXTURES / "openhands" / "openhands-extension",
        }
        for profile, skill_dir in fixtures.items():
            with self.subTest(profile=profile):
                self.assertEqual(
                    [],
                    validate_skill(
                        skill_dir,
                        compatibility=profile,
                        profiles=self.profiles,
                    ),
                )


if __name__ == "__main__":
    unittest.main()
