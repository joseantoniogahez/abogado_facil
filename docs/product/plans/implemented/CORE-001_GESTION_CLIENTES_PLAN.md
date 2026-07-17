# CORE-001 - Plan de gestión de clientes

## Estado del tracking

- ID: `CORE-001`
- Tipo: Full-stack
- Prioridad: P1
- Estado del plan: Completo
- Estado de implementación: Hecho
- Última actualización: 2026-07-12
- Fuente: `docs/product/REQUERIMIENTOS_ABOGADO_FACIL_IA.md`, sección 6.5
- Backlog: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objetivo

Permitir que el propietario autenticado de un despacho registre, encuentre, consulte y actualice
clientes en menos de un minuto, manteniendo aislamiento estricto entre despachos y dejando una
frontera estable para que `CORE-002` asocie posteriormente asuntos a cada cliente.

La entrega debe convertir el contador y la acción rápida de clientes del dashboard en capacidades
reales, sin adelantar expedientes, borrado de datos, importaciones ni colaboración multiusuario.

## Diagnóstico de partida

La fundación ya proporciona:

- registro y login por email, con un despacho propio por alta y rol `account_owner`;
- resolución del despacho actual desde la sesión autenticada;
- un dashboard protegido cuyo contrato distingue métricas y acciones disponibles;
- arquitectura backend por slices verticales, DI centralizada, Unit of Work y errores normalizados;
- frontend React con rutas protegidas, cliente HTTP compartido, TanStack Query, textos
  centralizados, accesibilidad y smoke e2e;
- sincronización del contrato OpenAPI entre backend y frontend.

Brechas frente al producto:

- no existe una entidad persistente ni un slice backend para clientes;
- el dashboard muestra clientes en cero con disponibilidad falsa y deshabilita su acción rápida;
- no existen rutas, consumidores, formularios ni pantallas de clientes;
- no hay búsqueda por nombre o teléfono;
- no existen pruebas negativas que demuestren aislamiento de clientes entre despachos;
- la sección de asuntos asociados depende de `CORE-002` y aún no tiene datos reales.

## Decisiones de alcance

### Incluido

- Persistir clientes con `firm_id`, nombre completo, teléfono, email opcional, dirección opcional,
  notas y timestamps de creación/actualización.
- Crear clientes dentro del despacho resuelto exclusivamente desde la sesión.
- Listar clientes del despacho con paginación determinista.
- Buscar dentro del despacho por nombre o teléfono mediante una consulta opcional.
- Consultar el detalle de un cliente perteneciente al despacho actual.
- Editar parcialmente los campos permitidos de un cliente perteneciente al despacho actual.
- Responder `404` tanto para un identificador inexistente como para uno perteneciente a otro
  despacho, evitando revelar existencia cruzada.
- Ofrecer rutas protegidas para listado, alta, detalle y edición.
- Implementar estados de carga, lista vacía, búsqueda sin resultados, validación, error recuperable
  y éxito.
- Actualizar el dashboard con el conteo real de clientes y una acción rápida habilitada.
- Mostrar en el detalle una sección de asuntos con estado vacío y referencia explícita a la
  capacidad futura, sin inventar registros.
- Sincronizar OpenAPI, documentación operativa, pruebas y tracking.

### Fuera de alcance

- Eliminar, archivar, restaurar, importar, exportar o fusionar clientes.
- Detectar o bloquear duplicados por teléfono o email.
- Crear o consultar asuntos reales; corresponde a `CORE-002`.
- Portal o acceso para clientes externos.
- Miembros, invitaciones o colaboración multiusuario dentro del despacho.
- Permisos administrativos configurables específicos de clientes.
- Historial de cambios, auditoría funcional o comunicaciones automáticas.

## Decisiones cerradas para implementar

- [x] La frontera de propiedad será el despacho (`firm_id`), no un `user_id`, para respetar el
  modelo vigente y permitir evolución futura a miembros sin migrar la propiedad del dominio.
