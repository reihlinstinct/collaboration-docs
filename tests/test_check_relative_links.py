"""Unit tests for tools/check_relative_links.py using synthetic temporary repos."""

import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))

import check_relative_links as checker  # noqa: E402


def write(root, rel, text):
    path = Path(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return path


class TempRepoCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = checker.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def problems_for(self, rel_doc):
        return checker.check_document(self.root, rel_doc)


class StandardLinkTests(TempRepoCase):
    def test_valid_local_file_link_passes(self):
        write(self.root, 'target.md', '# t\n')
        write(self.root, 'doc.md', 'See [t](target.md).\n')
        self.assertEqual(self.problems_for('doc.md'), [])

    def test_missing_local_target_reports_line(self):
        write(self.root, 'doc.md', 'ok\n[gone](missing.md)\n')
        problems = self.problems_for('doc.md')
        self.assertEqual(len(problems), 1)
        self.assertIn('doc.md:2:', problems[0])
        self.assertIn("'missing.md'", problems[0])

    def test_directory_target_is_valid(self):
        Path(self.root, 'guide').mkdir()
        write(self.root, 'doc.md', '[dir](guide)\n')
        self.assertEqual(self.problems_for('doc.md'), [])

    def test_image_link_is_checked(self):
        write(self.root, 'doc.md', '![pic](img/none.png)\n')
        self.assertEqual(len(self.problems_for('doc.md')), 1)

    def test_link_with_title_is_checked(self):
        write(self.root, 'a.md', 'x\n')
        write(self.root, 'doc.md', '[a](a.md "A title") [b](b.md \'x\')\n')
        problems = self.problems_for('doc.md')
        self.assertEqual(len(problems), 1)
        self.assertIn("'b.md'", problems[0])

    def test_percent_encoded_bare_target_is_decoded(self):
        write(self.root, 'my file.md', 'x\n')
        write(self.root, 'doc.md', '[f](my%20file.md)\n')
        self.assertEqual(self.problems_for('doc.md'), [])

    def test_nested_relative_links_resolve_against_document_directory(self):
        write(self.root, 'docs/guide/target.md', 'x\n')
        write(self.root, 'docs/guide/page.md', '[up](../../README.md)\n[sib](target.md)\n')
        write(self.root, 'docs/README.md', '[down](guide/target.md)\n')
        self.assertEqual(
            self.problems_for('docs/guide/page.md'),
            ["docs/guide/page.md:1: broken relative link: '../../README.md'"],
        )
        self.assertEqual(self.problems_for('docs/README.md'), [])
        write(self.root, 'README.md', 'root\n')
        self.assertEqual(self.problems_for('docs/guide/page.md'), [])


class AngleBracketTests(TempRepoCase):
    def test_angle_bracket_target_with_spaces_resolves(self):
        write(self.root, 'my notes/plan.md', 'x\n')
        write(self.root, 'doc.md', '[plan](<my notes/plan.md>)\n')
        self.assertEqual(self.problems_for('doc.md'), [])

    def test_angle_bracket_target_with_spaces_missing_is_reported(self):
        write(self.root, 'doc.md', '[plan](<my notes/plan.md>)\n')
        problems = self.problems_for('doc.md')
        self.assertEqual(len(problems), 1)
        self.assertIn("'my notes/plan.md'", problems[0])

    def test_angle_bracket_percent_escape_resolves_to_space_filename(self):
        write(self.root, 'a b.md', 'x\n')
        write(self.root, 'doc.md', '[x](<a%20b.md>)\n')
        self.assertEqual(self.problems_for('doc.md'), [])

    def test_angle_bracket_percent_escape_missing_target_is_reported(self):
        write(self.root, 'doc.md', '[x](<a%20b.md>)\n')
        self.assertEqual(
            self.problems_for('doc.md'),
            ["doc.md:1: broken relative link: 'a%20b.md'"],
        )

    def test_angle_bracket_literal_percent_filename_is_not_linkable(self):
        # Documented limit: a valid percent escape is always decoded, so a file
        # whose literal name is 'a%20b.md' is reported as missing.
        write(self.root, 'a%20b.md', 'x\n')
        write(self.root, 'doc.md', '[x](<a%20b.md>)\n')
        self.assertEqual(
            self.problems_for('doc.md'),
            ["doc.md:1: broken relative link: 'a%20b.md'"],
        )

    def test_invalid_percent_sequence_is_kept_literal(self):
        write(self.root, '100%.md', 'x\n')
        write(self.root, 'doc.md', '[x](<100%.md>)\n')
        self.assertEqual(self.problems_for('doc.md'), [])

    def test_angle_bracket_with_fragment_checks_file_part(self):
        write(self.root, 'my notes/plan.md', 'x\n')
        write(self.root, 'doc.md', '[p](<my%20notes/plan.md#step one>)\n')
        self.assertEqual(self.problems_for('doc.md'), [])


class UnencodedSpaceTests(TempRepoCase):
    def test_bare_target_cannot_contain_unencoded_space(self):
        # A bare destination cannot contain a space, so this is not treated as a link.
        write(self.root, 'my notes.md', 'x\n')
        write(self.root, 'doc.md', '[p](my notes.md)\n')
        self.assertEqual(self.problems_for('doc.md'), [])


class FragmentAndQueryTests(TempRepoCase):
    def test_file_plus_fragment_checks_file_only(self):
        write(self.root, 'target.md', '# Real heading\n')
        write(self.root, 'doc.md', '[a](target.md#no-such-anchor)\n')
        self.assertEqual(self.problems_for('doc.md'), [])

    def test_file_plus_fragment_missing_file_is_reported(self):
        write(self.root, 'doc.md', '[a](gone.md#section)\n')
        problems = self.problems_for('doc.md')
        self.assertEqual(len(problems), 1)
        self.assertIn("'gone.md#section'", problems[0])

    def test_query_string_is_stripped(self):
        write(self.root, 'target.md', 'x\n')
        write(self.root, 'doc.md', '[a](target.md?plain=1)\n')
        self.assertEqual(self.problems_for('doc.md'), [])

    def test_fragment_only_link_is_skipped(self):
        write(self.root, 'doc.md', '[top](#overview)\n')
        self.assertEqual(self.problems_for('doc.md'), [])


class ExternalAndSkipTests(TempRepoCase):
    def test_external_schemes_are_skipped(self):
        write(
            self.root,
            'doc.md',
            '[a](https://example.com/x)\n'
            '[b](http://example.com)\n'
            '[c](mailto:someone@example.invalid)\n'
            '[d](//cdn.example.com/x.js)\n',
        )
        self.assertEqual(self.problems_for('doc.md'), [])

    def test_code_fence_links_are_ignored(self):
        write(self.root, 'doc.md', '```\n[x](missing.md)\n```\n[y](missing2.md)\n')
        problems = self.problems_for('doc.md')
        self.assertEqual(len(problems), 1)
        self.assertIn("'missing2.md'", problems[0])

    def test_inline_code_span_links_are_ignored(self):
        write(self.root, 'doc.md', 'Use `[x](missing.md)` syntax.\n')
        self.assertEqual(self.problems_for('doc.md'), [])

    def test_escape_outside_root_is_reported(self):
        outside = Path(self.root).parent / 'outside-target-for-test.md'
        write(self.root, 'doc.md', '[o](../outside-target-for-test.md)\n')
        problems = self.problems_for('doc.md')
        self.assertEqual(len(problems), 1)
        self.assertIn('escapes repository root', problems[0])
        self.assertFalse(outside.exists())


class RootResolutionTests(TempRepoCase):
    def test_file_args_resolve_against_root_not_cwd(self):
        write(self.root, 'docs/doc.md', '[t](target.md)\n')
        write(self.root, 'docs/target.md', 'x\n')
        cwd = os.getcwd()
        try:
            os.chdir(tempfile.gettempdir())
            code, out, _ = self.run_main('--root', self.root, 'docs/doc.md')
        finally:
            os.chdir(cwd)
        self.assertEqual(code, checker.EXIT_OK, out)
        self.assertIn('no broken relative links', out)

    def test_missing_root_is_usage_error(self):
        code, _, err = self.run_main('--root', os.path.join(self.root, 'nope'))
        self.assertEqual(code, checker.EXIT_USAGE)
        self.assertIn('not a directory', err)

    def test_missing_file_argument_is_reported_not_crash(self):
        code, out, _ = self.run_main('--root', self.root, 'absent.md')
        self.assertEqual(code, checker.EXIT_BROKEN)
        self.assertIn('absent.md: file not found under root', out)

    def test_broken_link_returns_exit_one_with_summary(self):
        write(self.root, 'doc.md', '[x](missing.md)\n')
        code, out, _ = self.run_main('--root', self.root, 'doc.md')
        self.assertEqual(code, checker.EXIT_BROKEN)
        self.assertIn('doc.md:1: broken relative link', out)
        self.assertIn('found 1 problem(s)', out)

    def test_output_is_deterministic_across_argument_order(self):
        write(self.root, 'b.md', '[x](m1.md)\n')
        write(self.root, 'a.md', '[x](m2.md)\n')
        first = self.run_main('--root', self.root, 'b.md', 'a.md')
        second = self.run_main('--root', self.root, 'a.md', 'b.md')
        self.assertEqual(first[1], second[1])
        self.assertLess(first[1].index('a.md:1'), first[1].index('b.md:1'))


@unittest.skipUnless(shutil.which('git'), 'git is required for the tracked-file listing tests')
class TrackedListingTests(TempRepoCase):
    def test_nul_safe_listing_handles_spaces_and_skips_untracked(self):
        write(self.root, 'with space.md', 'x\n')
        write(self.root, 'untracked.md', 'x\n')
        subprocess.run(['git', '-C', self.root, 'init', '-q'], check=True)
        subprocess.run(['git', '-C', self.root, 'add', 'with space.md'], check=True)
        self.assertEqual(checker.tracked_markdown(self.root), ['with space.md'])

    def test_no_arguments_checks_tracked_files(self):
        write(self.root, 'ok.md', '[t](ok.md)\n')
        write(self.root, 'bad.md', '[t](none.md)\n')
        subprocess.run(['git', '-C', self.root, 'init', '-q'], check=True)
        subprocess.run(['git', '-C', self.root, 'add', 'ok.md', 'bad.md'], check=True)
        code, out, _ = self.run_main('--root', self.root)
        self.assertEqual(code, checker.EXIT_BROKEN)
        self.assertIn('bad.md:1', out)
        self.assertNotIn('ok.md:1', out)


if __name__ == '__main__':
    unittest.main()
