# SEC-001A - Aislamiento general por despacho

## Tracking Status

- ID: `SEC-001A`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Ready`
- Implementation status: `En progreso`
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

- [ ] Existe una matriz que enumera cada recurso tenant-owned y sus operaciones de lectura/escritura.
- [ ] Cada recurso existente tiene pruebas negativas multi-despacho en router, servicio o repositorio
  según la frontera donde se aplica la política.
- [ ] Ningún payload público permite seleccionar o expone innecesariamente `firm_id`.
- [ ] Los identificadores ajenos y ausentes producen el mismo contrato `404 not_found`.
- [ ] Los resultados de IA se incorporan a la matriz cuando exista su modelo persistente.
- [ ] Required documentation is synchronized with delivered behavior.
- [ ] Required validation gates pass and are recorded below.
- [ ] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                          | Change required |
| ------- | -------------------------------------------------------------------- | --------------- |
| Runtime | `backend/app/features/*` tenant-owned repositories and services      | review          |
| Tests   | `backend/tests/features/*` negative multi-despacho coverage          | yes             |
| Docs    | authorization matrix, product capability docs, this plan and backlog | yes             |

## Work Plan

### Implementation

- [ ] Inventariar cada consulta y mutación tenant-owned.
- [ ] Añadir las pruebas negativas faltantes sin duplicar cobertura equivalente.
- [ ] Corregir cualquier consulta que acepte un identificador sin aplicar `firm_id`.
- [ ] Incorporar resultados de IA cuando exista la feature persistente correspondiente.

### Tests and Documentation

- [ ] Add or update tests with the behavior change.
- [ ] Review all documentation surfaces required by `AGENTS.md`.
- [ ] Update canonical documents affected by the code diff.

### Validation

- [ ] `python -m pytest backend/tests`
- [ ] `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [ ] Pre-commit on changed files.

## Progress Log

| Date       | State       | Completed                                                                                                | Pending / next safe action                                              |
| ---------- | ----------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 2026-07-25 | En progreso | Plan recuperado; aislamiento existente identificado en clientes, asuntos, documentos y credenciales BYOK | Construir la matriz por recurso y localizar pruebas negativas faltantes |

## Validation Results

| Date       | Command                                                                                                | Result  | Notes                                                                                                             |
| ---------- | ------------------------------------------------------------------------------------------------------ | ------- | ----------------------------------------------------------------------------------------------------------------- |
| 2026-07-25 | Revisión estática de repositorios y pruebas existentes                                                 | Partial | Hay cobertura explícita para clientes y asuntos; la auditoría completa sigue pendiente                            |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed  | 444 pruebas y 100% de cobertura; el gate general pasa, pero todavía no existe la matriz de aceptación de SEC-001A |
| 2026-07-25 | `pre-commit run --all-files`                                                                           | Passed  | Hooks de código, documentación, secretos y Compose verdes                                                         |

## Pause / Handoff Record

- Current state: la aplicación aplica `firm_id` en las principales features, pero el ticket todavía
  no cuenta con una matriz y cobertura negativa completa.
- Changed files and contracts: plan de tracking e índice de planes pendientes.
- Pending work: inventario, pruebas negativas faltantes, correcciones encontradas y validación total.
- Blockers or approvals: los resultados de IA dependen de una feature persistente futura.
- Residual risks: una operación derivada puede carecer de una prueba negativa aunque su servicio
  aplique actualmente el filtro.
- Next safe action: enumerar las operaciones tenant-owned desde routers y repositorios y marcar la
  cobertura existente por recurso.

## Completion Documentation Review

- [ ] Root and service READMEs reviewed.
- [ ] Backend operation and architecture docs reviewed.
- [ ] Frontend operation docs and inventories reviewed.
- [ ] Foundation status files reviewed and changed only if a foundation contract moved.
- [ ] AI governance docs, templates, and checklists reviewed.
- [ ] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Frontend operation contracts: no cambia comportamiento frontend durante la recuperación del plan.

## Completion Summary

- Delivered: plan de ejecución recuperado; implementación y validación final pendientes.
- Validation: revisión estática inicial, 444 pruebas backend con 100% de cobertura y pre-commit
  completo.
- Skipped validation: ninguna aplicable a la recuperación del tracking; la matriz y pruebas
  específicas del ticket siguen como trabajo pendiente, no como gates omitidos.
- Human approvals: no aplican para recuperar el tracking.
- Residual risk: cobertura negativa multi-despacho incompleta hasta ejecutar el plan.
