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
- [x] `npm --prefix frontend run build`
- [x] `npm --prefix frontend run openapi:check`
- [x] Pre-commit sobre archivos modificados.

## Remediación de revisión 2026-07-24

- [x] El feedback de guardado y eliminación nunca muestra éxito y error obsoletos a la vez.
- [x] El error de carga conserva diagnóstico correlacionado y no presenta un estado desconocido
  como no configurado.
- [x] El smoke E2E cubre acceso protegido, carga, guardado y eliminación en `/settings/ai`.
- [x] La matriz de errores y la política de mutaciones documentan el consumidor BYOK.

## Progress Log

| Date       | State       | Completed                                                                                                              | Pending / next safe action                                                    |
| ---------- | ----------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 2026-07-21 | En progreso | Consumidor API, ruta protegida, navegación, pantalla y 6 pruebas enfocadas implementados; lint/typecheck/pruebas pasan | Resolver presupuesto CSS global, ejecutar check completo y revisar pre-commit |

### Presupuesto aprobado

El 2026-07-24 se aprobó aumentar hasta 50% el presupuesto CSS para cerrar este slice. Se aplicó
`21,400 → 32,100 B` raw y `6,000 → 9,000 B` gzip en `frontend/performance/bundle_budget.json`.

## Completion Summary

- Delivered: pantalla protegida de configuración BYOK para OpenAI y Gemini, guardado/eliminación,
  estados accesibles, feedback sin mensajes obsoletos, diagnóstico correlacionado, consumidor API
  tipado, navegación, smoke E2E y documentación sincronizada.
- Validation: `npm run check` (254 pruebas), `npm run build`, `npm run test:e2e:ci` (14 pruebas) y
  `pre-commit run --all-files` pasan.
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
| 2026-07-25 | `npm run check && npm run build` | Passed | 254 pruebas; OpenAPI, dependencias y presupuestos verdes |
| 2026-07-25 | `npm run test:e2e:ci` | Passed | 14 smoke tests, incluido `/settings/ai` |

## Pause / Handoff Record

## Final Handoff

AI-002 quedó cerrado nuevamente después de la remediación de revisión. El backlog está
sincronizado en `Hecho`, no quedan validaciones ni aprobaciones pendientes y la auditoría de
dependencias reporta cero vulnerabilidades altas o críticas.

- Current state: pantalla funcional conectada a `/v1/ai/credentials`, con estados deterministas y
  smoke E2E protegido.
- Changed files and contracts: UI y pruebas de `ai-settings`, catálogo i18n, matriz de consumidores,
  política de mutaciones, smoke E2E y READMEs.
- Pending work: ninguno dentro de AI-002.
- Blockers or approvals: ninguno.
- Residual risks: la prueba de conexión real pertenece a funciones posteriores.
- Next safe action: continuar con los siguientes tickets de producto IA.
