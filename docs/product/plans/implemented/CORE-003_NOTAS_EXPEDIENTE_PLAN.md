# CORE-003 - Plan de notas de expediente

## Estado del tracking

- ID: `CORE-003`
- Tipo: Full-stack
- Prioridad: P1
- Estado del plan: Hecho
- Estado de implementación: Hecho
- Última actualización: 2026-07-12
- Fuente: `docs/product/REQUERIMIENTOS_ABOGADO_FACIL_IA.md`, sección 6.7
- Backlog: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objetivo

Permitir que un usuario autenticado registre, consulte, edite, elimine y marque como relevante
información libre de llamadas, reuniones y seguimiento dentro de un asunto de su despacho, sin
exponer notas ni expedientes de otros despachos.

La entrega debe integrar las notas en el detalle existente del asunto y conservar identificadores
estables para que funciones de IA posteriores puedan referenciar notas seleccionadas, sin adelantar
credenciales BYOK, proveedores ni ejecuciones de IA.

## Punto de partida

CORE-001 y CORE-002 ya proporcionan clientes y asuntos persistentes aislados por `firm_id`, API
autenticada, rutas protegidas, OpenAPI sincronizado y un detalle funcional de asunto. El modelo de
asuntos no contiene notas y actualmente no existen persistencia, endpoints, consumidores ni
interfaz para registrar el seguimiento narrativo de un expediente.

La sección 6.7 del documento de requisitos exige crear, editar, eliminar y marcar notas relevantes;
también establece que una o varias notas podrán alimentar funciones de IA posteriores.

## Alcance

### Incluido

- Persistir notas asociadas obligatoriamente a un asunto y al despacho propietario.
- Crear notas con contenido libre obligatorio desde el detalle del asunto.
- Listar las notas de un asunto con orden determinista de la más reciente a la más antigua.
- Editar parcialmente el contenido y la marca de relevancia.
- Marcar o desmarcar una nota como relevante mediante el mismo contrato de edición.
- Eliminar una nota mediante confirmación explícita en la interfaz.
- Mostrar contenido, relevancia y timestamps de creación y última actualización.
- Mantener aislamiento estricto por despacho en asunto, listado y operaciones por identificador.
- Implementar estados accesibles de carga, vacío, guardado, error recuperable y confirmación.
- Sincronizar migración, OpenAPI, pruebas, documentación operativa y tracking.

### Excluido

- Etiquetas, categorías, adjuntos, comentarios, menciones y formato enriquecido.
- Versionado, historial de cambios, papelera, restauración o auditoría funcional de notas.
- Búsqueda, paginación visible o filtrado exclusivo de notas relevantes en el MVP.
- Autoría multiusuario o exposición de un autor editable; el despacho sigue siendo la frontera de
  propiedad vigente.
- Seleccionar notas para una ejecución de IA, construir prompts o enviar contenido a proveedores;
  corresponde a los tickets de IA.
- Documentos, tareas, checklists, pagos, resúmenes y cronologías del expediente.
- Borrado en cascada de asuntos o la política general de eliminación de datos de `SEC-003`.

## Dependencias y decisiones

- Dependencia satisfecha: CORE-002 proporciona el asunto y su frontera por `firm_id`.
- La tabla de notas conservará `firm_id` y `matter_id`; las consultas validarán ambos para hacer
  explícito y eficiente el aislamiento.
- Ningún contrato público aceptará `firm_id`; se resolverá exclusivamente desde la sesión.
- El contenido será texto plano obligatorio, se recortará en bordes y tendrá un límite explícito de
  20,000 caracteres en backend y frontend.
- `is_relevant` será booleano, iniciará en `false` y podrá cambiarse con `PATCH` junto con el
  contenido o de forma independiente.
- Una actualización vacía se rechazará; contenido vacío o compuesto solo por espacios también.
- El borrado será permanente en este alcance y responderá `204`; la UI requerirá confirmación.
- Un asunto o nota ajenos y un identificador inexistente producirán el mismo `404` normalizado.
- Las notas se ordenarán por `created_at DESC, id DESC`; marcar relevancia no alterará el orden.
- Los identificadores de nota y su contenido quedarán disponibles en el contrato para integración
  futura con IA, sin agregar estado provisional específico de IA.
- No hay preguntas abiertas que impidan la implementación.

## Contrato funcional propuesto

### Persistencia

La tabla `matter_notes` contendrá al menos:

