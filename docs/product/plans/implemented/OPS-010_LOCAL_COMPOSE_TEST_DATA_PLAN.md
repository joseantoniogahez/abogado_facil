# OPS-010 - Datos de prueba locales con Docker Compose

## Tracking Status

- ID: `OPS-010`
- Type: `Ops`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-08-02`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Disponer de un script manual para crear datos deterministas dentro del contenedor backend después
de levantar el stack local con Docker Compose, sin ejecutar el sembrado automáticamente durante el
build o el arranque ni permitirlo en test, staging o producción.

## Starting Point

- La imagen backend ejecuta `alembic upgrade head` desde `backend/prestart.sh` antes de iniciar
  FastAPI.
- `compose.override.yaml` configura el flujo local cargado automáticamente por `docker compose up`.
- No existe un script local para sembrar datos funcionales del producto bajo demanda.
- El catálogo canónico actual contiene ocho tipos en
  `backend/app/core/common/matter_types.py`.

## Scope

### Included

- Mantener en un archivo JSON versionado todos los valores editables usados por el sembrado.
- Crear dos usuarios de prueba, cada uno asociado a su propio despacho.
- Crear dos clientes para cada usuario/despacho, cuatro clientes en total.
- Crear para cada cliente un asunto de cada tipo canónico: 8 asuntos por cliente y 32 asuntos en
  total con el catálogo actual.
- Llenar todos los campos deterministas disponibles de usuario, despacho, cliente y asunto,
  incluidos estado, contraparte, descripción, siguiente acción y fecha de siguiente acción.
- Excluir datos generados por IA y no crear credenciales BYOK, ejecuciones, resultados, revisiones,
  feedback ni otros registros cuya fuente deba ser una función de IA.
- Proveer un comando manual ejecutable dentro del contenedor backend después de que las
  migraciones estén disponibles, por ejemplo
  `docker compose exec backend python -m app.core.db.local_seed`.
- Hacer el sembrado normal idempotente para que repetir el comando no duplique registros.
- Ofrecer un argumento manual `--reset`, destructivo y exclusivo de local, para limpiar y volver a
  sembrar en una sola ejecución explícita.

### Excluded

- Ejecutar el sembrado durante `docker compose build` o dentro del `Dockerfile`.
- Ejecutar el sembrado automáticamente durante `docker compose up` o cada reinicio del backend.
- Sembrar datos en `APP_ENV=test`, `staging`, `prod` o `production`.
- Generar contenido por medio de un proveedor de IA.
- Agregar claves API reales, secretos o datos personales reales al JSON.
- Cambiar el catálogo de tipos de asunto como parte de este ticket.

## Seed Dataset Contract

- Conteos esperados con el catálogo actual:
  - 2 usuarios y 2 despachos.
  - 2 clientes por usuario/despacho; 4 clientes en total.
  - 1 asunto de cada uno de los 8 tipos por cliente; 32 asuntos en total.
- Tipos requeridos:
  - `Pensión alimenticia`.
  - `Divorcio básico`.
  - `Despido / asunto laboral inicial`.
  - `Cobro de deuda`.
  - `Convenio de pago`.
  - `Arrendamiento`.
  - `Sucesorio básico`.
  - `Otro`.
- El cargador debe validar el JSON antes de escribir y fallar con un mensaje accionable si faltan
  usuarios, clientes, tipos o campos obligatorios.
- El cargador debe comprobar que los tipos declarados en el JSON coincidan con el catálogo
  canónico para detectar drift cuando se agregue o elimine un tipo.
- Las contraseñas del fixture deben ser exclusivamente locales, documentadas y marcadas para que
  los detectores de secretos no las confundan con credenciales reales.

## Dependencies and Decisions

- Dependencies: esquema vigente de usuarios/despachos, clientes y asuntos; migraciones Alembic;
  catálogo `MatterType`.
- Decisions closed:
  - El sembrado se solicita manualmente dentro del contenedor backend después de levantar el stack
    y completar migraciones. No ocurre durante el build ni el arranque automático.
  - El modo normal es idempotente y conserva datos locales existentes.
  - El argumento `--reset` permite limpiar los datos de aplicación del entorno local y recrear el
    fixture sin depender de una bandera persistente en `.env`.
  - Tanto el sembrado como `--reset` deben exigir `APP_ENV=local` dentro del proceso. Si no es
    local, deben abortar antes de borrar o insertar aunque el script exista dentro de la imagen.
  - El reset se ejecuta en una transacción y debe documentarse como destructivo.
  - El JSON será la fuente de valores; el código no duplicará nombres, correos, clientes o asuntos.
- Open questions: none.

## Acceptance Criteria

- [x] Después de `docker compose up`, el comando manual dentro del backend ejecuta el sembrado con
  `APP_ENV=local`.
- [x] El sembrado crea exactamente 2 usuarios, 2 despachos, 4 clientes y 32 asuntos con el catálogo
  actual.
- [x] Cada usuario tiene 2 clientes y cada cliente tiene exactamente un asunto de cada tipo
  canónico.
- [x] Los campos deterministas de todos los registros están llenos y no se crean datos propios de
  flujos de IA.
- [x] Los valores del fixture viven en un JSON versionado que puede modificarse sin cambiar el
  código del sembrador.
- [x] Una segunda ejecución sin `--reset` no duplica los datos sembrados ni borra datos existentes.
- [x] El argumento `--reset` limpia y vuelve a sembrar únicamente cuando `APP_ENV=local`, con una
  advertencia destructiva documentada.
- [x] El sembrado y el reset rechazan explícitamente cualquier ambiente distinto de local.
- [x] Build, arranque, test y producción no ejecutan automáticamente ni requieren el sembrado.
- [x] Un JSON inválido o desalineado con el catálogo no produce un sembrado parcial.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface             | Expected files or contracts                                                                 | Change required |
| ------------------- | ------------------------------------------------------------------------------------------- | --------------- |
| Runtime             | configuración `APP_ENV` y acceso manual al contenedor backend                               | review          |
| Seed implementation | `backend/app/core/db/` and a JSON fixture under that runtime package                        | yes             |
| Container           | `backend/Dockerfile` or backend image contents, only if the chosen fixture path requires it | review          |
| Tests               | backend seed tests and Compose/documentation contract tests                                 | yes             |
| Docs                | `README.md`, `backend/README.md`, affected backend operation docs                           | yes             |
| Foundation status   | `backend/docs/foundation_status.md`                                                         | review only     |

## Work Plan

### Implementation

- [x] Definir el schema del JSON y crear el fixture con los 2 usuarios, 4 clientes y 32 asuntos.
- [x] Implementar carga, validación integral y mensajes de error sin secretos.
- [x] Implementar upsert idempotente con identificadores naturales estables del fixture.
- [x] Implementar el argumento `--reset` con limpieza transaccional protegida por `APP_ENV=local`,
  respetando claves foráneas y tablas relacionadas.
- [x] Asegurar que el módulo y el JSON estén disponibles dentro del contenedor backend, sin
  invocarlos desde el build, el entrypoint ni el arranque de Compose.

### Tests and Documentation

- [x] Probar los conteos, relaciones, cobertura completa del catálogo y campos deterministas.
- [x] Probar idempotencia ejecutando dos veces el sembrador.
- [x] Probar rollback ante JSON inválido o error de persistencia.
- [x] Probar que seed y reset son rechazados fuera de `APP_ENV=local`.
- [x] Probar el reset local y que no queden datos anteriores de las tablas incluidas.
- [x] Documentar los comandos manuales de sembrado y `--reset` con advertencia destructiva.
- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] `docker compose config`
- [x] `docker compose -f compose.yaml -f compose.prod.yaml config`
- [x] `docker compose up --build`, ejecución manual del script y verificación de conteos en una
  base local desechable.
- [x] Segunda ejecución manual y verificación de ausencia de duplicados.
- [x] Ejecución manual controlada con `--reset` y verificación del nuevo sembrado.
- [x] `.\.venv\Scripts\python.exe -m pytest backend/tests`
- [x] `.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [x] `.\.venv\Scripts\python.exe -m pre_commit run --all-files`

