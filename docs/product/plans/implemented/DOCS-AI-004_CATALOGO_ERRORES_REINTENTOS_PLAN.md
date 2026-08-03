# DOCS-AI-004 - Catálogo de errores y reintentos

## Tracking Status

- ID: `DOCS-AI-004`
- Type: `Docs`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-08-02`

## Objective and Scope

Consolidar código, retry, traducción HTTP y reproducción determinista sin duplicar el contrato
normativo de errores. No modifica la política del runtime.

## Acceptance Criteria

- [x] Todos los códigos tienen decisión de retry y resultado observable.
- [x] Casos reproducibles distinguen retry técnico de regeneración del usuario.
- [x] Índices, backlog y validación documental están sincronizados.

## Delivery and Validation

- Delivered: `backend/docs/operations/ai_failure_catalog.md` e índice backend.
- Validation: pruebas documentales y pre-commit sobre archivos cambiados.
- Human approvals: not applicable.
- Residual risk: mappings de nuevos SDK requieren casos contractuales nuevos.