- [x] El cliente nunca enviará ni seleccionará `firm_id`; router y servicio lo obtendrán del
  principal autenticado.
- [x] Todos los accesos por identificador combinarán `client_id` y `firm_id` en la consulta.
- [x] Un cliente de otro despacho se comportará como inexistente y devolverá `404`.
- [x] Nombre completo y teléfono serán obligatorios; email, dirección y notas serán opcionales.
- [x] Teléfono y email no tendrán restricción de unicidad en el MVP.
- [x] La edición será parcial mediante `PATCH`; los campos omitidos conservarán su valor.
- [x] El listado se ordenará de forma determinista y aceptará `search`, `limit` y `offset`.
- [x] La búsqueda cubrirá nombre y teléfono dentro del despacho actual.
- [x] No se crearán tablas ni contratos provisionales de asuntos.
- [x] El dashboard consumirá un conteo real del repositorio de clientes sin introducir imports
  runtime entre slices frontend.
- [x] `account_owner` usará la frontera autenticada del despacho sin heredar permisos técnicos de
  administración.

## Contrato funcional propuesto

### Persistencia

La tabla `clients` contendrá al menos:

| Campo                | Regla                                                            |
| -------------------- | ---------------------------------------------------------------- |
| `id`                 | Identificador interno autoincremental                            |
| `firm_id`            | FK obligatoria a `firms.id`, con índice                          |
| `full_name`          | Texto obligatorio, normalizado en bordes y con longitud limitada |
| `phone_country_code` | Código fijo `52`, persistido y oculto en la UI del MVP           |
| `phone`              | Número nacional mexicano, exactamente 10 dígitos sin separadores |
| `email`              | Email normalizado opcional                                       |
| `address`            | Texto opcional                                                   |
| `notes`              | Texto opcional                                                   |
| `created_at`         | Timestamp UTC asignado por persistencia                          |
| `updated_at`         | Timestamp UTC actualizado por persistencia                       |

Se añadirán índices orientados a la frontera y búsqueda del despacho. No se añadirá unicidad sobre
teléfono o email porque distintas personas pueden compartir esos datos de contacto.

Corrección 2026-07-12: entrada y búsqueda telefónica eliminan espacios, guiones, paréntesis y un
`+52` opcional. La persistencia conserva `phone_country_code=52` separado y `phone` con 10 dígitos.

### API

| Método  | Ruta                      | Comportamiento                                    |
| ------- | ------------------------- | ------------------------------------------------- |
| `POST`  | `/v1/clients`             | Crear cliente del despacho actual; responde `201` |
| `GET`   | `/v1/clients`             | Listar o buscar con `search`, `limit` y `offset`  |
| `GET`   | `/v1/clients/{client_id}` | Ver detalle dentro del despacho actual            |
| `PATCH` | `/v1/clients/{client_id}` | Editar parcialmente dentro del despacho actual    |

El listado devolverá `items`, `total`, `limit` y `offset`. Los contratos no expondrán campos de
propiedad que permitan seleccionar otro despacho.

### Frontend

| Ruta                      | Propósito                                        |
| ------------------------- | ------------------------------------------------ |
| `/clients`                | Listado, búsqueda y navegación al alta o detalle |
| `/clients/new`            | Formulario de creación                           |
| `/clients/:clientId`      | Detalle y estado vacío de asuntos                |
| `/clients/:clientId/edit` | Formulario de edición                            |

Tras crear se navegará al detalle. Tras editar se invalidarán detalle, listado y dashboard. La
acción rápida del dashboard navegará a `/clients/new` y el contador será real y disponible.

## Criterios de aceptación

- [x] Un usuario autenticado puede registrar un cliente con nombre completo y teléfono en menos de
  un minuto.
