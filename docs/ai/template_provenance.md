# Template Provenance and Reuse Boundary

## Verified Lineage

ABOGADO_FACIL was created from
[`joseantoniogahez/tech_fastapi_react_postgres_docker`](https://github.com/joseantoniogahez/tech_fastapi_react_postgres_docker).

The relationship is reproducible from Git history:

| Reference                  | Commit                                                                                                                                                               | Tree                                       | Date       |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | ---------- |
| Upstream template snapshot | [`e08aa7688643ef86987746485deaf474af16053e`](https://github.com/joseantoniogahez/tech_fastapi_react_postgres_docker/commit/e08aa7688643ef86987746485deaf474af16053e) | `2d0a0e09686dd4200d9593508b12a7e542f5e882` | 2026-07-01 |
| Local initial snapshot     | `9caee176439d9e2799b6ee1460d98a08a76db86d`                                                                                                                           | `2d0a0e09686dd4200d9593508b12a7e542f5e882` | 2026-07-08 |
| First app bootstrap commit | `857a923322502ca770ddd2dfb3e627ef34896501`                                                                                                                           | `9aea95d3e45355cf3b57ece6a79fa7ffcbc0cc2d` | 2026-07-09 |

The matching Git tree proves that the local initial snapshot had exactly the same versioned content
as the pinned upstream template commit. The commits themselves differ because the local repository
started a separate history. The following local commit introduced the Abogado Fácil identity and
initial product planning artifacts.

Use the immutable upstream commit above for historical comparison. A later upstream branch head may
contain unrelated changes and must not be treated as the version originally used without comparing
its tree.

## Documentation Layers

Classification is based on current content, not only on where a file originated:

- **GENERAL — reusable foundation:** backend and frontend architecture rules, shared validation
  gates, scaffolding, and task-oriented skills that remain independent of the legal domain.
- **PARTICULAR — ABOGADO_FACIL:** product capabilities, backlog and plans, legal-domain entities and
  flows, app-specific permissions, routes, identity, operational limits, and release evidence.
- **MIXED:** root/service orientation and agent routing that connect reusable engineering rules to
  this product. Mixed documents must link to the canonical GENERAL and PARTICULAR sources instead
  of duplicating them.

Canonical locations:

| Knowledge                                                  | Canonical source                                                        |
| ---------------------------------------------------------- | ----------------------------------------------------------------------- |
| Repository task routing and validation                     | `AGENTS.md`                                                             |
| Backend engineering rules and current technical contracts  | `backend/docs/` (GENERAL and MIXED; classify each document by content)  |
| Frontend engineering rules and current technical contracts | `frontend/docs/` (GENERAL and MIXED; classify each document by content) |
| Delivered ABOGADO_FACIL behavior                           | `docs/product/capabilities/`                                            |
| Product status and implementation evidence                 | `docs/product/BACKLOG_ABOGADO_FACIL.md` and `docs/product/plans/`       |
| AI workflows and reusable skills                           | `docs/ai/` and `skills/`                                                |

## Bootstrap Boundary

`scripts/bootstrap_new_app.py` performs exact replacements against the pristine starter identity. It
is a dry-run-first bootstrap helper, not an idempotent rebranding or extraction tool.

ABOGADO_FACIL has already been bootstrapped, so running that script in the current worktree is
expected to refuse the operation when the original starter tokens are absent. To start another
application:

1. begin from the pinned upstream snapshot above, or from a newer template revision that has been
   reviewed explicitly;
1. run the workflow in `docs/ai/start_new_project.md` inside that compatible snapshot;
1. do not copy current ABOGADO_FACIL product capabilities, data, or domain rules into the new app by
   default.

Reusing foundation improvements added after the ABOGADO_FACIL bootstrap requires a separately
scoped extraction or migration. It must identify which changes are truly GENERAL, include tests and
documentation, and avoid treating the current application as a pristine template.

## Verification

To re-check the local side of the lineage:

```powershell
git show -s --format=%T 9caee176439d9e2799b6ee1460d98a08a76db86d
git show -s --format=%T 857a923322502ca770ddd2dfb3e627ef34896501
```

To verify the upstream side, fetch or clone the public template and inspect commit
`e08aa7688643ef86987746485deaf474af16053e`. The expected tree is
`2d0a0e09686dd4200d9593508b12a7e542f5e882`.
