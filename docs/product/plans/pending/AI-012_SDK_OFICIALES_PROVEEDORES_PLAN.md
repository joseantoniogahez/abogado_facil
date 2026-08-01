# AI-012 - SDK oficiales de proveedores

## Tracking Status

- ID: `AI-012`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Ready`
- Implementation status: `Listo`
- Last updated: `2026-08-01`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Reemplazar, cuando la evaluación técnica confirme compatibilidad, las solicitudes HTTP manuales de
OpenAI y Gemini por sus SDK Python oficiales, sin cambiar el puerto neutral ni los contratos de
seguridad, resiliencia y observabilidad ya entregados.

## Starting Point

`OpenAIProvider` y `GeminiProvider` implementan generación correctamente sobre `AiProviderPort`,
pero mantienen manualmente URLs, headers, serialización y lectura de respuestas.

## Scope

### Included

- Verificar los SDK oficiales y versiones compatibles con el runtime.
- Migrar ambos adaptadores a clientes asíncronos oficiales si preservan los contratos actuales.
- Mantener puerto neutral, errores seguros, timeouts, reintentos, métricas, correlación, salida
  estructurada y herramientas deshabilitadas.
- Mantener clientes inyectables para pruebas sin red.
- Retirar el transporte HTTP manual solo después de alcanzar paridad probada.

### Excluded

- Agregar proveedores o exponer API keys al frontend.
- Cambiar prompts, schemas, funciones IA o modelos elegidos por el usuario.
- Aceptar una regresión de seguridad o testabilidad para adoptar un SDK.

## Dependencies and Decisions

- Dependencies: `AI-003`, `AI-010` y `AI-011`, ya entregados.
- Decisions closed: se conservan `AiProviderPort` y la taxonomía propia; las excepciones de los SDK
  se traducen al contrato interno sin filtrar contenido sensible.
- Open questions: versión exacta de cada SDK y posibles incompatibilidades que justifiquen conservar
  HTTP manual para una operación concreta.

## Acceptance Criteria

- [ ] OpenAI y Gemini usan sus SDK Python oficiales, o existe evidencia documentada de una
  incompatibilidad que impida migrar sin degradar contratos.
- [ ] La API key permanece solo en backend y no aparece en logs, errores, jobs ni respuestas.
- [ ] Generación, JSON estructurado, timeout, rate limit, autenticación, resiliencia y observabilidad
  conservan el contrato multi-provider.
- [ ] Los clientes SDK se sustituyen por dobles en pruebas deterministas sin red.
- [ ] Dependencias y lockfiles quedan versionados y pasan el gate de dependencias del proyecto.
- [ ] Required documentation is synchronized with delivered behavior.
- [ ] Required validation gates pass and are recorded below.
- [ ] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                        | Change required |
| ------- | ------------------------------------------------------------------ | --------------- |
| Runtime | `backend/app/integrations/ai_providers.py`, dependencias Python    | yes             |
| Tests   | contratos y fallos de adaptadores multi-provider                   | yes             |
| Docs    | arquitectura de integraciones, errores/reintentos y README backend | review/update   |

## Work Plan

### Implementation

- [ ] Confirmar SDK, versión, API asíncrona y soporte de generación estructurada por proveedor.
- [ ] Incorporar dependencias mediante el mecanismo canónico del proyecto.
- [ ] Adaptar OpenAI y Gemini manteniendo inyección de clientes y traducción neutral de errores.
- [ ] Eliminar el código HTTP manual reemplazado y sin consumidores.

### Tests and Documentation

- [ ] Extender pruebas de contrato con respuestas y excepciones representativas de ambos SDK.
- [ ] Revisar todos los documentos requeridos por `AGENTS.md`.
- [ ] Actualizar documentación canónica afectada por adaptadores y dependencias.

### Validation

- [ ] `.\.venv\Scripts\python.exe -m pytest backend/tests`
- [ ] `.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [ ] `.\.venv\Scripts\python.exe -m pre_commit run --all-files`

## Progress Log

| Date       | State         | Completed                                | Pending / next safe action                            |
| ---------- | ------------- | ---------------------------------------- | ----------------------------------------------------- |
| 2026-08-01 | Plan prepared | Alcance y paridad contractual definidos. | Verificar SDK/versiones y probar clientes asíncronos. |

## Validation Results

| Date | Command | Result | Notes |
| ---- | ------- | ------ | ----- |
|      |         |        |       |

## Pause / Handoff Record

- Current state: adaptadores HTTP existentes operativos; migración no iniciada.
- Changed files and contracts: backlog y plan únicamente.
- Pending work: evaluación, dependencias, migración, pruebas y documentación.
- Blockers or approvals: ninguno.
- Residual risks: diferencias de excepciones, timeouts o schemas entre SDK y API HTTP actual.
- Next safe action: verificar versiones y capacidades actuales en la documentación oficial.

## Completion Documentation Review

- [ ] Root and service READMEs reviewed.
- [ ] Backend operation and architecture docs reviewed.
- [ ] Frontend operation docs and inventories reviewed.
- [ ] Foundation status files reviewed and changed only if a foundation contract moved.
- [ ] AI governance docs, templates, and checklists reviewed.
- [ ] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Pendiente de implementación.

## Completion Summary

- Delivered: pendiente.
- Validation: pendiente.
- Skipped validation: planificación documental; no se modificó runtime.
- Human approvals: no aplican por ahora.
- Residual risk: pendiente de evaluación de los SDK.
