# AI-001 - Credenciales BYOK

## Tracking Status

- ID: `AI-001`
- Type: Backend
- Priority: P0-IA
- Plan status: Complete
- Implementation status: Hecho
- Last updated: 2026-07-20
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Permitir que cada usuario guarde y elimine credenciales de proveedor IA de forma aislada por
despacho, cifrada en reposo y sin devolver el secreto al cliente.

## Starting Point

El backend ya dispone de autenticación, `firm_id`, Unit of Work, errores normalizados y patrones
de puertos/adaptadores, pero no tiene almacenamiento de credenciales IA ni clave maestra dedicada.

## Scope

### Included

- Modelo y migración de credenciales por usuario/proveedor.
- Cifrado AES-GCM mediante un puerto reutilizable.
- Crear o reemplazar, consultar estado sin secreto y eliminar credencial.
- Aislamiento por usuario/despacho, validación de proveedor y pruebas de no exposición.

### Excluded

- Llamadas reales a OpenAI/Gemini (`AI-003`).
- Pantalla frontend (`AI-002`).
- Prueba de conexión, jobs, consumo, rotación operativa y consentimiento jurídico.

## Dependencies and Decisions

- Dependencies: autenticación existente; `cryptography` como dependencia directa para AES-GCM.
- Decisions closed: clave maestra `AI_CREDENTIAL_ENCRYPTION_KEY` obligatoria en producción; secretos
  se descifran únicamente dentro del backend y nunca se serializan en respuestas.
- Open questions: ninguna para este slice.

## Acceptance Criteria

- [x] Credenciales se almacenan cifradas y con nonce/tag autenticados.
- [x] Crear/reemplazar, estado y eliminar están protegidos y aislados.
- [x] Ninguna respuesta, log o error contiene la clave.
- [x] Producción rechaza configuración sin clave maestra válida.
- [x] Pruebas cubren aislamiento multiusuario, reemplazo, eliminación y descifrado.
- [x] Documentación de API, authz, runtime y errores queda sincronizada.

## Affected Contracts and Files

| Surface | Expected files or contracts                                         | Change required |
| ------- | ------------------------------------------------------------------- | --------------- |
| Runtime | `app/core/config`, `app/core/security`, AI feature, migration       | yes             |
| Tests   | `backend/tests/features/ai_credentials`, config/router contracts    | yes             |
| Docs    | authz, API endpoints, authentication, error mapping, backend README | yes             |

## Work Plan

### Implementation

- [x] Añadir dependencia, configuración y puerto/adaptador criptográfico.
- [x] Crear modelo, repositorio, servicio, schemas, router y DI.
- [x] Crear migración y registrar la feature.

### Tests and Documentation

- [x] Añadir pruebas unitarias de cifrado, configuración y servicio.
- [x] Actualizar contratos canónicos y backlog.
- [x] Completar cobertura de repositorio, router y proveedores DI.

### Validation

- [x] `python -m pytest backend/tests --cov=app --cov-fail-under=100` (411 tests; 100% coverage)
- [x] Coverage backend al 100%.
- [x] Pre-commit sobre archivos modificados.

## Progress Log

| Date       | State | Completed                                                                             | Pending / next safe action          |
| ---------- | ----- | ------------------------------------------------------------------------------------- | ----------------------------------- |
| 2026-07-21 | Hecho | Slice vertical, pruebas de repositorio/router/DI, coverage 100% y OpenAPI completados | Sin trabajo pendiente en este slice |

## Validation Results

| Date       | Command                                                         | Result | Notes                       |
| ---------- | --------------------------------------------------------------- | ------ | --------------------------- |
| 2026-07-21 | `python -m pytest backend/tests --cov=app --cov-fail-under=100` | Passed | 411 tests, 100% coverage    |
| 2026-07-21 | `npm --prefix frontend run openapi:check`                       | Passed | OpenAPI artifact up to date |
| 2026-07-21 | `pre-commit run --files ...`                                    | Passed | All configured hooks passed |

## Pause / Handoff Record

- Current state: slice backend implementado y todos los gates requeridos verdes.
- Changed files and contracts: feature `ai_credentials`, configuración, migración, contratos backend, backlog y este plan.
- Pending work: ninguna funcional dentro de AI-001.
- Blockers or approvals: ninguno.
- Residual risks: la clave maestra debe gestionarse fuera de la base de datos.
- Next safe action: continuar con AI-002 o AI-003.

## Completion Summary

- Delivered: BYOK credential storage with AES-GCM, protected endpoints, firm isolation, and secret-free responses.
- Validation: backend 411 tests with 100% coverage; OpenAPI artifact synchronized and checked.
- Skipped validation: frontend check/build did not complete because Vite/esbuild could not resolve its config in the environment; this ticket has no UI changes.
- Human approvals: no aplicables al código; queda pendiente aprobación jurídica de `SEC-002`.
- Residual risk: the master key must be managed outside the database and must not be lost; UI and real provider connectivity belong to later tickets.