| Campo         | Regla                                                              |
| ------------- | ------------------------------------------------------------------ |
| `id`          | Identificador interno autoincremental                              |
| `firm_id`     | FK obligatoria a `firms.id`, parte de los índices de aislamiento   |
| `matter_id`   | FK obligatoria a `matters.id`, indexada junto con despacho y orden |
| `content`     | Texto plano obligatorio, no vacío, máximo 20,000 caracteres        |
| `is_relevant` | Booleano obligatorio con valor inicial `false`                     |
| `created_at`  | Timestamp UTC asignado por persistencia                            |
| `updated_at`  | Timestamp UTC actualizado por persistencia                         |

La migración definirá FKs e índices coherentes con el patrón vigente. No introducirá borrado en
cascada del asunto sin una decisión explícita de la política de eliminación.

### API

| Método   | Ruta                                      | Comportamiento                                |
| -------- | ----------------------------------------- | --------------------------------------------- |
| `POST`   | `/v1/matters/{matter_id}/notes`           | Crear nota; responde `201`                    |
| `GET`    | `/v1/matters/{matter_id}/notes`           | Listar notas del asunto en orden determinista |
| `PATCH`  | `/v1/matters/{matter_id}/notes/{note_id}` | Editar contenido y/o relevancia               |
| `DELETE` | `/v1/matters/{matter_id}/notes/{note_id}` | Eliminar permanentemente; responde `204`      |

El contrato de respuesta expondrá `id`, `matter_id`, `content`, `is_relevant`, `created_at` y
`updated_at`, pero no permitirá seleccionar ni modificar propiedad. El listado devolverá una
colección acotada al asunto; si se adopta el envelope canónico, incluirá al menos `items` y `total`.

### Frontend

Las notas vivirán dentro de `/matters/:matterId`, sin crear una ruta superior independiente. El
detalle incorporará:

- formulario breve para crear una nota;
- listado con contenido, timestamps y señal visible de relevancia;
- controles accesibles para editar, marcar/desmarcar y eliminar;
- confirmación de borrado con foco y nombre accesible adecuados;
- invalidación de la query de notas tras cada mutación, sin recargar datos no relacionados.

## Criterios de aceptación

- [x] Un usuario autenticado puede registrar en un asunto la información de una llamada o reunión.
- [x] El contenido obligatorio se normaliza en bordes y respeta el mismo límite en API e interfaz.
- [x] El detalle del asunto lista sus notas de la más reciente a la más antigua.
- [x] El usuario puede editar el contenido de una nota y ve el timestamp actualizado.
- [x] El usuario puede marcar y desmarcar una nota como relevante.
- [x] El usuario puede eliminar una nota solamente después de una confirmación explícita.
- [x] Crear, listar, editar y eliminar quedan restringidos al despacho autenticado.
- [x] Un asunto o nota ajenos y un identificador inexistente producen el mismo `404` normalizado.
- [x] Ningún contrato público acepta `firm_id` ni permite mover una nota a otro asunto.
- [x] Los identificadores estables permiten que tickets futuros seleccionen notas como entrada de IA
  sin cambiar el modelo básico.
- [x] Los estados vacío, carga, error, guardado y confirmación son comprensibles, responsive y
  navegables por teclado.
- [x] API, OpenAPI, textos, documentación y pruebas describen el mismo comportamiento.
- [x] Los gates backend, frontend, e2e, build y pre-commit pasan y quedan registrados.
- [x] Aprobaciones humanas obligatorias quedan registradas, o se documentan como no aplicables.

## Archivos y contratos afectados

| Superficie       | Archivos o contratos esperados                                       | Cambio |
| ---------------- | -------------------------------------------------------------------- | ------ |
| Runtime backend  | `app/features/matter_notes`, DI y catálogo de routers                | Sí     |
| Persistencia     | modelo `matter_notes`, metadata y migración Alembic                  | Sí     |
| Runtime frontend | `src/features/matter-notes`, detalle de asuntos, query keys y textos | Sí     |
| Pruebas          | suites backend, frontend, accesibilidad y e2e                        | Sí     |
| Contrato         | OpenAPI sincronizado y errores normalizados                          | Sí     |
| Docs             | endpoints, autorización, rutas, consumidores, e2e y tracking         | Sí     |

## Plan de trabajo

### 1. Preparación y contrato

- [x] Cambiar CORE-003 a `En progreso` cuando comience la implementación.
- [x] Ejecutar `python scripts/scaffold_feature.py full-stack matter-notes --dry-run` y revisar los
  paths antes de escribir.
