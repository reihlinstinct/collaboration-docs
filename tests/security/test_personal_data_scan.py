"""Regression tests for scripts/security/personal_data_scan.sh.

Exact 40-hex action pins (owner/action@<40 hex>) on `uses:` lines are exempt
from the numeric checks only, stripped per token: findings of other kinds on
the same line, and digit runs anywhere else, must still be reported.
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts/security/personal_data_scan.sh'
SHA = 'ossf/scorecard-action@fa7117db83c52d787ae5a89f350999701505d78e'
PIN_4_39_1 = 'github/codeql-action/upload-sarif@9b3254085494b55a0f7c4c2b3d2d52cc712ce370'


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

    def test_pinned_upload_sarif_sha_with_digit_run_passes(self):
        # Regression for #31: the 4.39.1 pin contains the 10-digit run 3254085494.
        result = run_scan({'.github/workflows/scorecard.yml': f'- uses: {PIN_4_39_1} # v4\n'})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pin_outside_uses_line_is_flagged(self):
        result = run_scan({'docs/x.md': f'see pin {PIN_4_39_1} here\n'})
        self.assertEqual(result.returncode, 1)
        self.assertIn('long ID-like number', result.stdout)

    def test_non_hex_40_char_pin_is_flagged(self):
        bad = 'owner/action@' + '9b3254085494b55a0f7c4c2b3d2d52cc712ce37g'
        result = run_scan({'.github/workflows/w.yml': f'- uses: {bad}\n'})
        self.assertEqual(result.returncode, 1)
        self.assertIn('long ID-like number', result.stdout)

    def test_real_id_next_to_pin_on_uses_line_is_flagged(self):
        result = run_scan({'.github/workflows/scorecard.yml':
                           f'- uses: {PIN_4_39_1} # id 123456789\n'})
        self.assertEqual(result.returncode, 1)
        self.assertIn('long ID-like number', result.stdout)

    def test_email_on_scorecard_line_is_flagged(self):
        result = run_scan({'.github/workflows/scorecard.yml':
                           f'- uses: {SHA} # contact someone@real-example.com\n'})
        self.assertEqual(result.returncode, 1)
        self.assertIn('email address', result.stdout)

    def test_token_on_scorecard_line_is_flagged(self):
        result = run_scan({'.github/workflows/scorecard.yml':
                           f'- uses: {SHA} # ' + 'ghp' + '_' + 'a' * 20 + '\n'})
        self.assertEqual(result.returncode, 1)
        self.assertIn('token', result.stdout)

    def test_classic_installation_token_flagged_without_echo(self):
        token = 'ghs' + '_' + 'a' * 36
        result = run_scan({'docs/x.md': f'token: {token}\n'})
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('token', result.stdout)
        self.assertNotIn(token, result.stdout)

    def test_stateless_installation_token_flagged_without_echo(self):
        token = 'ghs' + '_12345_' + 'A' * 100 + '.' + 'B' * 300 + '.' + 'C' * 108
        result = run_scan({'docs/x.md': f'token: {token}\n'})
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('token', result.stdout)
        self.assertNotIn(token, result.stdout)

    def test_over_520_char_stateless_token_flagged(self):
        token = 'ghs' + '_12345_' + 'A' * 100 + '.' + 'B' * 300 + '.' + 'C' * 200
        result = run_scan({'docs/x.md': f'token: {token}\n'})
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertNotIn(token, result.stdout)

    def test_short_token_fragment_passes(self):
        result = run_scan({'docs/x.md': 'prefix ghs_12345_short suffix\n'})
        self.assertEqual(result.returncode, 0, result.stdout)

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
