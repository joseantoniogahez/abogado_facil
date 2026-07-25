# OpenAPI Documentation Pattern

## Goal

Keep routers readable while preserving explicit endpoint documentation.

## Runtime exposure policy

Interactive documentation is enabled in non-production environments. It is disabled explicitly in
`prod`, `production`, and `staging` by setting `docs_url`, `redoc_url`, and `openapi_url` to
`None` when the application is created. Production deployments therefore do not expose the
complete API schema through `/docs`, `/redoc`, or `/openapi.json`.

## Current structure

OpenAPI metadata is owned by the feature that exposes the endpoint.

- shared helpers: `app/core/common/openapi.py`
- feature docs:
  - `app/features/audit_log/openapi.py`
  - `app/features/auth/openapi.py`
  - `app/features/clients/openapi.py`
  - `app/features/dashboard/openapi.py`
  - `app/features/health/openapi.py`
  - `app/features/matters/openapi.py`
  - `app/features/matter_checklists/openapi.py`
  - `app/features/matter_documents/openapi.py`
  - `app/features/matter_notes/openapi.py`
  - `app/features/matter_payments/openapi.py`
  - `app/features/matter_tasks/openapi.py`
  - `app/features/rbac/openapi/__init__.py`
  - `app/features/rbac/openapi/docs.py`
  - `app/features/rbac/openapi/params.py`

Routers consume those constants with `**DOC_CONSTANT`.

The AI credential and matter-calculation routers currently derive their schema metadata from typed
request/response models and FastAPI defaults. Any custom summaries, examples, parameters, or error
responses added to those surfaces must be placed in feature-local OpenAPI modules before being
consumed by their routers.

## Router pattern

```python
@router.get("/roles", response_model=list[RBACRole], **GET_ROLES_DOC)
async def list_roles(...):
    ...
```

Typed payload/path aliases can also live next to feature docs:

```python
RoleIdPath = Annotated[int, Path(ge=1)]
CreateRolePayload = Annotated[CreateRoleRequest, Body(...)]
```

## Naming conventions

- endpoint metadata: `<ENDPOINT_NAME>_DOC`
- payload/path aliases: descriptive singular names such as `CreateRolePayload`, `RoleIdPath`
- shared helpers:
  - `build_error_response`
  - `INTERNAL_ERROR_EXAMPLE`

## Adding docs for a new endpoint

1. Add metadata constants in the feature OpenAPI module.
1. Import them in the feature router.
1. Keep examples close to the feature, not in a global demo module.
1. Run router tests after updating the docs.
