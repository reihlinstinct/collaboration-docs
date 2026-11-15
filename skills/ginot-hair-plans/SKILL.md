---
name: ginot-hair-plans
description: Develop the ginot-hair-plans tracker - public repo, GitHub Pages site, data API and MCP server for planning schemes in the Ginot HaIr area of Jerusalem. Load before changing code, data or review content.
---

# ginot-hair-plans

Scope: the tracker repository, site and API. This skill grants no new task,
account access, spending or publishing permission.

## What this solution is

[ginot-hair-plans](https://github.com/reihlinstinct/ginot-hair-plans) tracks
every planning scheme and building-permit request inside the Ginot HaIr
community-council area of Jerusalem and publishes them as a public
[site](https://reihlinstinct.github.io/ginot-hair-plans/) with derived
objection deadlines, a static data API, a Cloudflare Worker query layer and
a read-only MCP server.

## Load before work

- Repo [README](https://github.com/reihlinstinct/ginot-hair-plans#readme): purpose, data sources, Data API and MCP sections
- [worker/README.md](https://github.com/reihlinstinct/ginot-hair-plans/blob/main/worker/README.md): the read-only API/MCP Workers and the submission rules
- [Contributor rules](../../CONTRIBUTING.md)
- [Canonical merge gate](../../docs/WORKING-WITH-GEMINI.md#the-merge-gate-why-a-merge-waits)

## Operating rules

- The public repo holds public planning data only; personal fields from
  source feeds are stripped, and private status or comment files never enter
  the repo.
- Objection talking points and drafts are recommendations for the owner and
  the planner. Nothing is ever auto-filed; filing an objection is the
  owner's decision per case.
- Outside review submissions through the write Worker arrive unverified,
  land in a private submissions inbox and never go live automatically; the
  read-only Worker API returns only approved fields.
- Public reviews never attribute information to the owner and carry no
  internal correction notes.
- Free-tier limits apply (Cloudflare builds, Actions minutes): keep the
  publishing cadence the repo documents.

## Apply and report

Confirm the assigned issue, scope and exact head before work. Report the
issue or PR link, head SHA, what changed, checks run and limits through the
established coordination channel. State what was actually verified; never
claim a deploy, review or check that did not run.
