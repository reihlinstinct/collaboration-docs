---
name: geni-uploader
description: Develop and operate geni-uploader, the containerized uploader for Geni source documents and photos. Load before changing the tool, planning an upload run or reviewing PRs.
---

# geni-uploader

Scope: the uploader tool and its run pipeline. This skill grants no new
task, account access, spending or publishing permission.

## What this solution is

[geni-uploader](https://github.com/reihlinstinct/geni-uploader) is a
containerized, user-run uploader that pushes source documents and photos to
Geni profiles through the official API and verifies every write with a
follow-up GET. The public repo is generic: no family material and no names.
The upload bundle (manifest, scans, status file) lives in a separate private
data repository; credentials are mounted at runtime and never baked into the
image, printed or committed.

## Load before work

- Repo [README](https://github.com/reihlinstinct/geni-uploader#readme), [docs/](https://github.com/reihlinstinct/geni-uploader/tree/master/docs) and [PRIVACY.md](https://github.com/reihlinstinct/geni-uploader/blob/master/PRIVACY.md)
- [Contributor rules](../../CONTRIBUTING.md)
- [Canonical merge gate](../../docs/WORKING-WITH-GEMINI.md#the-merge-gate-why-a-merge-waits)

## Operating rules

- Geni's terms forbid AI assistants operating accounts. Live Geni calls run
  only through the protected environment the owner approves per run; agent
  work stays offline: planning, tests, dry-run and output analysis.
- Public logs stay anonymised and the detailed log is encrypted. No profile
  IDs, private paths or family names in public issues, tests or docs;
  examples use invented names.
- Default branch is `master`. Identity checks on target profiles are hard
  gates; a 429 rate limit stops the run.
- The container image is immutable and carries the pinned, reviewed loader;
  the data repository supplies data only and its code is never executed.

## Apply and report

Confirm the assigned issue, scope and exact head before work. Report the
issue or PR link, head SHA, what changed or was planned, checks run and
limits through the established coordination channel. State what was actually
verified; never claim a run, upload or review that did not happen.