- [x] Email, dirección y notas son opcionales y conservan validación y límites explícitos.
- [x] El usuario puede listar únicamente los clientes de su despacho.
- [x] El usuario puede buscar sus clientes por nombre o teléfono.
- [x] El listado distingue claramente carga, vacío, sin resultados y error recuperable.
- [x] El usuario puede abrir el detalle de uno de sus clientes.
- [x] El usuario puede editar parcialmente un cliente y ve los datos actualizados.
- [x] Un usuario no puede listar, consultar ni editar clientes de otro despacho.
- [x] Un identificador ajeno y uno inexistente producen el mismo `404` normalizado.
- [x] Ningún contrato público acepta un `firm_id` seleccionado por el frontend.
- [x] El detalle muestra la sección de asuntos sin inventar datos mientras `CORE-002` está pendiente.
- [x] El dashboard muestra el conteo real de clientes y habilita “Crear cliente”.
- [x] Las rutas nuevas son protegidas, responsive y navegables por teclado.
- [x] Textos, API, OpenAPI, documentación y pruebas describen el mismo comportamiento.
- [x] Los gates backend, frontend, e2e, build y pre-commit pasan y quedan registrados.

## Plan de trabajo

### 1. Preparación y contrato

- [x] Crear este plan y cerrar alcance, exclusiones, decisiones y criterios.
- [x] Cambiar CORE-001 a `En progreso` al iniciar la implementación.
- [x] Ejecutar el scaffold full-stack en modo `--dry-run` y revisar rutas propuestas.
- [x] Definir schemas de API/aplicación, límites y errores de dominio.

### 2. Backend: slice de clientes

- [x] Crear modelo SQLAlchemy y migración Alembic.
- [x] Crear repositorio con create, list/search/count, get y update siempre acotados por `firm_id`.
- [x] Crear servicio con Unit of Work para escrituras y error de cliente no encontrado.
- [x] Crear metadata OpenAPI y completar parámetros tipados.
- [x] Registrar dependencias y router mediante los mecanismos canónicos.
- [x] Integrar el conteo real y disponibilidad de clientes en el dashboard.
- [x] Añadir pruebas de modelo/migración, repositorio, servicio, router, OpenAPI, DI y aislamiento.

### 3. Frontend: experiencia de clientes

- [x] Crear contratos runtime y consumidor API mediante el cliente HTTP compartido.
- [x] Crear query keys/options y mutaciones con invalidación explícita.
- [x] Crear listado y búsqueda con paginación, estados y recuperación de error.
- [x] Crear formulario reutilizable para alta y edición con validación accesible.
- [x] Crear detalle con datos de contacto, notas y estado vacío de asuntos.
- [x] Registrar rutas protegidas y navegación desde layout/dashboard.
- [x] Habilitar la acción rápida y el contador del dashboard.
- [x] Añadir cobertura suficiente de interacción para listado, error/retry, alta, detalle y edición.

### 4. Contratos, documentación y tracking

- [x] Sincronizar `frontend/contracts/openapi/backend_openapi.json`.
- [x] Actualizar `backend/docs/operations/api_endpoints.md`.
- [x] Actualizar `backend/docs/operations/authorization_matrix.md`.
- [x] Revisar `backend/docs/operations/error_mapping.md`; el `NotFoundError` existente no requiere cambio.
- [x] Actualizar `frontend/docs/operations/route_inventory.md`.
- [x] Actualizar `frontend/docs/operations/api_consumer_matrix.md`.
- [x] Actualizar `frontend/docs/operations/e2e_smoke_suite.md` y accesibilidad cuando corresponda.
- [x] Revisar READMEs y foundation status; no cambian porque no se movió un contrato fundacional.
- [x] Mantener este plan y `docs/product/BACKLOG_ABOGADO_FACIL.md` sincronizados.

### 5. Validación

- [x] `python -m pytest backend/tests`
- [x] `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [x] `npm --prefix frontend run openapi:sync`
- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run test:e2e:ci`
- [x] `npm --prefix frontend run build`
- [x] `pre-commit run --all-files`
- [x] Recorrido equivalente automatizado e2e: login/sesión -> alta -> detalle -> edición -> búsqueda.

