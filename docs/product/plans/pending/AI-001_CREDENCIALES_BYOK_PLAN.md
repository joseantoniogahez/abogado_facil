# AI-001 - Credenciales BYOK

## Tracking Status

- ID: `AI-001`
- Type: Backend
- Priority: P0-IA
- Plan status: Draft
- Implementation status: En progreso
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

- [ ] Credenciales se almacenan cifradas y con nonce/tag autenticados.
- [ ] Crear/reemplazar, estado y eliminar están protegidos y aislados.
- [ ] Ninguna respuesta, log o error contiene la clave.
- [ ] Producción rechaza configuración sin clave maestra válida.
- [ ] Pruebas cubren aislamiento multiusuario, reemplazo, eliminación y descifrado.
- [ ] Documentación de API, authz, runtime y errores queda sincronizada.

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
- [ ] Completar cobertura de repositorio, router y proveedores DI.

### Validation

- [x] `python -m pytest backend/tests` (402 tests funcionales; coverage gate pendiente)
- [ ] Coverage backend al 100%.
- [ ] Pre-commit sobre archivos modificados.

## Progress Log

| Date       | State       | Completed                                                              | Pending / next safe action                                |
| ---------- | ----------- | ---------------------------------------------------------------------- | --------------------------------------------------------- |
| 2026-07-20 | En progreso | Slice vertical, migración, contratos y pruebas enfocadas implementados | Completar pruebas de cobertura y revisar OpenAPI generado |

## Validation Results

| Date | Command | Result | Notes |
| ---- | ------- | ------ | ----- |
|      |         |        |       |

## Pause / Handoff Record

- Current state: slice backend implementado y pruebas enfocadas verdes.
- Changed files and contracts: feature `ai_credentials`, configuración, migración, contratos backend, backlog y este plan.
- Pending work: pruebas de repositorio/router/DI, coverage 100%, sincronización OpenAPI y revisión final.
- Blockers or approvals: ninguno.
- Residual risks: la clave maestra debe gestionarse fuera de la base de datos.
- Next safe action: añadir pruebas directas para las líneas pendientes y ejecutar el coverage gate completo.

## Completion Summary

- Delivered: pendiente.
- Validation: pendiente.
- Skipped validation: pendiente.
- Human approvals: no aplicables al código; queda pendiente aprobación jurídica de `SEC-002`.
- Residual risk: pendiente.
