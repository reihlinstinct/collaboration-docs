"""Regression tests for scripts/security/personal_data_scan.sh.

The pinned ossf/scorecard-action SHA is exempt from the numeric checks only,
stripped per token: findings of other kinds on the same line must still be
reported (review fix for the previous line-wide exclusion).
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts/security/personal_data_scan.sh'
SHA = 'ossf/scorecard-action@fa7117db83c52d787ae5a89f350999701505d78e'


def run_scan(files):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
        for name, content in files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding='utf-8')
        subprocess.run(['git', 'add', '-A'], cwd=root, check=True)
        return subprocess.run(['bash', str(SCRIPT)], cwd=root,
                              capture_output=True, text=True)


class PersonalDataScanTest(unittest.TestCase):
    def test_pinned_scorecard_sha_alone_passes(self):
        result = run_scan({'.github/workflows/scorecard.yml': f'- uses: {SHA} # v2.5.0\n'})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_email_on_scorecard_line_is_flagged(self):
        result = run_scan({'.github/workflows/scorecard.yml':
                           f'- uses: {SHA} # contact someone@real-example.com\n'})
        self.assertEqual(result.returncode, 1)
        self.assertIn('email address', result.stdout)

    def test_token_on_scorecard_line_is_flagged(self):
        result = run_scan({'.github/workflows/scorecard.yml':
                           f'- uses: {SHA} # ghp_abcdefghijklmnop\n'})
        self.assertEqual(result.returncode, 1)
        self.assertIn('token', result.stdout)

    def test_other_long_number_on_scorecard_line_is_flagged(self):
        result = run_scan({'.github/workflows/scorecard.yml':
                           f'- uses: {SHA} # id 123456789\n'})
        self.assertEqual(result.returncode, 1)
        self.assertIn('long ID-like number', result.stdout)

    def test_private_key_is_flagged(self):
        result = run_scan({'docs/x.md': 'BEGIN RSA PRIVATE KEY\n'})
        self.assertEqual(result.returncode, 1)
        self.assertIn('private key', result.stdout)


if __name__ == '__main__':
    unittest.main()