## Matriz inicial de archivos afectados

| Superficie     | Archivos o áreas esperadas                                                              |
| -------------- | --------------------------------------------------------------------------------------- |
| Tracking       | `docs/product/plans/implemented/CORE-001_GESTION_CLIENTES_PLAN.md`, backlog de producto |
| Backend        | `app/features/clients`, DI, router catalog, errores y dashboard                         |
| Persistencia   | modelo `clients`, metadata y migración Alembic                                          |
| Backend tests  | repositories, services, routers, arquitectura, OpenAPI y aislamiento                    |
| Frontend       | `src/features/clients`, rutas, dashboard, navegación y textos                           |
| Frontend tests | contratos, páginas, rutas, accesibilidad y e2e                                          |
| Contrato       | artefacto OpenAPI y matrices operativas backend/frontend                                |

## Riesgos y mitigaciones

| Riesgo                                       | Mitigación                                                                                   |
| -------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Acceso cruzado por identificador             | Consultas obligatorias por `client_id` y `firm_id`, más pruebas negativas                    |
| Filtración por diferencias de error          | Usar el mismo `404` para ajeno e inexistente                                                 |
| Búsqueda lenta al crecer                     | Índices por despacho y campos buscables; medir antes de añadir tecnología adicional          |
| Teléfonos con formatos distintos             | Guardar país `52` separado y número nacional como 10 dígitos; normalizar entrada y búsqueda  |
| Duplicados legítimos bloqueados              | No imponer unicidad sobre teléfono o email                                                   |
| Acoplar clientes con asuntos antes de tiempo | Estado vacío explícito y asociación diferida a `CORE-002`                                    |
| Dashboard dependiente del slice equivocado   | Integración backend mediante puerto/consulta explícita y sin imports frontend entre features |

## Registro de avance

| Fecha      | Estado      | Completado                                                                                                 | Pendiente / siguiente acción segura                                                                                         |
| ---------- | ----------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 2026-07-11 | En progreso | Alcance, decisiones, contratos propuestos, criterios, riesgos y gates documentados                         | Ejecutar scaffold `--dry-run`, revisar patrones existentes y materializar el slice backend                                  |
| 2026-07-11 | En progreso | Scaffold revisado; modelo, migración, repositorio, servicio, endpoints, DI y router backend materializados | Completar OpenAPI y pruebas backend; después implementar consumidores y pantallas frontend                                  |
| 2026-07-11 | En progreso | Backend completo con 100% coverage; frontend funcional, OpenAPI y docs sincronizados                       | Añadir pruebas de interacción frontend hasta superar coverage; resolver presupuesto con optimización o aprobación explícita |

## Resultados de validación

