# TEST-AI-001 - Contratos y fallos multi-provider

## Tracking Status

- ID: `TEST-AI-001`
- Type: Backend
- Priority: P1
- Plan status: Complete
- Implementation status: Hecho
- Last updated: 2026-07-25
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Demostrar con una suite contractual única que OpenAI, Gemini y Mock producen el mismo contrato
seguro de éxito y fallo, y que timeout, rate limit, respuesta inválida y decisiones de retry no
dependen de detalles específicos del proveedor.

## Starting Point

Los tres adaptadores ya implementan `AiProviderPort`, comparten `AiProviderError` y tienen pruebas
unitarias separadas. RQ configura reintentos y backoff, pero falta una matriz explícita que conecte
la clasificación `retryable` con la política esperada del futuro handler sin hacer llamadas reales.

## Scope

### Included

- Matriz contractual de éxito para OpenAI, Gemini y Mock.
- Matriz de timeout, rate limit y respuesta inválida con código y decisión de retry comunes.
- Contrato de frontera del handler: persistir y terminar en fallos no recuperables; relanzar sólo
  fallos recuperables para que RQ aplique retry/backoff.
- Verificación de que payloads, claves y mensajes externos no aparecen en fallos públicos o logs.
- Documentación canónica y contratos de documentación sincronizados.

### Excluded

- Un handler o endpoint funcional de producto.
- Llamadas reales a OpenAI, Gemini o Redis.
- Cambios de dependencia, esquema de base de datos o configuración.
- Circuit breaker, cuotas distribuidas o selección automática de proveedor.

## Dependencies and Decisions

- Dependencies: `AI-009`, `AI-010`, `AI-011` y `OBS-001`, todos completados.
- Decisions closed: usar transportes inyectados y Mock; mantener `Retry` de RQ como mecanismo de
  transporte; el handler futuro captura fallos no reintentables y sólo relanza los reintentables.
- Open questions: ninguna.

## Acceptance Criteria

- [x] OpenAI, Gemini y Mock cumplen una matriz común de éxito.
- [x] Timeout y rate limit producen códigos seguros con `retryable=True` en los tres proveedores.
- [x] JSON/estructura inválida produce `provider_invalid_response` con `retryable=False`.
- [x] La política probada sólo entrega a RQ fallos recuperables y respeta retry/backoff configurado.
- [x] Las pruebas no realizan red y demuestran ausencia de claves, payloads y detalles externos.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                       | Change required |
| ------- | ------------------------------------------------- | --------------- |
| Runtime | provider/RQ contracts                             | review          |
| Tests   | multi-provider contract, RQ, documentation suites | yes             |
| Docs    | provider errors, RQ queue, foundation status      | yes             |

## Work Plan

### Implementation

- [x] Añadir la matriz contractual multi-provider.
- [x] Fijar la decisión de retry del handler y el backoff RQ mediante pruebas.
- [x] Corregir cualquier divergencia runtime revelada por la matriz.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Pruebas focalizadas de proveedores, RQ y contratos de documentación.
- [x] `python -m pytest backend/tests`
- [x] Cobertura backend 100%.
- [x] `pre-commit run --all-files`.

## Progress Log

| Date       | State       | Completed                                         | Pending / next safe action       |
| ---------- | ----------- | ------------------------------------------------- | -------------------------------- |
| 2026-07-25 | En progreso | Alcance, matriz y frontera de retry identificados | Implementar la suite contractual |
| 2026-07-25 | Hecho       | Matriz, retry, docs y validación completados      | Sin trabajo pendiente            |

## Validation Results

| Date       | Command                                                                                                | Result | Notes                                    |
| ---------- | ------------------------------------------------------------------------------------------------------ | ------ | ---------------------------------------- |
| 2026-07-25 | Pruebas focalizadas de providers, RQ y documentación                                                   | Passed | 76 pruebas                               |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed | 511 pruebas; cobertura total 100%        |
| 2026-07-25 | `pre-commit run --all-files`                                                                           | Passed | Reejecución limpia tras formato Markdown |

## Pause / Handoff Record

- Current state: contrato multi-provider y frontera de retry probados y documentados.
- Changed files and contracts: suite multi-provider, assertions RQ, contratos de documentación,
  operaciones de proveedores/cola, foundation status y tracking.
- Pending work: ninguno dentro de `TEST-AI-001`.
- Blockers or approvals: ninguno.
- Residual risks: no existe handler funcional; el primer ticket de producto debe aplicar la
  frontera probada al persistir el lifecycle real.
- Next safe action: continuar con el siguiente ticket priorizado de seguridad o hero flow.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/backend READMEs: sin cambio; no hay dependencia, servicio, endpoint ni configuración nueva.
- API/auth/RBAC/OpenAPI: sin cambio; la suite fija contratos internos existentes.
- Arquitectura: revisada y sin cambio; ports/adapters y límites de responsabilidad permanecen.
- Frontend: sin cambio; no existe superficie pública nueva.
- Foundation status: actualizado porque la matriz multi-provider pasa a ser un gate transversal.
- AI governance: proceso sin cambio; backlog, plan e índices sincronizados.

## Completion Summary

- Delivered: matriz común de éxito/fallo para OpenAI, Gemini y Mock; timeout, rate limit, respuesta
  inválida, seguridad de datos, decisión de retry y backoff RQ probados y documentados.
- Validation: 76 pruebas focalizadas; 511 pruebas backend con cobertura 100%; pre-commit completo.
- Skipped validation: proveedores, Redis y worker reales; la suite usa transportes/colas inyectados
  porque todavía no existe un handler funcional y no debe enviar datos externos.
- Human approvals: not applicable.
- Residual risk: el futuro handler debe persistir fallos no recuperables y relanzar únicamente los
  recuperables; el contrato queda fijado, pero su integración corresponde al primer caso de uso.

Do not set the item to `Hecho` while any required criterion, validation, documentation update, or
approval remains incomplete.