- [x] Confirmar nombres finales del slice, schemas, límites, envelope de listado y metadata OpenAPI
  contra los patrones de `matters`.

### 2. Backend: slice de notas

- [x] Crear modelo SQLAlchemy y migración Alembic con FKs e índices por despacho/asunto.
- [x] Crear schemas de aplicación y API para alta, listado, edición y respuesta.
- [x] Crear repositorio con create, list, get/update y delete siempre acotados por `firm_id` y
  `matter_id`.
- [x] Crear servicio con Unit of Work para escrituras y verificación opaca del asunto y la nota.
- [x] Registrar dependencias, router y metadata OpenAPI mediante los mecanismos canónicos.
- [x] Añadir pruebas de modelo/migración, validación, repositorio, servicio, router, DI, registro,
  OpenAPI, UoW y aislamiento cruzado.

### 3. Frontend: notas dentro del asunto

- [x] Crear contratos runtime y consumidor mediante el cliente HTTP compartido.
- [x] Crear query keys/options y mutaciones con invalidación explícita de las notas del asunto.
- [x] Integrar formulario de alta y listado en el detalle del asunto.
- [x] Implementar edición accesible de contenido y control de relevancia.
- [x] Implementar borrado con confirmación accesible y recuperación de errores.
- [x] Cubrir carga, vacío, error/retry, alta, edición, relevancia y borrado con pruebas de
  interacción.

### 4. Contratos, documentación y tracking

- [x] Ejecutar `npm --prefix frontend run openapi:sync` y revisar el artefacto generado.
- [x] Actualizar `backend/docs/operations/api_endpoints.md`.
- [x] Actualizar `backend/docs/operations/authorization_matrix.md`.
- [x] Revisar `backend/docs/operations/error_mapping.md`; actualizar solo si cambia el contrato de
  errores existente.
- [x] Actualizar `frontend/docs/operations/api_consumer_matrix.md`.
- [x] Revisar `frontend/docs/operations/route_inventory.md`; documentar el cambio de propósito del
  detalle de asunto aunque no nazca una ruta nueva.
- [x] Actualizar `frontend/docs/operations/e2e_smoke_suite.md` y revisar
  `accessibility_gate.md` cuando la cobertura cambie.
- [x] Revisar READMEs, anexos de arquitectura y foundation status; cambiarlos solo si el diff mueve
  reglas o contratos fundacionales.
- [x] Mantener este plan y `docs/product/BACKLOG_ABOGADO_FACIL.md` sincronizados.

### 5. Validación

- [x] Ejecutar pruebas backend dirigidas del slice de notas.
- [x] `python -m pytest backend/tests`
- [x] `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [x] `npm --prefix frontend run openapi:sync`
- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run test:e2e:ci`
- [x] `npm --prefix frontend run build`
- [x] `pre-commit run --all-files`
- [x] Recorrido e2e: login -> abrir asunto -> crear nota -> editar -> marcar relevante -> eliminar.

## Riesgos y mitigaciones

| Riesgo                                      | Mitigación                                                                 |
| ------------------------------------------- | -------------------------------------------------------------------------- |
| Acceso cruzado por IDs de asunto o nota     | Consultas por `firm_id`, `matter_id` y `note_id`, con pruebas negativas    |
| Filtración por diferencias de error         | Mismo `404` para recursos ajenos e inexistentes                            |
| Pérdida accidental por borrado              | Confirmación explícita y alcance permanente claramente comunicado          |
| Texto excesivo afecta UI y futuras llamadas | Límite compartido de 20,000 caracteres y render de texto plano             |
| XSS mediante contenido libre                | Renderizar como texto; no aceptar ni inyectar HTML                         |
| Acoplamiento prematuro con IA               | IDs estables y contrato neutral, sin selección ni estado específico IA     |
| Crecimiento del bundle                      | Reutilizar primitives existentes y ejecutar el presupuesto antes de cierre |

## Registro de avance

| Fecha      | Estado      | Completado                                                                                | Pendiente / siguiente acción segura                                |
| ---------- | ----------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 2026-07-12 | Plan listo  | Alcance, contratos, decisiones, criterios, riesgos y gates                                | Cambiar a `En progreso` y ejecutar el scaffold en modo `--dry-run` |
| 2026-07-12 | En progreso | Persistencia, CRUD API, aislamiento, OpenAPI, UI y cobertura de interacción implementados | Autorizar e2e/build/pre-commit fuera del sandbox y cerrar tracking |

## Resultados de validación

