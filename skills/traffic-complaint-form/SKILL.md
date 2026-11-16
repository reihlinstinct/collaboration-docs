---
name: traffic-complaint-form
description: Develop the traffic-complaint-form pipeline in the civic-form-tools org, which fills the Israel Police traffic complaint form and emails a locked PDF. Load before changing the workflow, form layout or docs.
---

# traffic-complaint-form

Scope: the form pipeline repository. This skill grants no new task, account
access, spending or publishing permission.

## What this solution is

[traffic-complaint-form](https://github.com/civic-form-tools/traffic-complaint-form)
fills the Israel Police traffic complaint form from a GitHub Actions
workflow and emails the filled one-page PDF, encrypted, to the recipient
(in batch mode, one password ZIP of the filled PDFs).
The complainant identity, output password, recipient email and SMTP
credentials live only in one atomic secret in the protected `production`
environment (the case-data private key is a second production secret); real
case data arrives as a sealed-box encrypted payload.

## Load before work

- Repo [README](https://github.com/civic-form-tools/traffic-complaint-form#readme): privacy model and workflow design
- [Contributor rules](../../CONTRIBUTING.md)
- [Canonical merge gate](../../docs/WORKING-WITH-GEMINI.md#the-merge-gate-why-a-merge-waits)

## Operating rules

- The public repo contains no personal data: no names, ID numbers, plates,
  locations or incident details in code, tests, issues or logs.
- Every run is gated by the protected environment's required reviewer.
  Output is encrypted in every mode (single: locked PDF; batch: password
  ZIP) and never stored in the repo, artifacts or cache.
- The pipeline only emails the output (locked PDF, or a password ZIP in
  batch mode) to the recipient. Filing anything with the police is the
  owner's separate, explicit decision; never treat a successful run as a
  filing.
- The case-data public key lives in the repo for callers; the private key
  never leaves the protected environment.

## Apply and report

Confirm the assigned issue, scope and exact head before work. Report the
issue or PR link, head SHA, what changed, checks run and limits through the
established coordination channel. State what was actually verified; never
claim a run, delivery or review that did not happen.
