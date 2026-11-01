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

check() { # label regex - full-line scan, only the global doc allowlist applies
  if grep -nEI "$2" $files | grep -vE "$common"; then
    echo "::error::possible $1 found"; fail=1; fi
}

check_num() { # label regex - like check, with the pinned action SHA stripped per token
  hits=$(grep -nEI "$2" $files | sed "s|$scorecard_sha||g" | grep -EI "$2" | grep -vE "$common" || true)
  if [ -n "$hits" ]; then
    printf '%s\n' "$hits"
    echo "::error::possible $1 found"; fail=1; fi
}

check "email address" '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
check_num "phone-like number" '(\+?[0-9]{1,3}[ -])?[0-9]{2,3}[ -][0-9]{3}[ -][0-9]{3,4}'
check_num "long ID-like number" '[0-9]{8,}'
check "token" '(ghp_|github_pat_|xox[bp]-|AKIA)[A-Za-z0-9_]{10,}'
check "private key" 'BEGIN [A-Z ]*PRIVATE KEY'
exit $fail
