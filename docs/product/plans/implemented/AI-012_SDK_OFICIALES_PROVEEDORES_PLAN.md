# AI-012 - SDK oficiales de proveedores

## Tracking Status

- ID: `AI-012`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
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
- Open questions: ninguna; se fijan `openai==2.46.0` y `google-genai==2.13.0`, cuyas APIs
  asíncronas cubren generación, JSON estructurado e inyección de clientes.

## Acceptance Criteria

- [x] OpenAI y Gemini usan sus SDK Python oficiales, o existe evidencia documentada de una
  incompatibilidad que impida migrar sin degradar contratos.
- [x] La API key permanece solo en backend y no aparece en logs, errores, jobs ni respuestas.
- [x] Generación, JSON estructurado, timeout, rate limit, autenticación, resiliencia y observabilidad
  conservan el contrato multi-provider.
- [x] Los clientes SDK se sustituyen por dobles en pruebas deterministas sin red.
- [x] Dependencias y lockfiles quedan versionados y pasan el gate de dependencias del proyecto.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                        | Change required |
| ------- | ------------------------------------------------------------------ | --------------- |
| Runtime | `backend/app/integrations/ai_providers.py`, dependencias Python    | yes             |
| Tests   | contratos y fallos de adaptadores multi-provider                   | yes             |
| Docs    | arquitectura de integraciones, errores/reintentos y README backend | review/update   |

## Work Plan

### Implementation

- [x] Confirmar SDK, versión, API asíncrona y soporte de generación estructurada por proveedor.
- [x] Incorporar dependencias mediante el mecanismo canónico del proyecto.
- [x] Adaptar OpenAI y Gemini manteniendo inyección de clientes y traducción neutral de errores.
- [x] Eliminar el código HTTP manual reemplazado y sin consumidores.

### Tests and Documentation

- [x] Extender pruebas de contrato con respuestas y excepciones representativas de ambos SDK.
- [x] Revisar todos los documentos requeridos por `AGENTS.md`.
- [x] Actualizar documentación canónica afectada por adaptadores y dependencias.

### Validation

- [x] `.\.venv\Scripts\python.exe -m pytest backend/tests`
- [x] `.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [x] `.\.venv\Scripts\python.exe -m pre_commit run --files <changed-files>`

## Progress Log

| Date       | State         | Completed                                                      | Pending / next safe action                            |
| ---------- | ------------- | -------------------------------------------------------------- | ----------------------------------------------------- |
| 2026-08-01 | Plan prepared | Alcance y paridad contractual definidos.                       | Verificar SDK/versiones y probar clientes asíncronos. |
| 2026-08-01 | En progreso   | SDK oficiales y APIs asíncronas compatibles verificados.       | Migrar adaptadores y pruebas.                         |
| 2026-08-01 | Hecho         | Adaptadores, pruebas, dependencias y documentación entregados. | Iniciar `AI-013`.                                     |

## Validation Results

| Date       | Command                                                                                                                    | Result | Notes                               |
| ---------- | -------------------------------------------------------------------------------------------------------------------------- | ------ | ----------------------------------- |
| 2026-08-01 | `.\.venv\Scripts\python.exe -m pip check`                                                                                  | Pass   | Sin dependencias rotas.             |
| 2026-08-01 | `.\.venv\Scripts\python.exe -m pytest backend/tests`                                                                       | Pass   | 593 pruebas.                        |
| 2026-08-01 | `.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Pass   | 593 pruebas; cobertura 100%.        |
| 2026-08-01 | `.\.venv\Scripts\python.exe -m pre_commit run --files <changed-files>`                                                     | Pass   | Todos los hooks aplicables pasaron. |

## Pause / Handoff Record

- Current state: OpenAI y Gemini operan mediante SDK oficiales con clientes asíncronos inyectables.
- Changed files and contracts: adaptadores IA, dependencias, pruebas contractuales, docs de
  arquitectura/errores, README backend, configuración de mypy y tracking.
- Pending work: ninguno para `AI-012`.
- Blockers or approvals: ninguno.
- Residual risks: deprecación interna advertida por `google-genai` bajo Python 3.14; no afecta tests
  ni contrato y debe vigilarse al actualizar el SDK.
- Next safe action: iniciar `AI-013` sobre los clientes SDK ya disponibles.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root `README.md`: sin cambios; no cambió instalación ni operación de nivel repositorio.
- Frontend docs/inventories: sin cambios; no cambió API ni consumidor frontend.
- `backend/docs/foundation_status.md`: sin cambios; se preservaron reglas, contratos y gates.
- AI governance docs/templates: sin cambios; no cambió el proceso de gobierno.

## Completion Summary

- Delivered: SDK oficiales asíncronos de OpenAI y Gemini, dobles inyectables, taxonomía segura,
  dependencias fijadas y documentación sincronizada.
- Validation: `pip check`, 593 pruebas backend, cobertura 100% y pre-commit sobre archivos cambiados.
- Skipped validation: pre-commit `--all-files` agotó el tiempo al preparar entornos; el gate dirigido
  sobre todos los archivos modificados pasó completo.
- Human approvals: no aplican.
- Residual risk: advertencia de deprecación interna de `google-genai` en Python 3.14.
