# Backlog Item Tracking

## Purpose

Define the required lifecycle for every item in `docs/product/BACKLOG_ABOGADO_FACIL.md`. The backlog is the
concise status index; each item plan is the detailed source of truth for execution and handoff.

## Required Artifacts

- Summary tracker: `docs/product/BACKLOG_ABOGADO_FACIL.md`.
- Pending item plan: `docs/product/plans/pending/<TICKET>_<DESCRIPTIVE_NAME>_PLAN.md`.
- Implemented item plan: `docs/product/plans/implemented/<TICKET>_<DESCRIPTIVE_NAME>_PLAN.md`.
- Plan template: `docs/ai/templates/backlog_item_plan.md`.
- Canonical backend, frontend, and AI governance docs affected by the implementation.

Use uppercase ticket IDs and uppercase snake case for the descriptive plan filename. Create new
plans under `plans/pending/`; move the same file to `plans/implemented/` when engineering reaches
`Implementado` or the item reaches `Hecho`. Reuse an existing item plan instead of creating a second
tracker for the same ticket.

## Lifecycle

### Before Implementation

1. Read `AGENTS.md` and the playbooks and operation docs routed by the item scope.
1. Create or locate the item plan and record the objective, scope, exclusions, dependencies,
   acceptance criteria, expected files or contracts, validation gates, and known risks.
1. Resolve only ambiguities that would make implementation unsafe or materially incorrect.
1. Set the backlog item to `Listo` when its scope is executable, or directly to `En progreso` when
   implementation begins.

### During Implementation

1. Keep the item plan synchronized with material decisions and scope changes.
1. Check completed plan tasks and acceptance criteria only when evidence supports them.
1. Record validation commands and their actual outcomes; never report an unexecuted gate as passed.
1. Keep detailed notes out of the summary backlog.

### Before Every Pause or Partial Handoff

Update the item plan before yielding work. Record:

- current implementation state;
- completed and pending work;
- files and contracts changed;
- decisions and assumptions made;
- validation commands, results, and failures;
- blockers, external approvals, and residual risks;
- the exact next safe action for resuming work.

Keep the backlog status synchronized. Use `En progreso` when safe work remains and `Bloqueado` only
when progress genuinely depends on unavailable input or an external state change. Do not use
`Hecho` for a partial delivery.

### Before Completion

1. Compare the delivered behavior against every acceptance criterion.
1. Inspect the code diff and determine whether it changes API, auth, RBAC, routing, data, errors,
   OpenAPI, API consumers, runtime configuration, accessibility, performance, security,
   observability, e2e coverage, deployment, or AI governance contracts.
1. Update every affected README, operation document, architecture annex, inventory, foundation
   status, checklist, or template in the same change. Do not update foundation status for ordinary
   feature progress unless a foundation rule, contract, or gate changed.
1. Run the validation matrix required by `AGENTS.md` and any item-specific gates.
1. Record final validation evidence, skipped commands with reasons, residual risks, and required
   human approvals in the item plan.
1. Set the backlog item to `Implementado` when engineering, documentation, and validation are
   complete but a mandatory external approval or release gate remains. Use `Hecho` only when no
   required implementation, documentation, validation, gate, or approval remains.

## Backlog Content Boundary

`docs/product/BACKLOG_ABOGADO_FACIL.md` contains only concise planning fields such as ticket, type,
priority, status, work summary, and deliverable. Do not add chronological logs, implementation
details, command output, file lists, or pause notes there; those belong in the item plan.

## Status Semantics

- `Identificado`: known work without an implementation-ready plan.
- `Listo`: scoped and ready to start.
- `En progreso`: implementation or validation has started and required work remains.
- `Bloqueado`: progress requires unavailable input, approval, or an external state change.
- `Implementado`: engineering work and its validations are complete, but release remains blocked by
  a mandatory external approval or gate; the technical plan stays under `plans/implemented/`.
- `Hecho`: acceptance criteria, documentation, validations, and mandatory approvals are complete.

## Documentation Review Checklist

At completion, explicitly consider:

- root and service READMEs;
- backend operation and architecture docs;
- frontend operation docs and contract inventories;
- backend and frontend foundation status files;
- AI governance docs, templates, and checklists;
- the item plan and summary backlog.

Record documents reviewed but intentionally unchanged when that context prevents future ambiguity.
