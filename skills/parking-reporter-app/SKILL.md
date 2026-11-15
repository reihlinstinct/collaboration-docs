---
name: parking-reporter-app
description: Develop and test the parking-reporter-app Android app, which turns a phone photo into a reviewed 106 report draft. Load before changing code, reviewing PRs or running any live submission test.
---

# Parking reporter app

Scope: the Android app repository only. This skill grants no new task,
account access, spending or publishing permission.

## What this solution is

[parking-reporter-app](https://github.com/reihlinstinct/parking-reporter-app)
is the open-source Android development preview (Kotlin, Hebrew UI, English
documentation): CameraX capture with EXIF evidence, on-device plate
recognition, manual category choice from the captured municipal catalog,
encrypted reporter settings, a review screen before sending, and staged
municipal submission. It is the mobile counterpart of the 106 reporting
pipeline.

## Load before work

- Repo [README](https://github.com/reihlinstinct/parking-reporter-app#readme), [docs/MUNICIPAL_TAXONOMY.md](https://github.com/reihlinstinct/parking-reporter-app/blob/main/docs/MUNICIPAL_TAXONOMY.md) and the [Hebrew user wiki](https://github.com/reihlinstinct/parking-reporter-app/wiki)
- [Contributor rules](../../CONTRIBUTING.md)
- [Canonical merge gate](../../docs/WORKING-WITH-GEMINI.md#the-merge-gate-why-a-merge-waits)

## Operating rules

- Merge needs green CI plus independent review on the exact head; the
  emulator test matrix and the pre-merge checklist in the repo apply.
- No municipal credentials are compiled into the app and no cloud photo
  recognition is bundled.
- Regular CI files no live case. A live submission test runs only under the
  owner's live-test rule, through the CI path, with the same filing rules as
  any real report (clear plate, no duplicates).
- Tests and demos use synthetic data; EXIF is stripped from submitted
  photos; the on-device report log stays encrypted.
- Product decisions come from the owner through Instinct; repo history is
  not authority for new product rules.

## Apply and report

Confirm the assigned issue, scope and exact head before work. Report the
issue or PR link, head SHA, what changed, checks run (including which
emulator levels) and limits through the established coordination channel.
State what was actually verified; never claim a test, build or review that
did not run.
