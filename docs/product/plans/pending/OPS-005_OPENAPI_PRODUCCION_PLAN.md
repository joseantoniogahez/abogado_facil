# OPS-005 - Protección de documentación OpenAPI en producción

## Tracking Status

- ID: `OPS-005`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Ready`
- Implementation status: `Identificado`
- Last updated: `2026-07-19`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Evitar que la documentación y el esquema completo de la API queden expuestos accidentalmente en
producción, manteniendo una experiencia útil en local y test.

## Starting Point

La fábrica crea FastAPI sin configuración explícita de `docs_url`, `redoc_url` u `openapi_url`.

## Scope

### Included

- Decidir y aplicar política por entorno para `/docs`, `/redoc` y `/openapi.json`.
- Añadir pruebas de configuración y actualizar documentación operativa.

### Excluded

- Cambiar el contrato funcional de endpoints.
- Crear un portal externo de documentación.

## Dependencies and Decisions

- Dependencies: `AUDIT-001`.
- Decisions closed: local/test deben conservar documentación; producción requiere protección o deshabilitación explícita.
- Open questions: confirmar si el despliegue productivo tendrá acceso administrativo interno.

## Acceptance Criteria

- [ ] Política por entorno implementada y probada.
- [ ] No se filtran secretos ni endpoints de forma no intencionada.
- [ ] Documentación canónica sincronizada.
- [ ] Backend tests y coverage gate pasan.

## Affected Contracts and Files

| Surface | Expected files or contracts                   | Change required |
| ------- | --------------------------------------------- | --------------- |
| Runtime | `backend/app/core/setup/factory.py`, settings | yes             |
| Tests   | `backend/tests/test_main.py`, settings tests  | yes             |
| Docs    | backend runtime/security docs                 | yes             |

## Work Plan

- [ ] Confirmar decisión de exposición con la auditoría.
- [ ] Implementar configuración por entorno.
- [ ] Probar local/test/prod y documentar la política.

## Validation

- [ ] `python -m pytest backend/tests`
- [ ] coverage gate backend
- [ ] pre-commit sobre archivos modificados

## Progress Log

| Date       | State         | Completed               | Pending / next safe action |
| ---------- | ------------- | ----------------------- | -------------------------- |
| 2026-07-19 | Plan prepared | Scope and risk recorded | Wait for `AUDIT-001`       |

## Validation Results

No ejecutadas: ticket no iniciado.

## Pause / Handoff Record

- Current state: plan listo.
- Pending work: implementar política y pruebas.
- Blockers or approvals: decisión de exposición productiva.
- Residual risks: documentación potencialmente pública.
- Next safe action: iniciar después de `AUDIT-001`.

## Completion Summary

- Delivered: pendiente.
- Validation: pendiente.
- Residual risk: pendiente.
