# Contributing

- Work from a fork or a branch and open a PR. One focused change per PR, with a clear title and a full description: what changed, why, and any limits.
- Never push to `main` and never merge your own PR. The maintainer merges when CI is green.
- No personal data, secrets, tokens, plates, IDs or private-case details in any file, issue or PR.
- Docs are in English. Keep them short and concrete.

## Issues: labels, milestones and order

The same scheme is used in every public repo. Do not add parallel label schemes.

**Labels** (every open issue has one type, one area and one priority)
- `type: feature | fix | task | docs | security` - the kind of work.
- `area: ...` - the part of the project. The list is per repo.
- `priority: high | medium | low` - high is done first.
- `status: blocked | held | in-progress | needs-review` - only when it applies.
- `needs-triage` - not sorted yet. Remove it when the three labels above are set.
- `good first issue` - small and clear, a good place to start.

**Milestones:** `Now` (in progress or due this week), `Next` (planned after Now), `Later` (backlog). High priority goes to Now, medium to Next, low to Later, unless the maintainer decides otherwise.

**Picking an issue:** filter by milestone `Now`, then `Next`. Take high priority first. Skip blocked, held and in-progress items. Comment "taking this", work from a fork, open a PR.
