#!/usr/bin/env bash
# Scan tracked Markdown/YAML for personal data and secrets.
# The only exemption is the commit SHA pinned to ossf/scorecard-action in
# .github/workflows/scorecard.yml: its hex trips the numeric checks, so that
# exact token is removed before the two numeric checks only. Email, token and
# private-key checks see every line unmodified, and a real finding on the same
# line as the action reference is still caught.
set -u
cd "$(git rev-parse --show-toplevel)"
files=$(git ls-files '*.md' '*.yml')
fail=0
common='example\.invalid|reihlinstinct|users\.noreply'
scorecard_sha='ossf/scorecard-action@fa7117db83c52d787ae5a89f350999701505d78e'

check() { # label regex - report file:line only, never the matched content
  hits=$(grep -HnEI "$2" $files | grep -vE "$common" | cut -d: -f1-2 || true)
  if [ -n "$hits" ]; then
    printf '%s\n' "$hits"
    echo "::error::possible $1 found"; fail=1; fi
}

check_num() { # label regex - like check, with the pinned action SHA stripped per token
  hits=$(grep -HnEI "$2" $files | sed "s|$scorecard_sha||g" | grep -EI "$2" | grep -vE "$common" | cut -d: -f1-2 || true)
  if [ -n "$hits" ]; then
    printf '%s\n' "$hits"
    echo "::error::possible $1 found"; fail=1; fi
}

check "email address" '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
check_num "phone-like number" '(\+?[0-9]{1,3}[ -])?[0-9]{2,3}[ -][0-9]{3}[ -][0-9]{3,4}'
check_num "long ID-like number" '[0-9]{8,}'
check "token" '(gh[pousr]_[A-Za-z0-9_-]{20,}(\.[A-Za-z0-9_-]+)*|github_pat_[A-Za-z0-9_]{30,}|xox[bp]-[A-Za-z0-9-]{10,}|AKIA[A-Z0-9]{16})'
check "private key" 'BEGIN [A-Z ]*PRIVATE KEY'
exit $fail
