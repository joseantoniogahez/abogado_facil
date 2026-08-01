# DOC-002 - Generador de borradores desde plantilla

## Tracking Status

- ID: `DOC-002`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-31`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Permitir seleccionar una plantilla, validar sus datos, confirmar el contexto enviado al proveedor
BYOK y obtener un borrador editable sujeto a revisión profesional.

## Scope

### Included

- Formulario dinámico para los campos declarados por `DOC-001`.
- Preview firmado con campos incluidos, costo BYOK y token contra cambios posteriores.
- Generación estructurada mediante proveedor configurado, contexto minimizado y job auditable.
- Borrador editable con aviso persistente; sin envío ni presentación automática.
- Pruebas, OpenAPI e inventarios.

### Excluded

- Persistencia de borradores o versiones.
- Copiar o exportar el borrador (`DOC-003`).
- Asesoría legal autónoma o documentos complejos.

## Dependencies and Decisions

- Dependencies: `DOC-001`, BYOK, gates de contexto y salida IA, ciclo de `AIJob`.
- Decision: preview y generación son globales al despacho y no requieren seleccionar un asunto.
- Decision: el backend revalida campos y firma su contenido; cualquier cambio exige nuevo preview.
- Decision: la salida estructurada contiene un solo texto editable y se etiqueta como borrador.

## Acceptance Criteria

- [x] El formulario refleja campos requeridos y opcionales de las cuatro plantillas.
- [x] El backend rechaza campos faltantes, desconocidos o vacíos.
- [x] La generación solo ocurre tras preview vigente y usa infraestructura BYOK controlada.
- [x] El resultado queda editable con advertencia de revisión y sin acciones automáticas.
- [x] Gates backend, frontend, OpenAPI y pre-commit pasan.

## Work Plan

- [x] Implementar esquemas, servicio, DI y endpoints de preview/generación.
- [x] Integrar formulario, proveedor/modelo, confirmación y editor en frontend.
- [x] Añadir pruebas y actualizar documentación e inventarios.
- [x] Ejecutar validaciones completas.

## Progress Log

| Date       | State       | Completed                                                       | Pending / next safe action        |
| ---------- | ----------- | --------------------------------------------------------------- | --------------------------------- |
| 2026-07-31 | En progreso | Arquitectura de preview, validación y job definida.             | Implementar servicio y contratos. |
| 2026-07-31 | Hecho       | Generación controlada, editor, pruebas y contratos completados. | Continuar con `DOC-003`.          |

## Validation Results

| Date       | Command                                                         | Result | Notes                                        |
| ---------- | --------------------------------------------------------------- | ------ | -------------------------------------------- |
| 2026-07-31 | `python -m pytest backend/tests --cov=app --cov-fail-under=100` | Pass   | 598 pruebas; cobertura total de 100 %.       |
| 2026-07-31 | `npm --prefix frontend run openapi:sync`                        | Pass   | Contrato actualizado con preview/generación. |
| 2026-07-31 | `npm --prefix frontend run check`                               | Pass   | Lint, tipos, pruebas, cobertura y contratos. |
| 2026-07-31 | `npm --prefix frontend run build`                               | Pass   | Build y presupuesto de bundle aprobados.     |
| 2026-07-31 | `pre-commit run --all-files`                                    | Pass   | Hooks aprobados tras aplicar formato.        |

## Pause / Handoff Record

- Current state: implementación completa y validada.
- Changed files and contracts: API de drafts, DI, OpenAPI, formulario, editor e inventarios.
- Pending work: ninguno para `DOC-002`; copiar/exportar corresponde a `DOC-003`.
- Blockers or approvals: ninguno.
- Residual risks: calidad del texto dependiente del proveedor y de los datos ingresados.
- Next safe action: preparar `DOC-003` sobre el editor entregado.

## Completion Documentation Review

- [x] Root and service READMEs reviewed; no cambios requeridos.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed; ninguna regla base cambió.
- [x] AI governance docs reviewed; ninguna regla cambió.
- [x] Item plan and backlog synchronized.

## Completion Summary

- Delivered: preview firmado, generación BYOK auditable y borrador editable para cuatro plantillas.
- Validation: backend 100 %, OpenAPI, frontend check/build y pre-commit.
- Skipped validation: E2E no aplica; no cambiaron autenticación, ruta ni manejo global de errores.
- Human approvals: no aplicable.
- Residual risk: calidad y latencia dependen del proveedor y de la información ingresada.
