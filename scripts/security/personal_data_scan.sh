#!/usr/bin/env bash
# Scan tracked Markdown/YAML for personal data and secrets.
# The only exemption is exact 40-hex action pins (owner/action@<40 hex>) on
# `uses:` lines: their hex trips the numeric checks, so those tokens are
# removed before the two numeric checks only. Email, token and private-key
# checks see every line unmodified, and a real finding on the same line as an
# action reference is still caught.
set -u
cd "$(git rev-parse --show-toplevel)"
files=$(git ls-files '*.md' '*.yml')
fail=0
common='example\.invalid|reihlinstinct|users\.noreply'
uses_pin='[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[a-f0-9]{40}'

check() { # label regex - report file:line only, never the matched content
  hits=$(grep -HnEI "$2" $files | grep -vE "$common" | cut -d: -f1-2 || true)
  if [ -n "$hits" ]; then
    printf '%s\n' "$hits"
    echo "::error::possible $1 found"; fail=1; fi
}

check_num() { # label regex - like check, with exact 40-hex uses: pins stripped per token
  hits=$(grep -HnEI "$2" $files | sed -E "/uses:/s|$uses_pin||g" | grep -EI "$2" | grep -vE "$common" | cut -d: -f1-2 || true)
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
