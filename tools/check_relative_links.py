#!/usr/bin/env python3
"""Offline checker for broken relative links in Markdown files.

Scope and limits:
- Line-oriented regular-expression parser, not a full CommonMark parser. No
  claim of complete Markdown parsing.
- Checks inline links and images: [label](target) and [label](<target>), with an
  optional quoted or parenthesised title.
- Angle-bracket destinations may contain spaces. Percent escapes (for example
  %20) are decoded with urllib.parse.unquote for both bare and angle-bracket
  destinations, so <a%20b.md> refers to a file named 'a b.md'. A file whose
  literal name contains a valid percent escape cannot be linked by that name.
- Skips fenced code blocks and inline code spans.
- Ignores reference-style links, autolinks, raw HTML links and labels with
  unescaped square brackets.
- Checks only the file part of a local target: a #fragment or ?query is removed.
  Anchor existence is not verified.
- Skips URLs with a scheme (http, https, mailto and so on), protocol-relative
  URLs and fragment-only links.
- No network access and no third-party dependencies.

Usage:
  python3 tools/check_relative_links.py [--root DIR] [FILE ...]

FILE arguments are paths relative to --root (default: the current directory).
With no FILE arguments, every Markdown file tracked by git under --root is
checked. Exit codes: 0 no problems, 1 problems found, 2 usage or IO error.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from urllib.parse import unquote

EXIT_OK = 0
EXIT_BROKEN = 1
EXIT_USAGE = 2

LINK_RE = re.compile(
    r'(?<!\\)!?\[(?:[^\[\]\\]|\\.)*\]'
    r'\(\s*(?:<(?P<angle>[^<>\r\n]*)>|(?P<bare>[^\s()<>]+))'
    r'(?:\s+(?:"[^"\r\n]*"|\'[^\'\r\n]*\'|\([^()\r\n]*\)))?\s*\)'
)
CODE_SPAN_RE = re.compile(r'`[^`\r\n]*`')
FENCE_RE = re.compile(r'^\s{0,3}(`{3,}|~{3,})')
SCHEME_RE = re.compile(r'^[A-Za-z][A-Za-z0-9+.\-]*:')


def iter_links(text):
    """Yield (line_number, raw_target) for inline links outside code."""
    open_fence = None
    for lineno, line in enumerate(text.splitlines(), start=1):
        fence = FENCE_RE.match(line)
        if open_fence is not None:
            if (
                fence
                and fence.group(1)[0] == open_fence[0]
                and len(fence.group(1)) >= len(open_fence)
            ):
                open_fence = None
            continue
        if fence:
            open_fence = fence.group(1)
            continue
        # Blank out code spans but keep column positions stable.
        scanned = CODE_SPAN_RE.sub(lambda m: ' ' * len(m.group(0)), line)
        for match in LINK_RE.finditer(scanned):
            target = match.group('angle')
            if target is None:
                target = match.group('bare')
            yield lineno, target


def local_path_part(target):
    """Return the decoded filesystem part of a local target, or None if not local."""
    stripped = target.strip()
    if not stripped or stripped.startswith('#') or stripped.startswith('//'):
        return None
    if SCHEME_RE.match(stripped):
        return None
    cut = len(stripped)
    for marker in ('#', '?'):
        index = stripped.find(marker)
        if index != -1 and index < cut:
            cut = index
    path = stripped[:cut]
    if not path:
        return None
    return unquote(path)


def is_inside(root, candidate):
    try:
        return os.path.commonpath([root, candidate]) == root
    except ValueError:
        return False


def check_document(root, rel_doc):
    """Return line-ordered problem strings for one Markdown file under root."""
    root = os.path.abspath(root)
    doc = os.path.join(root, rel_doc)
    with open(doc, encoding='utf-8') as handle:
        text = handle.read()
    base = os.path.dirname(doc)
    problems = []
    for lineno, target in iter_links(text):
        path = local_path_part(target)
        if path is None:
            continue
        resolved = os.path.normpath(os.path.join(base, path))
        if not is_inside(root, resolved):
            problems.append(
                f'{rel_doc}:{lineno}: link escapes repository root: {target!r}'
            )
        elif not os.path.exists(resolved):
            problems.append(f'{rel_doc}:{lineno}: broken relative link: {target!r}')
    return problems


def tracked_markdown(root):
    """List git-tracked *.md paths under root using NUL-safe output."""
    proc = subprocess.run(
        ['git', '-C', root, 'ls-files', '-z', '--', '*.md'],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.decode('utf-8', 'replace').strip()
        raise RuntimeError(f'git ls-files failed: {detail}')
    return [
        item.decode('utf-8', 'surrogateescape')
        for item in proc.stdout.split(b'\0')
        if item
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Check relative links in Markdown files without network access.'
    )
    parser.add_argument(
        '--root',
        default='.',
        help='repository root; FILE arguments are resolved against it (default: current directory)',
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Markdown files relative to --root (default: all git-tracked *.md files)',
    )
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f'error: --root is not a directory: {args.root}', file=sys.stderr)
        return EXIT_USAGE

    try:
        files = args.files if args.files else tracked_markdown(root)
    except (OSError, RuntimeError) as exc:
        print(f'error: could not list Markdown files: {exc}', file=sys.stderr)
        return EXIT_USAGE

    problems = []
    checked = 0
    for rel in sorted(set(files)):
        if not os.path.isfile(os.path.join(root, rel)):
            problems.append(f'{rel}: file not found under root')
            continue
        try:
            problems.extend(check_document(root, rel))
        except (OSError, UnicodeDecodeError) as exc:
            problems.append(f'{rel}: could not read as UTF-8 text: {exc}')
            continue
        checked += 1

    for problem in problems:
        print(problem)
    if problems:
        print(f'found {len(problems)} problem(s) in {checked} checked file(s)')
        return EXIT_BROKEN
    print(f'checked {checked} Markdown file(s): no broken relative links')
    return EXIT_OK


if __name__ == '__main__':
    sys.exit(main())
