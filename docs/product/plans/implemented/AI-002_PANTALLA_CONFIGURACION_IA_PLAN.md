# AI-002 - Pantalla de configuración IA

## Tracking Status

- ID: `AI-002`
- Type: Full-stack
- Priority: P1
- Plan status: Complete
- Implementation status: Hecho
- Last updated: 2026-07-25
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Permitir que una persona autenticada gestione sus credenciales BYOK desde una pantalla clara,
sin volver a mostrar secretos y sin asumir que una credencial configurada ya fue probada.

## Scope

### Included

- Ruta protegida `/settings/ai`.
- Listado de estado de OpenAI y Gemini.
- Guardado y eliminación con feedback accesible y errores normalizados.
- Advertencia explícita de que la clave se envía al backend y que el uso de IA requiere revisión.

### Excluded

- Prueba de conexión o llamadas reales a proveedores (`AI-003`).
- Mostrar, recuperar o editar parcialmente una clave existente.
- Consentimiento jurídico definitivo (`SEC-002`).

## Acceptance Criteria

- [x] La pantalla permite guardar y eliminar una clave por proveedor.
- [x] Nunca muestra la clave almacenada ni la respuesta contiene secretos.
- [x] Los estados de carga, error, éxito y vacío son accesibles.
- [x] La ruta, consumidor API, inventarios y pruebas quedan sincronizados.

## Validation

- [x] `npm --prefix frontend run check`
- [ ] `npm --prefix frontend run build` (compilación pasa; falla `perf:check` por presupuesto CSS global)
- [x] `npm --prefix frontend run openapi:check`
- [x] Pre-commit sobre archivos modificados.

## Progress Log

| Date       | State       | Completed                                                                                                              | Pending / next safe action                                                    |
| ---------- | ----------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 2026-07-21 | En progreso | Consumidor API, ruta protegida, navegación, pantalla y 6 pruebas enfocadas implementados; lint/typecheck/pruebas pasan | Resolver presupuesto CSS global, ejecutar check completo y revisar pre-commit |

### Presupuesto aprobado

El 2026-07-24 se aprobó aumentar hasta 50% el presupuesto CSS para cerrar este slice. Se aplicó
`21,400 → 32,100 B` raw y `6,000 → 9,000 B` gzip en `frontend/performance/bundle_budget.json`.

## Completion Summary

- Delivered: pantalla protegida de configuración BYOK para OpenAI y Gemini, guardado/eliminación,
  estados accesibles, consumidores API tipados, navegación y documentación sincronizada.
- Validation: `npm run check`, `npm run build`, `npm run openapi:check` y `pre-commit run --all-files` pasan.
- Skipped validation: ninguna.
- Human approvals: aumento de presupuesto CSS aprobado por el usuario; no se requirió aprobación jurídica para este slice.
- Residual risk: no valida conexión con proveedores ni ejecuta llamadas reales; corresponde a AI-003.

## Validation Results

| Date       | Command                                                                                                 | Result  | Notes                                                        |
| ---------- | ------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------ |
| 2026-07-21 | `npm run lint -- --fix`                                                                                 | Passed  | Frontend lint limpio                                         |
| 2026-07-21 | `npm run typecheck`                                                                                     | Passed  | TypeScript limpio                                            |
| 2026-07-21 | `npm run test -- src/features/ai-settings/api.test.ts src/features/ai-settings/AiSettingsPage.test.tsx` | Passed  | 2 files, 6 tests                                             |
| 2026-07-21 | `npm run build`                                                                                         | Partial | Vite compila; `perf:check` falla por CSS 21,647 B / 21,400 B |

| 2026-07-24 | `npm run build` | Passed | Vite compila y los cuatro presupuestos de rendimiento pasan con el aumento aprobado |
| 2026-07-24 | `npm run check` | Blocked | Tests, lint, typecheck y OpenAPI pasan; `deps:audit` reporta 2 vulnerabilidades altas en React Router |
| 2026-07-25 | `npm run check` | Passed | Tests con cobertura, OpenAPI y `deps:audit` pasan; vulnerabilidades altas/críticas: 0 |
| 2026-07-25 | `pre-commit run --all-files` | Passed | Todos los hooks pasan |

## Pause / Handoff Record

## Final Handoff

AI-002 quedó cerrado el 2026-07-25. El backlog está sincronizado en `Hecho`, el plan fue movido
a `plans/implemented/`, y no quedan acciones funcionales pendientes en este ticket. El siguiente
ticket recomendado es `AI-003`.

- Current state: pantalla funcional conectada a `/v1/ai/credentials` mediante TanStack Query; React Router actualizado a `7.18.1`.
- Changed files and contracts: `frontend/src/features/ai-settings/`, rutas, navegación, catálogo i18n, route inventory y API consumer matrix.
- Pending work: resolver o aprobar formalmente la excepción de las 2 vulnerabilidades altas reportadas por npm audit y correr pre-commit antes de marcar `Hecho`.
- Blockers or approvals: `deps:audit` permanece bloqueado; `react-router-dom@7.18.1` es la versión publicada más reciente y el advisory todavía la reporta dentro del rango afectado.
- Residual risks: todavía no existe prueba de conexión; el backend acepta únicamente las validaciones del slice AI-001.
- Next safe action: obtener una versión corregida de React Router o una aprobación explícita de seguridad para documentar una excepción temporal.
