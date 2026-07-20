# <TICKET> - <Backlog Item Name>

## Tracking Status

- ID: `<TICKET>`
- Type: `<Backend | Frontend | Full-stack | AI | Legal | Docs | Ops | Product | Setup>`
- Priority: `<P0 | P0-IA | P1 | P2>`
- Plan status: `<Draft | Ready | Complete>`
- Implementation status: `<Identificado | Listo | En progreso | Bloqueado | Hecho>`
- Last updated: `<YYYY-MM-DD>`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Describe the user or operational outcome and how success will be recognized.

## Starting Point

Summarize existing behavior, relevant architecture, and verified gaps.

## Scope

### Included

- <Required behavior or deliverable>

### Excluded

- <Explicitly deferred or protected behavior>

## Dependencies and Decisions

- Dependencies: \<tickets, providers, migrations, approvals, or none>.
- Decisions closed: <implementation decisions already made>.
- Open questions: <only questions that materially affect delivery>.

## Acceptance Criteria

- [ ] <Observable criterion>
- [ ] Required documentation is synchronized with delivered behavior.
- [ ] Required validation gates pass and are recorded below.
- [ ] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts | Change required  |
| ------- | --------------------------- | ---------------- |
| Runtime | <paths or none>             | \<yes/no/review> |
| Tests   | <paths or suites>           | \<yes/no/review> |
| Docs    | <canonical docs>            | \<yes/no/review> |

## Work Plan

### Implementation

- [ ] <Task>

### Tests and Documentation

- [ ] Add or update tests with the behavior change.
- [ ] Review all documentation surfaces required by `AGENTS.md`.
- [ ] Update canonical documents affected by the code diff.

### Validation

- [ ] <Targeted validation command>
- [ ] <Required gate from the validation matrix>
- [ ] Pre-commit on changed files.

## Progress Log

| Date       | State         | Completed | Pending / next safe action |
| ---------- | ------------- | --------- | -------------------------- |
| YYYY-MM-DD | Plan prepared | <summary> | <next action>              |

## Validation Results

| Date | Command | Result | Notes |
| ---- | ------- | ------ | ----- |
|      |         |        |       |

## Pause / Handoff Record

- Current state: <what works now>.
- Changed files and contracts: <summary>.
- Pending work: <ordered remainder>.
- Blockers or approvals: <details or none>.
- Residual risks: <details or none>.
- Next safe action: <exact resume point>.

Update this section before every pause or partial handoff.

## Completion Documentation Review

- [ ] Root and service READMEs reviewed.
- [ ] Backend operation and architecture docs reviewed.
- [ ] Frontend operation docs and inventories reviewed.
- [ ] Foundation status files reviewed and changed only if a foundation contract moved.
- [ ] AI governance docs, templates, and checklists reviewed.
- [ ] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- <Document>: <reason no update was required>.

## Completion Summary

- Delivered: <behavior and documentation>.
- Validation: <passed commands>.
- Skipped validation: \<command and reason, or none>.
- Human approvals: <record or not applicable>.
- Residual risk: <risk or none>.

Do not set the item to `Hecho` while any required criterion, validation, documentation update, or
approval remains incomplete.
