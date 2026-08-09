# AI Governance Docs

This folder contains repository-level AI workflow assets that apply across backend and frontend.

Use `AGENTS.md` as the root operating guide. Use these templates when a request needs a structured
scope before implementation.

Current product behavior and planning state live under `../product/`; use
`../product/capabilities/` for delivered functional truth and
`../product/BACKLOG_ABOGADO_FACIL.md` for concise status.

## Provenance and Documentation Layers

- `template_provenance.md`: verified upstream revision, GENERAL/PARTICULAR/MIXED boundary, and the
  supported starting state for identity bootstrap.

## New Project Startup

- `start_new_project.md`: practical workflow for turning a pristine compatible starter snapshot
  into a named application. It is not a rebranding workflow for the current ABOGADO_FACIL tree.

## Improvement Plans

- `agent_capability_improvement_plan.md`: tracking plan for skills, plugin packaging, and MCP
  decisions that improve agent portability across new projects.

## Backlog Tracking

- `backlog_tracking.md`: canonical procedure for planning, pausing, resuming, documenting, and
  completing backlog items.
- `templates/backlog_item_plan.md`: reusable detailed plan and progress record for one backlog item.

## Skills

- `../../skills/README.md`: repository-local skill catalog and manual activation guide.
- `../../skills/backend-code-reviewer/SKILL.md`: specialized backend code-review workflow.
- `../../skills/frontend-code-reviewer/SKILL.md`: specialized frontend code-review workflow.
- `../../skills/fastapi-agents/SKILL.md`: adapter that loads the official FastAPI library skill
  from the installed package and applies this repository's overlay rules.
- `../../scripts/install_project_skills.py`: previews or installs repository-local skills into the
  active Codex skills directory. It writes only when `--write` is passed.

## Checklists

- `new_app_bootstrap_checklist.md`: canonical checklist for bootstrapping a compatible starter
  snapshot into a new application.

## Templates

- `templates/backlog_item_plan.md`: plan, pause record, validation log, and completion checklist for
  each backlog item.
- `templates/full_stack_feature_request.md`: request shape for features that touch both backend and
  frontend.
- `templates/new_app_request.md`: request shape for bootstrapping a new application from this
  starter kit.

## Scaffolds

- `../../scripts/scaffold_feature.py`: creates backend, frontend, or full-stack feature structure
  with TODO checklists. Use `--dry-run` before writing files.
- `../../scripts/bootstrap_new_app.py`: previews or applies identity changes in a pristine compatible
  starter snapshot. It writes only when `--write` is passed and is not idempotent.

Example:

```powershell
.\.venv\Scripts\python.exe scripts/scaffold_feature.py --dry-run full-stack audit-log --route /admin/audit-log --with-model
.\.venv\Scripts\python.exe scripts/install_project_skills.py --skill new-app-bootstrapper
```

Run the bootstrap helper only from the compatible starting state defined in
`template_provenance.md`.
