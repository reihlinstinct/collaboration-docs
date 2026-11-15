---
name: parking-106-reporting
description: Operate and develop the Jerusalem 106 municipal reporting pipeline - the public parking-report-helper engine and its private records runner. Load before changing, running or reviewing any part of the 106 filing workflow.
---

# Parking 106 reporting

Scope: the reporting pipeline only. This skill grants no new task, account
access, spending or publishing permission.

## What this solution is

[parking-report-helper](https://github.com/reihlinstinct/parking-report-helper)
is the public engine: it turns citizen photo evidence of street hazards in
Jerusalem (mainly sidewalk parking) into ready-to-file Hebrew municipal
reports, checks vehicles against the government registry, files cases through
the municipality's 106 API and keeps duplicate and audit state. The public
repo holds code, a captured subject catalog and synthetic tests only. Real
photos, plates, reporter identity, registry snapshots and credentials live in
a separate private data repository that runs reviewed versions of this code.

## Load before work

- Repo [README](https://github.com/reihlinstinct/parking-report-helper#readme) and [docs/API106.md](https://github.com/reihlinstinct/parking-report-helper/blob/main/docs/API106.md)
- [Contributor rules](../../CONTRIBUTING.md)
- [Canonical merge gate](../../docs/WORKING-WITH-GEMINI.md#the-merge-gate-why-a-merge-waits)

## Operating rules

- Nothing private in the public repo: no photos, plates, ID numbers,
  reporter details, credentials or real registry snapshots.
- Read-only API calls (GET checks, catalogs) need no approval. A real
  submission that opens a municipal case follows the approval rules Instinct
  states for the task; never file from an unreviewed change.
- One report per vehicle; never risk a duplicate case. Retries only while
  nothing has reached the municipality.
- Private-runner Actions minutes are budgeted: run tests on code changes
  only.
- Report wording rules (category choice, registry facts, address style) are
  owned by the private runner's reviewed configuration; do not restate them
  from memory.

## Apply and report

Confirm the assigned issue, repository, scope and exact head before work.
Report the issue or PR link, head SHA, what changed or ran, checks and limits
through the established coordination channel. State what was actually
verified; never claim a filing, test or review that did not run.
