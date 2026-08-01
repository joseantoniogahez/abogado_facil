# DOC-003 - Copiar y exportar borrador

## Tracking Status

- ID: `DOC-003`
- Type: `Frontend`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-31`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Permitir que la persona usuaria copie o descargue el borrador generado, conservando una advertencia
legal visible y exigiendo confirmacion explicita de revision antes de habilitar ambas acciones.

## Starting Point

`DOC-002` entrega un borrador editable y no persistido con aviso de revision profesional. Aun no
existen acciones para extraer ese contenido de la aplicacion.

## Scope

### Included

- Copia del texto editado mediante la API del portapapeles del navegador.
- Exportacion local en texto plano con una cabecera que lo identifica como borrador sujeto a revision.
- Confirmacion explicita previa, retroalimentacion accesible y reinicio de la confirmacion al editar.
- Pruebas enfocadas y sincronizacion del inventario de rutas.

### Excluded

- PDF, DOCX, almacenamiento, versionado, envio o presentacion automatica.
- Cambios de API, autenticacion, autorizacion o navegacion.

## Dependencies and Decisions

- Dependencies: `DOC-002`.
- Decisions closed: exportar como `.txt` sin dependencias; incluir advertencia en el archivo; exigir
  confirmacion por cada version editada.
- Open questions: ninguna.

## Acceptance Criteria

- [x] Copiar y exportar permanecen deshabilitados hasta confirmar la revision.
- [x] Copiar usa el contenido editado y comunica exito o fallo de forma accesible.
- [x] Exportar descarga un `.txt` con advertencia y contenido editado.
- [x] Editar el borrador invalida la confirmacion anterior.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                  | Change required |
| ------- | -------------------------------------------- | --------------- |
| Runtime | `DocumentDraftGenerator.tsx`, catalogo i18n  | yes             |
| Tests   | `DocumentTemplatesPage.test.tsx`             | yes             |
| Docs    | route inventory, backlog e indices de planes | yes             |

## Work Plan

### Implementation

- [x] Agregar confirmacion, copia y exportacion segura al editor.
- [x] Invalidar la confirmacion cuando cambie el contenido o se regenere.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run openapi:check`
- [x] `npm --prefix frontend run build`
- [x] Pre-commit on all files.

## Progress Log

| Date       | State       | Completed                                                       | Pending / next safe action       |
| ---------- | ----------- | --------------------------------------------------------------- | -------------------------------- |
| 2026-07-31 | En progreso | Alcance, decisiones y gates definidos.                          | Implementar acciones y pruebas.  |
| 2026-07-31 | Hecho       | Copia, exportacion, revision, pruebas y documentos completados. | Continuar con la siguiente fase. |

## Validation Results

| Date       | Command                                                               | Result | Notes                                                    |
| ---------- | --------------------------------------------------------------------- | ------ | -------------------------------------------------------- |
| 2026-07-31 | `npm --prefix frontend run check`                                     | Pass   | Lint, tipos, pruebas, cobertura, OpenAPI y dependencias. |
| 2026-07-31 | `npm --prefix frontend run build`                                     | Pass   | Build y presupuesto de bundle aprobados.                 |
| 2026-07-31 | `python -m pytest backend/tests/docs/test_documentation_contracts.py` | Pass   | 18 pruebas documentales.                                 |
| 2026-07-31 | `pre-commit run --all-files`                                          | Pass   | Todos los hooks pasan tras aplicar formato Markdown.     |

## Pause / Handoff Record

- Current state: implementacion completa y validada.
- Changed files and contracts: editor de borradores, catalogo i18n, prueba e inventario de ruta.
- Pending work: ninguno para `DOC-003`.
- Blockers or approvals: ninguno.
- Residual risks: disponibilidad del portapapeles depende del navegador y contexto seguro.
- Next safe action: iniciar la siguiente fase del backlog.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Backend docs and OpenAPI: no API, auth, RBAC, data or error contract changed.
- Frontend foundation status: no foundation rule, contract or gate changed.
- E2E smoke inventory: no auth, routing or global error journey changed.

## Completion Summary

- Delivered: copia al portapapeles y exportacion `.txt` con confirmacion de revision, advertencia y retroalimentacion accesible.
- Validation: frontend check/build, contrato OpenAPI, contratos documentales y pre-commit.
- Skipped validation: E2E no aplica; no cambiaron autenticacion, rutas ni manejo global de errores.
- Human approvals: no aplicable.
- Residual risk: el portapapeles puede ser denegado por permisos del navegador; la interfaz informa el fallo.