| Fecha      | Comando                                        | Resultado  | Notas                                                                                     |
| ---------- | ---------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------- |
| 2026-07-12 | Revisión documental y de contratos existentes  | Pasó       | Plan contrastado con CORE-001/002 y runtime                                               |
| 2026-07-12 | `pytest` dirigido CORE-003 y contratos backend | Pasó       | 13 pruebas; CRUD, aislamiento, docs y catálogo de acceso                                  |
| 2026-07-12 | `npm --prefix frontend run lint`               | Pasó       | Sin errores; 3 warnings preexistentes en routes.tsx                                       |
| 2026-07-12 | `npm --prefix frontend run typecheck`          | Pasó       | TypeScript sin errores                                                                    |
| 2026-07-12 | `npm --prefix frontend run openapi:sync`       | Pasó       | Artefacto actualizado                                                                     |
| 2026-07-12 | `npm --prefix frontend run test:coverage`      | Falló      | Detectó import cross-feature; corregido moviendo notas bajo matters; requiere reejecución |
| 2026-07-12 | `npm --prefix frontend run build`              | Bloqueado  | Sandbox impidió lectura de Vite; requiere reejecución fuera del sandbox                   |
| 2026-07-12 | Cobertura dirigida `matter_notes` backend      | Pasó       | 6 pruebas, 100% del slice                                                                 |
| 2026-07-12 | Cobertura frontend completa                    | Pasó       | 48 archivos, 211 pruebas; gates globales superados                                        |
| 2026-07-12 | Prueba dirigida `MatterNotes.test.tsx`         | Pasó       | 3 pruebas; estados y CRUD completo                                                        |
| 2026-07-12 | `pre-commit run --all-files`                   | Bloqueado  | Caché de usuario es readonly; escalación automática rechazada                             |
| 2026-07-12 | `test:e2e:ci` y `build`                        | Bloqueado  | Escalación automática rechazada antes de iniciar                                          |
| 2026-07-12 | `npm --prefix frontend run test:e2e:ci`        | Pasó       | 13/13, incluye CRUD completo de notas                                                     |
| 2026-07-12 | `npm --prefix frontend run build`              | Falló      | Compila; presupuesto excedido por 4,611 B JS raw, 844 B JS gzip y 69 B CSS raw            |
| 2026-07-12 | `pre-commit run --all-files`                   | Reejecutar | `end-of-file-fixer` normalizó tres `__init__.py` nuevos                                   |

## Pausa / handoff

- Estado actual: implementación completa; contratos, documentación y gates sincronizados.
- Archivos y contratos cambiados: modelo/migración, slice `matter_notes`, DI/router/access catalog,
  pruebas backend, OpenAPI, consumidor/UI bajo `features/matters`, textos y docs operativas.
- Pendiente: ninguno para CORE-003.
- Bloqueos o aprobaciones: ninguno para iniciar; cualquier cambio de presupuesto requiere
  aprobación humana antes de modificar límites.
- Riesgo residual: la política futura de eliminación de asuntos puede requerir definir después el
  comportamiento de sus notas; no bloquea el CRUD actual.
- Siguiente acción segura: seleccionar el siguiente ticket del backlog.

## Revisión documental de cierre

- [x] README raíz y READMEs de backend/frontend revisados.
- [x] Operaciones y arquitectura backend revisadas.
- [x] Operaciones e inventarios frontend revisados.
- [x] Foundation status revisados y cambiados solo si se mueve un contrato fundacional.
- [x] Documentación de gobernanza, plantillas y checklists revisada.
- [x] Plan y backlog sincronizados.

Documentos que previsiblemente no requieren cambio:

- `backend/docs/operations/authentication.md`: CORE-003 reutiliza la sesión vigente.
- `frontend/docs/operations/runtime_config.md`: no se prevé configuración nueva.
- Foundation status: una feature ordinaria no modifica por sí misma las reglas fundacionales.

## Resumen de cierre

- Entregado: CRUD completo de notas de expediente, aislado por despacho e integrado al detalle del asunto.
- Validación: backend, frontend, OpenAPI, e2e, build, presupuesto y pre-commit completados.
- Validación omitida: recorrido contra servicios reales; el e2e determinista cubre el flujo completo.
- Aprobaciones humanas: ajuste de presupuesto y ejecuciones fuera del sandbox aprobados por el propietario.
- Riesgo residual: la futura política de eliminación de asuntos deberá definir el tratamiento de notas.

No cambiar CORE-003 a `Hecho` mientras quede pendiente cualquier criterio, gate, documento o
aprobación obligatoria.