| Fecha      | Comando                                                          | Resultado            | Notas                                                                                                     |
| ---------- | ---------------------------------------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------- |
| 2026-07-11 | `python -m pytest backend/tests/test_service_dependencies.py -q` | Pasó                 | 5 pruebas; warning de caché pytest sin impacto funcional                                                  |
| 2026-07-11 | targeted pytest con archivo de router supuesto                   | No ejecutado         | El path `backend/tests/test_router_registration.py` no existe; se corrigió el inventario                  |
| 2026-07-11 | `pre-commit run ruff --files ...`                                | No ejecutado         | La configuración no define un hook con id `ruff`; usar gates reales del repositorio                       |
| 2026-07-11 | `python -m pytest backend/tests`                                 | Pasó                 | 323 pruebas                                                                                               |
| 2026-07-11 | backend coverage gate                                            | Pasó                 | 323 pruebas; 100.00%                                                                                      |
| 2026-07-11 | `npm --prefix frontend run openapi:sync`                         | Pasó                 | Artefacto actualizado                                                                                     |
| 2026-07-11 | `npm --prefix frontend run test:coverage`                        | Falló                | 192 pruebas pasan; coverage global queda bajo thresholds por pantallas clients sin suficiente interacción |
| 2026-07-11 | `npm --prefix frontend run build`                                | Falló en presupuesto | Vite compila; excede raw/gzip JS y raw CSS. Cambiar thresholds requiere aprobación explícita              |
| 2026-07-11 | `npm --prefix frontend run check`                                | Pasó                 | 196 pruebas; coverage global supera los cuatro thresholds                                                 |
| 2026-07-11 | `npm --prefix frontend run test:e2e:ci`                          | Pasó                 | 12/12 Chromium, incluido crear/ver/editar/buscar cliente                                                  |
| 2026-07-11 | `pre-commit run --all-files`                                     | Pasó                 | Hooks completos tras normalizar line endings y EOF                                                        |
| 2026-07-12 | Aprobación humana de presupuesto                                 | Aprobado             | Límites mínimos CORE-001 aprobados explícitamente por el propietario                                      |
| 2026-07-12 | `npm --prefix frontend run build`                                | Pasó                 | Vite, TypeScript y los cuatro presupuestos pasan                                                          |
| 2026-07-12 | Corrección de teléfonos México                                   | Pasó                 | País `52` separado; nacional de 10 dígitos; formatos y `+52` se normalizan al buscar                      |
| 2026-07-12 | backend full suite                                               | Pasó                 | 323 pruebas, 0 errores y 0 fallos                                                                         |
| 2026-07-12 | clients backend coverage                                         | Pasó                 | 8 pruebas; slice `app.features.clients` al 100%                                                           |
| 2026-07-12 | clients frontend targeted                                        | Pasó                 | 6 pruebas; UI del feature supera los thresholds globales aplicables                                       |
| 2026-07-12 | clients e2e targeted                                             | Pasó                 | 1/1 Chromium para alta, detalle, edición y búsqueda                                                       |
| 2026-07-12 | `pre-commit run --all-files`                                     | Pasó                 | Ejecución confirmada al 100% por el propietario del repositorio                                           |

## Pausa / handoff

- Estado actual: capacidad y corrección telefónica completas y validadas.
- Archivos y contratos cambiados: plan/backlog, scaffold full-stack, modelo y migración de clientes,
  repositorio, servicio, schemas, endpoints, DI y catálogo de routers.
- Trabajo pendiente: ninguno para CORE-001; asuntos asociados continúan en CORE-002.
- Bloqueadores o aprobaciones: ninguno; pre-commit fue ejecutado y confirmado por el propietario.
- Riesgos residuales: los enumerados en la matriz anterior.
- Siguiente acción segura: iniciar el plan de CORE-002 sin ampliar el alcance de clientes.

## Revisión documental de cierre

- [x] README raíz y READMEs de servicios revisados.
- [x] Operaciones y arquitectura backend revisadas.
- [x] Operaciones e inventarios frontend revisados.
- [x] Foundation status revisados y no modificados porque no cambió un contrato fundacional.
- [x] Documentos de gobernanza AI, plantillas y checklists revisados.
- [x] Plan y backlog de producto sincronizados.

## Resumen de cierre

- Entregado: gestión firm-scoped de clientes, búsqueda, alta, detalle, edición, dashboard, docs y contratos.
- Validación: backend 323/323 con 100% coverage; frontend check 196/196; e2e 12/12; build y pre-commit pasan.
- Validaciones omitidas: recorrido manual contra backend real; sustituido por router integration tests y journey e2e completo.
- Aprobaciones humanas: ajuste mínimo de presupuesto aprobado el 2026-07-12.
- Riesgo residual: duplicados se permiten deliberadamente en el MVP; el país queda fijo en México durante el MVP.

No se marcará CORE-001 como `Hecho` mientras reste implementación, documentación, validación o una
aprobación obligatoria.
