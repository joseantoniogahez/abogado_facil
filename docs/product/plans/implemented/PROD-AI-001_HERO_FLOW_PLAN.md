# PROD-AI-001 - Hero flow de incorporación de cliente

## Tracking Status

- ID: `PROD-AI-001`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-08-01`

## Objective

Demostrar de forma reproducible que un relato inicial pasa por preview, ejecución, revisión humana,
guardado y conversión explícita en una acción del expediente.

## Scope

- Identificar y reforzar el E2E canónico del hero flow dentro de un asunto creado.
- Documentar entradas, pasos, persistencia, resultado accionable, riesgos y evidencia.
- Mantener creación de cliente/asunto como capacidades previas; el análisis ocurre dentro del asunto.
- Excluir métricas y feedback de utilidad (`OBS-002`, `PROD-AI-002`, `PROD-AI-003`).

## Acceptance Criteria

- [x] El usuario captura un relato y revisa preview, proveedor, fuentes y costo.
- [x] La ejecución produce y guarda una salida estructurada.
- [x] La salida se revisa y acepta explícitamente antes de copiar o convertir.
- [x] La conversión crea una entidad visible en el expediente.
- [x] E2E, documentación de evidencia y gates frontend pasan.

## Progress Log

| Date       | State       | Completed                                           | Pending / next safe action           |
| ---------- | ----------- | --------------------------------------------------- | ------------------------------------ |
| 2026-08-01 | En progreso | Flujo existente y prueba smoke identificados.       | Formalizar evidencia y ejecutar E2E. |
| 2026-08-01 | Hecho       | E2E explícito, evidencia y contratos sincronizados. | Ninguna.                             |

## Validation Results

| Date       | Command                                 | Result | Notes                                      |
| ---------- | --------------------------------------- | ------ | ------------------------------------------ |
| 2026-08-01 | `npm --prefix frontend run check`       | Pass   | Lint, tipos, cobertura, contratos y audit. |
| 2026-08-01 | `npm --prefix frontend run build`       | Pass   | Build y presupuesto aprobados.             |
| 2026-08-01 | `npm --prefix frontend run test:e2e:ci` | Pass   | Suite E2E completa.                        |

## Pause / Handoff Record

- Current state: completo.
- Pending work: ninguno dentro de `PROD-AI-001`.
- Blockers or approvals: ninguno.
- Next safe action: continuar con `OBS-002` y `PROD-AI-003`.

## Completion Summary

- Delivered: hero flow reproducible desde relato hasta nota accionable con revisión humana.
- Validation: frontend check, build y suite E2E completos.
- Residual risk: métricas agregadas y feedback de utilidad permanecen en tickets posteriores.
