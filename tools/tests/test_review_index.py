"""Publication boundaries tested against real, disposable Git repositories."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_index import build, metadata


class ReviewIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = self.root / 'library' / 'registry.yml'
        self.registry.parent.mkdir()
        rows = []
        for name, role in [('visible', 'showcase'), ('private-example', 'hidden')]:
            repo = self.root / name
            repo.mkdir()
            (repo / 'README.md').write_text('# Source\n', encoding='utf-8')
            for stamp in ['20261105T0856Z', '20261105T0900Z']:
                bundle = repo / '.review' / ('CODE_REVIEW_Agent_v1_' + stamp)
                bundle.mkdir(parents=True)
                (bundle / '00_INDEX.md').write_text('**Reviewer:** Agent\n', encoding='utf-8')
                (bundle / '01_EXECUTIVE_SUMMARY.md').write_text('# Executive Summary\n\n**Overall Grade:** B+\n\n[Root](README.md) and [Detail](02_DETAIL.md).\n\n| Area | Grade |\n|---|---|\n| Notes | B |\n', encoding='utf-8')
                (bundle / '02_DETAIL.md').write_text('Details\n', encoding='utf-8')
            (repo / '.review' / '2026-10-23_confirmation.md').write_text('Confirmed\n', encoding='utf-8')
            self.commit(repo)
            rows.append({'project': name, 'github': 'owner/' + name, 'status': 'active', 'presentation_role': role})
        self.registry.write_text(yaml.safe_dump({'projects': rows}), encoding='utf-8')
        self.commit(self.registry.parent)
        self.output = self.root / 'output'

    @staticmethod
    def commit(repo):
        for args in [('init', '-q'), ('add', '.'), ('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Fixture'), ('update-ref', 'refs/remotes/origin/main', 'HEAD')]:
            subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True)

    def build(self, check=False):
        return build(self.root, self.registry, self.output, '2026-10-01', check)

    def test_parallel_reviews_focused_records_pins_and_isolated_output(self):
        sentinel = self.root / 'portfolio-landing' / 'reviews.html'
        sentinel.parent.mkdir()
        sentinel.write_bytes(b'Other agent output')
        result = self.build()
        self.assertEqual(result['reviewProjects'], ['visible'])
        self.assertEqual(len(result['reviewBundles']), 2)
        self.assertEqual(len(result['focusedReviews']), 1)
        document = (self.output / 'public-index.html').read_text(encoding='utf-8')
        self.assertNotIn('private-example', document)
        self.assertNotIn('/main/', document)
        self.assertIn('/README.md', document)
        self.assertIn('/02_DETAIL.md', document)
        self.assertIn('id="review-visible"', document)
        self.assertEqual(sentinel.read_bytes(), b'Other agent output')
        self.build(check=True)

    def test_nonwriting_check_detects_corruption(self):
        self.build()
        path = self.output / 'index.html'
        path.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Stale review output'):
            self.build(check=True)
        self.assertEqual(path.read_bytes(), b'changed')

    def test_unpublished_review_is_internal_only(self):
        source = self.root / 'visible/.review/CODE_REVIEW_Agent_v1_20261105T0900Z/01_EXECUTIVE_SUMMARY.md'
        source.write_text('UNPUBLISHED CONTENT\n', encoding='utf-8')
        result = self.build()
        self.assertEqual(len(result['reviewBundles']), 1)
        self.assertIn('UNPUBLISHED CONTENT', (self.output / 'index.html').read_text(encoding='utf-8'))
        self.assertNotIn('UNPUBLISHED CONTENT', (self.output / 'public-index.html').read_text(encoding='utf-8'))

    def test_hidden_summary_link_cannot_enter_public_export(self):
        source = self.root / 'visible/.review/CODE_REVIEW_Agent_v1_20261105T0900Z/01_EXECUTIVE_SUMMARY.md'
        source.write_text('[Secret](../../../private-example/README.md)\n', encoding='utf-8')
        # Publish the hostile reference so it cannot be rejected merely as an uncommitted edit.
        self.commit(self.root / 'visible')
        with self.assertRaisesRegex(ValueError, 'Hidden or unpublished'):
            self.build()

    def test_unpublished_linked_source_is_rejected(self):
        repo = self.root / 'visible'
        source = repo / '.review/CODE_REVIEW_Agent_v1_20261105T0900Z/01_EXECUTIVE_SUMMARY.md'
        source.write_text('[Draft](draft.md)\n', encoding='utf-8')
        self.commit(repo)
        (repo / 'draft.md').write_text('Local only\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Unpublished linked source'):
            self.build()

    def test_explicit_grade_only_and_html_escaping(self):
        self.assertEqual(metadata('', '| Area | Grade | Notes |', '20261105T0900Z')['grade'], 'Not assigned')
        self.assertEqual(metadata('', '**Overall Grade:** B+\n', '20261105T0900Z')['grade'], 'B+')
        source = self.root / 'visible/.review/CODE_REVIEW_Agent_v1_20261105T0900Z/01_EXECUTIVE_SUMMARY.md'
        source.write_text('<script>alert(1)</script>\n', encoding='utf-8')
        self.commit(self.root / 'visible')
        self.build()
        document = (self.output / 'public-index.html').read_text(encoding='utf-8')
        self.assertNotIn('<script>', document)
        self.assertIn('&lt;script&gt;', document)


if __name__ == '__main__':
    unittest.main()
