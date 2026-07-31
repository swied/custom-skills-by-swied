import unittest
from pathlib import Path

from scripts.audit_harness_docs import (
    audit_sources,
    document_contains_path,
    load_manifest,
    load_sources,
    validate_source_coverage,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "installers" / "harnesses.tsv"
SOURCES_PATH = REPOSITORY_ROOT / "config" / "harness-docs.tsv"


class HarnessDocumentationAuditTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_manifest(MANIFEST_PATH)
        self.sources = load_sources(SOURCES_PATH)

    def test_every_installer_alias_has_one_documentation_source(self):
        self.assertEqual([], validate_source_coverage(self.manifest, self.sources))

    def test_path_detection_handles_html_and_home_variants(self):
        self.assertTrue(
            document_contains_path("<code>$HOME/.agents/skills/</code>", ".agents/skills")
        )
        self.assertTrue(document_contains_path("Use ~/.qwen/skills/.", ".qwen/skills"))
        self.assertFalse(document_contains_path("Use .agents/skills in this project.", ".agents/skills"))

    def test_audit_reports_only_sources_missing_global_path(self):
        bad_url = self.sources[0].documentation_url

        def fetcher(url, _timeout):
            if url == bad_url:
                return "Project skills live in .agents/skills."
            source = next(item for item in self.sources if item.documentation_url == url)
            relative_path = self.manifest[source.group][0]
            return f"Global skills live in ~/{relative_path}/."

        errors = audit_sources(self.manifest, self.sources, timeout=1, fetcher=fetcher)
        self.assertEqual(1, len(errors))
        self.assertIn(self.sources[0].product, errors[0])


if __name__ == "__main__":
    unittest.main()
