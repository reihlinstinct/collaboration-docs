# Code layout within files

Standard for ordering code inside a file in every `reihlinstinct` repository.
Approved by the owner 2026-11-09.

## Order by reading logic, not alphabet

A new reader reads top to bottom. Order definitions so the file tells its
story:

1. **Public API first.** The functions, classes and constants the module
   exists to offer come first, right after imports and module constants.
2. **Helpers right below their first use.** A private helper lives directly
   under the function that first calls it, not in a distant "utils" block. A
   helper shared by several callers sits under the first caller.
3. **Grouped sections with headers.** When a file has several groups (API,
   parsing, formatting, entry point), separate them with a marked section
   header comment.

Never order definitions alphabetically. Alphabetical order serves search, not
reading; editors already provide search.

## Section headers

Use one marked, greppable form so checks and readers agree:

- Python / shell / YAML: `# Section: <Name>`
- JavaScript / TypeScript / Kotlin / Swift / Java: `// Section: <Name>`

One header per group. Short names, no numbering.

## File size

- Soft limit of 400 lines per source file. Above it, split by responsibility
  (extract a module) rather than let the file grow.
- A file above 250 lines must use section headers.
- Generated files, lockfiles and vendored code are exempt: configure them as
  exclusions, never hand-edit them into compliance.
- Test files (`tests/`, `test_*`, `*_test`, `*.test.*`, `*.spec.*`) get a
  higher cap of 600 lines: test modules grow by accretion of cases, so above
  the cap the remedy is split by topic, not reordering. The section-header
  rule applies to tests unchanged.

## What CI enforces

The `repo-checks` code-layout check (versioned) enforces, per consumer config:

- the file-size cap (default 400 lines, configurable, with named exclusions);
- section headers present in any source file above 250 lines.

What stays human: whether the order actually tells the story, whether a helper
belongs in a different module, and when a file does too much. Reviewers judge
those; the check only guarantees size and navigation markers.

## Migration

Existing files are fixed incrementally, one focused PR per repo: reorder
definitions and add section headers without behavior change. A reorder PR
contains no logic edits, and the repo's tests must pass unchanged.
