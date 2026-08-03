# DEMO-AI-001 - Guion de demo técnica y de producto

## Tracking Status

- ID: `DEMO-AI-001`
- Type: `Docs`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-08-02`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Entregar un recorrido breve y reproducible del hero flow, con preparación, narrativa, evidencia y
escenarios de fallo seguros para audiencias técnicas y de producto.

## Scope

Incluye demo principal, BYOK, revisión humana, conversión, métricas, fallos y comando automatizado.
Excluye datos reales, llamadas pagadas obligatorias, benchmark entre modelos y despliegue público.

## Acceptance Criteria

- [x] El guion recorre relato, preview, ejecución, revisión y acción persistida.
- [x] Incluye fallos de preview, credencial, proveedor, schema, prompt injection y aislamiento.
- [x] Enlaza evidencia automatizada y límites de la demostración.
- [x] Backlog, índices y cierre del ciclo están sincronizados.
- [x] Validaciones integrales están registradas.

## Completion Summary

- Delivered: `docs/product/evidence/DEMO-AI-001_GUIA_DEMO_TECNICA_PRODUCTO.md`.
- Validation: backend, frontend, E2E, build, contratos documentales y pre-commit integrales.
- Human approvals: not applicable; no release productivo fue solicitado.
- Residual risk: una demo con proveedor real depende de clave, cuota, red y comportamiento externo.

## Validation Results

| Date       | Command                                                         | Result | Notes                                                                |
| ---------- | --------------------------------------------------------------- | ------ | -------------------------------------------------------------------- |
| 2026-08-02 | `python -m pytest backend/tests --cov=app --cov-fail-under=100` | Pass   | 610 pruebas; cobertura 100%                                          |
| 2026-08-02 | `npm --prefix frontend run check`                               | Pass   | lint, tipos, cobertura, OpenAPI y dependencias                       |
| 2026-08-02 | `npm --prefix frontend run build`                               | Pass   | build y presupuestos de performance                                  |
| 2026-08-02 | `npm --prefix frontend run test:e2e:ci`                         | Pass   | 14 escenarios, incluido hero flow                                    |
| 2026-08-02 | auditoría de estados y planes                                   | Pass   | 84 tickets `Hecho`; cero checkboxes abiertos en planes implementados |
