# AI-003 - Abstracción multi-provider

## Tracking Status

- ID: `AI-003`
- Type: Backend
- Priority: P1
- Plan status: Complete
- Implementation status: Hecho
- Last updated: 2026-07-25
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Definir un puerto común para ejecutar solicitudes de IA y adaptadores aislados para OpenAI, Gemini
y Mock, sin que las funciones de producto conozcan SDKs, formatos externos ni credenciales.

## Scope

### Included

- Contrato provider-neutral para solicitudes de texto y respuestas normalizadas.
- Adaptadores OpenAI y Gemini mediante transporte HTTP inyectable.
- MockProvider determinista para desarrollo y pruebas.
- Traducción segura de respuestas inválidas y errores de proveedor.
- Pruebas de contratos y payloads sin llamadas de red reales.

### Excluded

- Endpoints de funciones IA (`AI-101` a `AI-103`).
- Ejecución de jobs, reintentos y rate limits (`AI-009`, `AI-010`).
- Validación obligatoria de credenciales en cada función (`AI-004`).

## Acceptance Criteria

- [x] Los tres proveedores implementan el mismo puerto.
- [x] Los adaptadores no exponen API keys en errores ni logs.
- [x] Las respuestas se normalizan a un contrato común.
- [x] Las pruebas cubren payloads, errores HTTP, respuestas inválidas y Mock.
- [x] Documentación de arquitectura e integración queda sincronizada.
- [x] Gemini autentica mediante `x-goog-api-key` y la credencial nunca forma parte de la URL.

## Validation

- [x] `python -m pytest backend/tests`
- [x] `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [x] Pre-commit sobre archivos modificados.

## Progress Log

| Date       | State | Completed                                                                           | Pending / next safe action      |
| ---------- | ----- | ----------------------------------------------------------------------------------- | ------------------------------- |
| 2026-07-25 | Hecho | Puerto común, adaptadores OpenAI/Gemini/Mock, pruebas y documentación implementados | Sin trabajo pendiente en AI-003 |

## Validation Results

| Date       | Command                                                                                                | Result | Notes                       |
| ---------- | ------------------------------------------------------------------------------------------------------ | ------ | --------------------------- |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed | 423 tests, cobertura 100%   |
| 2026-07-25 | `pre-commit run --all-files`                                                                           | Passed | Todos los hooks pasan       |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed | 431 pruebas, cobertura 100% |

## Completion Summary

- Delivered: puerto `AiProviderPort`, contrato común, adaptadores OpenAI/Gemini/Mock, transporte
  HTTP inyectable y errores seguros sin secretos.
- Validation: suite backend completa con cobertura 100% y pre-commit completo.
- Skipped validation: ninguna.
- Human approvals: no aplicables.
- Residual risk: la validación de BYOK por ejecución y el ciclo de vida de jobs pertenecen a AI-004 y AI-009.

## Pause / Handoff Record

- Current state: Gemini autentica por header y las URLs de proveedor no contienen credenciales.
- Pending work: ninguno dentro de AI-003.
- Blockers or approvals: ninguno.
- Residual risk: no se ejecutaron llamadas reales a proveedores, fuera del alcance del adaptador.
- Next safe action: conectar el puerto desde funciones IA futuras.
