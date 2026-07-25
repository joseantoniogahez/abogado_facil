# SEC-001A - Aislamiento general por despacho

## Tracking Status

- ID: `SEC-001A`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Hecho`
- Implementation status: `Hecho`
- Last updated: `2026-07-25`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Demostrar con una matriz explícita y pruebas negativas que los recursos de un despacho no pueden
ser leídos ni modificados por una sesión perteneciente a otro despacho.

## Starting Point

Clientes, asuntos y sus recursos derivados ya reciben `firm_id` desde el principal autenticado.
Los repositorios de clientes y asuntos incluyen pruebas de acceso cruzado, y los servicios ocultan
identificadores ausentes o ajenos como `404`. Falta consolidar la matriz completa, cubrir de forma
uniforme todos los recursos derivados y extenderla a resultados de IA cuando esa persistencia
exista.

## Scope

### Included

- Clientes, asuntos, notas, checklists, tareas, pagos, cálculos y documentos.
- Credenciales BYOK, limitadas por usuario y despacho.
- Pruebas negativas de lectura y escritura con identificadores de otro despacho.
- Respuestas opacas que no permitan distinguir entre un recurso inexistente y uno ajeno.
- Matriz documental de cobertura por recurso y operación.

### Excluded

- Aislamiento del contexto enviado a proveedores, cubierto por `SEC-001B`.
- Persistencia de resultados de IA antes de que exista una feature propietaria.
- Rediseño del modelo de membresías o soporte multi-despacho avanzado.

## Dependencies and Decisions

- Dependencies: modelos actuales con `firm_id`, principal autenticado y `SEC-001B` para contexto IA.
- Decisions closed: el despacho se deriva de la sesión; los clientes no seleccionan `firm_id`; los
  identificadores ajenos se ocultan como no encontrados.
- Open questions: ninguna para continuar con la matriz y las pruebas de recursos existentes.

## Acceptance Criteria

- [x] Existe una matriz que enumera cada recurso tenant-owned y sus operaciones de lectura/escritura.
- [x] Cada recurso existente tiene pruebas negativas multi-despacho en router, servicio o repositorio
  según la frontera donde se aplica la política.
- [x] Ningún payload público permite seleccionar o expone innecesariamente `firm_id`.
- [x] Los identificadores ajenos y ausentes producen el mismo contrato `404 not_found`.
- [x] Los resultados de IA se incorporan a la matriz cuando exista su modelo persistente.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                          | Change required |
| ------- | -------------------------------------------------------------------- | --------------- |
| Runtime | `backend/app/features/*` tenant-owned repositories and services      | review          |
| Tests   | `backend/tests/features/*` negative multi-despacho coverage          | yes             |
| Docs    | authorization matrix, product capability docs, this plan and backlog | yes             |

## Work Plan

### Implementation

- [x] Inventariar cada consulta y mutación tenant-owned.
- [x] Añadir las pruebas negativas faltantes sin duplicar cobertura equivalente.
- [x] Corregir cualquier consulta que acepte un identificador sin aplicar `firm_id`.
- [x] Incorporar resultados de IA cuando exista la feature persistente correspondiente.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] `python -m pytest backend/tests`
- [x] `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [x] Pre-commit on changed files.

## Progress Log

| Date       | State       | Completed                                                                                                | Pending / next safe action                                              |
| ---------- | ----------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 2026-07-25 | En progreso | Plan recuperado; aislamiento existente identificado en clientes, asuntos, documentos y credenciales BYOK | Construir la matriz por recurso y localizar pruebas negativas faltantes |
| 2026-07-25 | Hecho       | Matriz documentada; pruebas negativas de escrituras y descargas completadas; queries BYOK verificadas    | Ninguno; agregar resultados IA cuando exista su persistencia            |

## Validation Results

| Date       | Command                                                                                                | Result  | Notes                                                                                                             |
| ---------- | ------------------------------------------------------------------------------------------------------ | ------- | ----------------------------------------------------------------------------------------------------------------- |
| 2026-07-25 | Revisión estática de repositorios y pruebas existentes                                                 | Partial | Hay cobertura explícita para clientes y asuntos; la auditoría completa sigue pendiente                            |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed  | 444 pruebas y 100% de cobertura; el gate general pasa, pero todavía no existe la matriz de aceptación de SEC-001A |
| 2026-07-25 | `pre-commit run --all-files`                                                                           | Passed  | Hooks de código, documentación, secretos y Compose verdes                                                         |
| 2026-07-25 | Pruebas enfocadas de aislamiento (6 archivos)                                                          | Passed  | 12 pruebas; lecturas, escrituras, descarga y queries BYOK cubiertas                                               |
| 2026-07-25 | `python -m pytest backend/tests`                                                                       | Passed  | 444 pruebas                                                                                                       |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed  | 444 pruebas; cobertura total 100%                                                                                 |
| 2026-07-25 | `pre-commit run --files <changed-files>`                                                               | Passed  | Todos los hooks aplicables pasan tras aceptar el formato automático                                               |

## Pause / Handoff Record

- Current state: ticket completo; la matriz canónica enumera recursos, operaciones, fronteras y
  evidencia negativa.
- Changed files and contracts: matriz de autorización, pruebas de recursos derivados, queries BYOK,
  plan e índice del backlog.
- Pending work: ninguno dentro de `SEC-001A`; los resultados IA persistidos están aplazados.
- Blockers or approvals: ninguno; aprobaciones humanas no aplican.
- Residual risks: los resultados persistidos de IA deberán añadirse cuando exista su feature.
- Next safe action: continuar con el siguiente release gate priorizado del backlog.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/backend READMEs, endpoint/error contracts, architecture annexes and foundation status:
  unchanged because runtime behavior and foundation rules did not change.
- Frontend operation contracts: unchanged because this ticket changes backend test evidence and
  authorization documentation only.
- AI governance templates/checklists: unchanged; the deferred persisted-result row preserves the
  release-gate requirement without inventing a persistence feature.

## Completion Summary

- Delivered: matriz completa de aislamiento por despacho y evidencia negativa uniforme para los
  recursos existentes, incluidas credenciales BYOK.
- Validation: 12 pruebas enfocadas, 444 pruebas backend y cobertura total de 100%.
- Skipped validation: ninguna.
- Human approvals: no aplican.
- Residual risk: incorporar a la matriz cualquier resultado IA persistido cuando exista su modelo.
