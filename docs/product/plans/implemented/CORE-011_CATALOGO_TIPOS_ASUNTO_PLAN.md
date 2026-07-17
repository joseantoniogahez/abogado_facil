# CORE-011 - Catálogo de tipos de asunto y checklists base

## Tracking Status

- ID: `CORE-011`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Hecho`
- Implementation status: `Hecho`
- Last updated: `2026-07-15`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Facilitar la clasificación consistente de los asuntos mediante un catálogo cerrado que enlace cada
tipo canónico con su checklist base y se persista en `matter_type` como string.

## Starting Point

`matter_type` es un string obligatorio y el frontend lo captura como texto libre. CORE-006 define
siete checklists estáticas en `backend/app/features/matter_checklists/templates.py`; la selección
depende de que el texto normalizado coincida exactamente con una clave. Un sinónimo o variación no
reconocida produce una checklist vacía, aunque el asunto admite elementos personalizados.

## Scope

### Included

- Definir en el backend un enumerador o constante equivalente con los siete tipos iniciales ya
  soportados y el valor adicional `Otro`.
- Usar el valor string del enumerador tanto como identidad canónica como valor persistido en la
  columna existente `matter_type`.
- Exponer el catálogo al frontend y usarlo al crear o editar un asunto.
- Mostrar un selector cerrado en el frontend; `Otro` es una opción fija y no habilita texto libre.
- Preservar asuntos existentes durante la transición al catálogo cerrado.
- Hacer que la inicialización de checklists use la identidad canónica elegida, evitando depender
  exclusivamente de coincidencias de texto libre.

### Excluded

- Constructor general de plantillas o checklists.
- Captura o edición libre del nombre de un tipo de asunto, incluso al elegir `Otro`.
- Crear, editar, compartir o eliminar tipos y plantillas reutilizables por usuario o despacho.
- Reemplazar los elementos personalizados que ya admite la checklist de cada asunto.
- Plantillas documentales de `DOC-001` y sugerencias de checklist mediante IA de `AI-203`.

## Dependencies and Decisions

- Dependencies: `CORE-002` y `CORE-006`, ambos completados.
- Decisions closed: para el MVP, el catálogo vive en una constante o enumerador del backend y es la
  fuente canónica de los valores permitidos.
- Decisions closed: `matter_type` continúa almacenándose como string en la base de datos; no se crea
  una tabla de catálogo ni se requiere una clave foránea.
- Decisions closed: el frontend muestra un selector cerrado y `Otro` es un valor fijo, no una salida
  de texto libre.
- Decisions closed: las definiciones reutilizables por usuario o despacho no forman parte de este
  ítem; deben evaluarse como un backlog posterior cuando exista evidencia de uso.
- Open questions: none.

## Acceptance Criteria

- [x] El usuario puede elegir uno de los siete tipos precargados o `Otro` al crear o editar un
  asunto.
- [x] Elegir un tipo precargado inicializa siempre la checklist base correspondiente, sin depender
  de acentos, mayúsculas o del texto visible.
- [x] Elegir `Otro` guarda exactamente ese valor y no muestra ni acepta un nombre personalizado.
- [x] El backend rechaza en alta y edición valores que no pertenezcan al enumerador.
- [x] Los asuntos existentes conservan su `matter_type` y sus checklists sin pérdida ni duplicados.
- [x] El catálogo backend es la fuente canónica de los valores permitidos y de su plantilla base.
- [x] Las definiciones globales no pueden ser modificadas por un usuario en este alcance.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface     | Expected files or contracts                                                     | Change required |
| ----------- | ------------------------------------------------------------------------------- | --------------- |
| Backend     | `features/matters`, `features/matter_checklists`, endpoint de catálogo, OpenAPI | yes             |
| Persistence | columna string existente `matters.matter_type`; revisión de datos previos       | review          |
| Frontend    | formulario de asuntos, consumidor del catálogo y textos                         | yes             |
| Tests       | suites backend/frontend; compatibilidad e idempotencia                          | yes             |
| Docs        | endpoints, consumidores, mutation policy y tracking                             | yes             |

## Work Plan

### Implementation

- [x] Crear el enumerador/constante backend con los siete tipos, `Otro` y sus checklists base.
- [x] Aplicar el enumerador a los contratos de alta y edición sin cambiar la columna string.
- [x] Exponer el catálogo con lectura autenticada y aislamiento/política coherentes con asuntos.
- [x] Sustituir el campo libre por un selector cerrado, incluido `Otro`, en alta y edición.
- [x] Definir y probar la compatibilidad de lectura para valores previos fuera del enumerador.
- [x] Preservar la inicialización perezosa e idempotente de CORE-006.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] `python -m pytest backend/tests`
- [x] `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [x] `npm --prefix frontend run openapi:sync`
- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run build`
- [x] Pre-commit on changed files.

## Progress Log

| Date       | State         | Completed                                                             | Pending / next safe action                             |
| ---------- | ------------- | --------------------------------------------------------------------- | ------------------------------------------------------ |
| 2026-07-14 | Plan prepared | Catálogo backend, persistencia string y selector cerrado aprobados    | Iniciar implementación del enumerador y sus contratos. |
| 2026-07-15 | Hecho         | Catálogo canónico, endpoint, selector, compatibilidad, pruebas y docs | Ninguno.                                               |

## Validation Results

| Date       | Command                                  | Result | Notes                                                    |
| ---------- | ---------------------------------------- | ------ | -------------------------------------------------------- |
| 2026-07-15 | `python -m pytest backend/tests`         | Pass   | 364 passed.                                              |
| 2026-07-15 | Backend coverage gate                    | Pass   | 100.00% coverage.                                        |
| 2026-07-15 | `npm --prefix frontend run openapi:sync` | Pass   | Artifact synchronized.                                   |
| 2026-07-15 | `npm --prefix frontend run check`        | Pass   | Lint, types, tests, OpenAPI and dependency gates passed. |
| 2026-07-15 | `npm --prefix frontend run build`        | Pass   | Build and performance budgets passed.                    |
| 2026-07-15 | `pre-commit run --all-files`             | Pass   | All hooks passed with lossless UTF-8 OpenAPI output.     |

## Pause / Handoff Record

- Current state: implementación, contratos, pruebas y documentación completos.
- Changed files and contracts: catálogo backend, contratos de asuntos, endpoint autenticado,
  OpenAPI, selector frontend, consumidores, pruebas y tracking.
- Pending work: none.
- Blockers or approvals: none; mandatory human approvals are not applicable.
- Residual risks: los valores históricos permanecen legibles y editables en otros campos, pero deben
  reemplazarse por una opción canónica para cambiar `matter_type`.
- Next safe action: none.

Update this section before every pause or partial handoff.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/service READMEs, architecture annexes, foundation status, route inventory, mutation policy,
  runtime configuration, accessibility, performance, observability and AI governance docs remain
  unchanged because no corresponding route, runtime, foundation, policy or governance rule moved.

## Completion Summary

- Delivered: catálogo inmutable de ocho tipos, endpoint autenticado, validación de escritura,
  selector cerrado y compatibilidad de lectura/edición para datos históricos.
- Validation: backend completo con 100% de cobertura; frontend check, build, OpenAPI y presupuesto
  de rendimiento aprobados.
- Skipped validation: e2e no aplica porque no cambiaron rutas, autenticación ni el pipeline de errores.
- Human approvals: not applicable.
- Residual risk: los tipos históricos sólo pueden mantenerse o sustituirse por un valor canónico.

Do not set the item to `Hecho` while any required criterion, validation, documentation update, or
approval remains incomplete.
