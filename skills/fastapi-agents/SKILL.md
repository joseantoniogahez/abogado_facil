---
name: fastapi-agents
description: Adapter for using the official FastAPI library Agent Skill together with this repository's governance rules. Use when Codex implements or reviews FastAPI, Pydantic, dependency injection, streaming/SSE, lifecycle, OpenAPI, middleware, security, or Starlette-backed behavior.
---

# FastAPI project adapter

## Required official skill

Before taking action, load the official FastAPI library skill bundled with the installed FastAPI
package:

```text
.venv/Lib/site-packages/fastapi/.agents/skills/fastapi/SKILL.md
```

When the repository uses a different Python environment, resolve the installed `fastapi` package
and load `<fastapi-package>/.agents/skills/fastapi/SKILL.md` instead. Do not copy that file into
this repository or replace its guidance with a locally maintained summary.

The official skill is the source of truth for current FastAPI conventions and references. This
adapter only adds the repository-specific constraints below.

## Repository overlay

After loading the official skill:

1. Read `AGENTS.md`.
2. Read `backend/docs/backend_playbook.md` and `backend/docs/foundation_status.md`.
3. Read affected backend operation and architecture documents. For full-stack work, read the
   frontend playbook and API contract-sync documentation too.
4. Preserve this repository's boundaries: router -> service -> repository -> core runtime,
   typed dependency providers, Unit of Work for writes, explicit authorization, normalized errors,
   feature-owned OpenAPI metadata, and synchronized frontend contracts.
5. Add or update tests and canonical documentation with the implementation.
6. Run the validation matrix from `AGENTS.md` and report skipped checks and residual risk.

## Safety boundary

This skill is for coding-agent guidance only. It does not add an AI agent to the running API and
does not authorize installing the third-party `fastapi-agent` package. A runtime agent would need a
separate product request, route allowlist, authentication design, data-handling review, cost limits,
and tests.