## Progress Log

| Date       | State         | Completed                                                                         | Pending / next safe action                                                    |
| ---------- | ------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 2026-08-02 | Plan prepared | Dataset, manual local execution, idempotency and `--reset` contract documented.   | Review affected data relationships, then implement the JSON schema and tests. |
| 2026-08-02 | In progress   | Backend relationships, runtime guard, fixture packaging and reset scope reviewed. | Implement the validated JSON fixture, seed transaction and focused tests.     |
| 2026-08-02 | Complete      | Fixture, seed, local-only reset, tests, docs and Docker validation completed.     | None; ready for normal repository delivery.                                   |

## Validation Results

| Date       | Command                                                                                                                    | Result | Notes                                                   |
| ---------- | -------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------- |
| 2026-08-02 | `.\.venv\Scripts\python.exe -m pytest backend/tests`                                                                       | Pass   | 610 tests passed.                                       |
| 2026-08-02 | `.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Pass   | 610 tests and 100% coverage.                            |
| 2026-08-02 | `docker compose config -q` and production overlay config                                                                   | Pass   | Local and production configurations are valid.          |
| 2026-08-02 | `docker compose up --build -d`                                                                                             | Pass   | The backend image contains the module and JSON fixture. |
| 2026-08-02 | Seed twice, seed with `--reset`, then PostgreSQL counts                                                                    | Pass   | Counts: 2 users, 2 firms, 4 clients and 32 matters.     |
| 2026-08-02 | `.\.venv\Scripts\python.exe -m pre_commit run --all-files`                                                                 | Pass   | All configured hooks passed on the final worktree.      |

## Pause / Handoff Record

- Current state: implementación, documentación y validaciones completas.
- Changed files and contracts: fixture y utilidad local bajo `app/core/db`, pruebas, READMEs,
  backlog e índices de planes.
- Pending work: none.
- Blockers or approvals: none; no mandatory human approval applies.
- Residual risks: `--reset` es destructivo por diseño y debe usarse sólo en el perfil local.
- Next safe action: entregar los cambios mediante el flujo normal del repositorio.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Backend operation and architecture docs: unchanged because no endpoint, auth, RBAC, error, DI,
  UoW, router or OpenAPI contract changed.
- Frontend docs: unchanged because the utility has no frontend consumer or route.
- Foundation status: unchanged because no foundation rule or validation gate changed.
- AI governance docs: unchanged because the fixture excludes all AI-owned records.

## Completion Summary

- Delivered: local-only validated JSON fixture, idempotent manual seed and guarded transactional reset.
- Validation: backend suite and coverage, Compose configs, live Docker seed/idempotency/reset/counts,
  and all pre-commit hooks passed.
- Skipped validation: none.
- Human approvals: not applicable.
- Residual risk: intentional destructive behavior of the explicitly documented `--reset` option.

Use `Implementado` when engineering is complete but a mandatory release gate or external approval
remains. Do not set the item to `Hecho` while any required criterion, validation, documentation
update, gate, or approval remains incomplete.
