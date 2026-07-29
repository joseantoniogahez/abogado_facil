# SEC-001B - Aislamiento del contexto enviado a IA

## Tracking Status

- ID: `SEC-001B`
- Type: `Backend`
- Priority: `P0-IA`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-29`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Demostrar que preview, ejecución y regeneración construyen contexto exclusivamente desde el asunto
autorizado para el despacho autenticado, sin aceptar resultados o recursos de otro despacho.

## Starting Point

La asistencia IA usa `matter_id` y `firm_id`, obtiene el asunto mediante `get_for_firm`, limita las
fuentes a relato explícito y descripción autorizada, y consulta resultados persistidos por
`firm_id`/`matter_id`. Faltaba el plan formal y evidencia negativa específica del gate.

## Scope

### Included

- Pruebas negativas entre despachos para preview, ejecución y regeneración.
- Verificación de que no se construye proveedor/job/contexto al fallar autorización.
- Documentación de la matriz de autorización y resultado de gates.

### Excluded

- Compartición de asuntos entre despachos.
- Notas o documentos como fuentes IA; siguen excluidos en Fase 3.

## Acceptance Criteria

- [x] Un asunto ajeno produce respuesta opaca y no llama al proveedor.
- [x] Un resultado de otro despacho no puede usarse como origen de regeneración.
- [x] El contexto contiene únicamente relato explícito y descripción del asunto autorizado.
- [x] Suite backend, cobertura y documentación pasan.

## Work Plan

- [x] Añadir pruebas negativas multi-despacho a `backend/tests/features/ai_assistance/`.
- [x] Revisar repositorio y token firmado para confirmar inclusión de `firm_id`.
- [x] Actualizar matriz de autorización y registrar gates.
- [x] Ejecutar validaciones backend completas y cobertura.

## Progress Log

| Date       | State       | Completed                                                                            | Pending / next safe action                       |
| ---------- | ----------- | ------------------------------------------------------------------------------------ | ------------------------------------------------ |
| 2026-07-29 | En progreso | Plan creado; revisión confirmó filtros por despacho y token HMAC ligado a `firm_id`. | Añadir y ejecutar pruebas negativas específicas. |
| 2026-07-29 | Hecho       | Pruebas negativas, backend completo y cobertura 100% pasan.                          | Ninguna.                                         |

## Pause / Handoff Record

- Current state: aislamiento implementado, documentado y validado.
- Pending work: none.
- Blockers or approvals: none.
- Residual risks: none within the Phase 3 source set.
- Next safe action: preserve the negative tests when adding new AI context sources.
