# PROD-003 - Plan del dashboard autenticado inicial

## Estado del tracking

- ID: `PROD-003`
- Tipo: Full-stack
- Prioridad: P1
- Estado del plan: Completado
- Estado de implementación: Hecho
- Última actualización: 2026-07-11
- Fuente: `docs/REQUERIMIENTOS_ABOGADO_FACIL_IA.md`, sección 6.4

## Objetivo

Convertir la bienvenida autenticada actual en el dashboard principal de Abogado Fácil para que el
usuario identifique de inmediato el estado de su despacho, los pendientes que requieren atención y
si la IA está configurada. La primera versión debe ser útil aun antes de que existan los módulos de
clientes, asuntos, tareas y BYOK, sin inventar actividad ni adelantar esos dominios.

## Diagnóstico de partida

La fundación ya proporciona:

- una ruta protegida `/welcome` que muestra el `display_name` de la sesión;
- un layout autenticado responsive con navegación principal y menú administrativo condicionado por
  permisos;
- sesión bearer, logout determinista, manejo normalizado de errores y diagnósticos por request ID;
- catálogo centralizado de textos, pruebas unitarias, accesibilidad, smoke e2e y presupuesto de
  bundle;
- aislamiento del usuario registrado mediante su despacho y rol `account_owner`.

Brechas frente al producto:

- `/welcome` solo muestra un saludo y el botón de logout;
- no existe un contrato backend de resumen de dashboard;
- todavía no existen los slices de clientes (`CORE-001`), asuntos (`CORE-002`), tareas
  (`CORE-007`) ni credenciales BYOK (`AI-001`/`AI-002`);
- no hay contadores, lista de próximos vencimientos, estado de IA ni acciones rápidas;
- los destinos posteriores al login y los fallbacks de autorización todavía usan `/welcome` como
  nombre técnico de la pantalla inicial;
- faltan contratos y pruebas para estados de carga, vacío, éxito parcial y error del dashboard.

## Decisiones de alcance

### Incluido

- Sustituir la experiencia de `/welcome` por un dashboard autenticado con saludo, resumen y
  navegación orientada al producto.
- Adoptar `/dashboard` como ruta canónica autenticada y mantener una redirección temporal de
  `/welcome` a `/dashboard` para no romper enlaces internos ni sesiones existentes durante el
  cambio.
- Mostrar tarjetas para clientes, asuntos activos y tareas pendientes.
- Mostrar una sección de tareas próximas o vencimientos con un estado vacío explícito.
- Mostrar el estado de configuración de IA con lenguaje claro y sin afirmar que una credencial fue
  validada cuando el módulo BYOK todavía no existe.
- Mostrar accesos rápidos a crear cliente, crear asunto y analizar relato inicial; mientras sus
  tickets no estén implementados, deben aparecer deshabilitados o identificados como próximos, sin
  navegar a rutas inexistentes.
- Incorporar un contrato backend de solo lectura para el resumen, autenticado y limitado al
  despacho actual, preparado para que los slices futuros aporten datos reales.
- Tratar la ausencia de módulos de dominio como disponibilidad conocida, no como un error ni como
  datos simulados.
- Cubrir diseño responsive, accesibilidad, carga, vacío, respuesta válida, sesión expirada y error
  recuperable.

### Fuera de alcance

- CRUD de clientes, asuntos o tareas, cubierto por `CORE-001`, `CORE-002` y `CORE-007`.
- Persistencia, cifrado o validación de credenciales BYOK, cubiertos por `AI-001` y `AI-002`.
- Análisis real de relatos, cubierto por `AI-101`.
- Notificaciones push, sincronización de calendario o recordatorios automáticos.
- Métricas financieras, gráficas, actividad histórica o personalización de widgets.
- Cambios a roles administrativos o ampliación de privilegios de `account_owner`.

## Decisiones cerradas para implementar

- [x] El dashboard será la pantalla inicial canónica después del login en `/dashboard`.
- [x] `/welcome` quedará como redirección temporal a `/dashboard`; no mantendrá una segunda
  implementación de la pantalla.
- [x] No se mostrarán datos de ejemplo como si pertenecieran al usuario.
- [x] Los módulos todavía no materializados se representarán con cero y/o disponibilidad explícita,
  según el contrato final, y sus acciones rápidas no abrirán rutas inexistentes.
- [x] El resumen se obtendrá mediante un endpoint agregado de solo lectura para evitar múltiples
  solicitudes y mantener el objetivo de respuesta menor a dos segundos en uso normal.
- [x] El endpoint resolverá el despacho desde la identidad autenticada; el cliente no enviará un
  `firm_id` seleccionable.
- [x] La implementación inicial no agregará tablas de clientes, asuntos, tareas o IA ni dependencias
  especulativas.

## Contrato funcional propuesto

La respuesta de resumen deberá distinguir valores reales de capacidades todavía no disponibles. La
forma definitiva se cerrará en schemas/OpenAPI, pero debe expresar al menos:

- conteo de clientes;
- conteo de asuntos activos;
- conteo de tareas pendientes;
- colección ordenada y limitada de próximas tareas o vencimientos;
- estado de IA: `not_available`, `not_configured`, `configured` o `error`;
- disponibilidad de cada módulo/acción para que el frontend no deduzca capacidades a partir de un
  conteo igual a cero.

Cuando un slice futuro se incorpore, será responsable de aportar sus datos al resumen respetando la
frontera de despacho. Hasta entonces, el endpoint devolverá estados vacíos deterministas y
disponibilidad falsa, nunca registros ficticios.

## Criterios de aceptación

- [x] Un usuario autenticado llega a `/dashboard` después de iniciar sesión.
- [x] Visitar `/welcome` redirige a `/dashboard` sin perder la sesión.
- [x] Un visitante no autenticado que intenta abrir `/dashboard` es enviado al login por la política
  protegida existente.
- [x] El dashboard saluda con el `display_name` y contextualiza el despacho actual.
- [x] Se muestran contadores identificables para clientes, asuntos activos y tareas pendientes.
- [x] Se muestra una sección de próximas tareas o vencimientos, incluido un estado vacío claro.
- [x] Se muestra el estado de IA sin exponer secretos ni confundir `no disponible` con
  `configurada`.
- [x] Las acciones rápidas de funcionalidades pendientes están deshabilitadas o marcadas como
  próximas y no conducen a 404.
- [x] La respuesta backend solo contiene datos del despacho de la sesión y no acepta seleccionar el
  despacho mediante parámetros del cliente.
- [x] Carga, vacío, error recuperable y sesión expirada tienen comportamiento visible y probado.
- [x] Los errores conservan el contrato normalizado y el diagnóstico por request ID.
- [x] La pantalla funciona en viewport móvil y escritorio, navegación por teclado y controles de
  accesibilidad existentes.
- [x] El resumen responde en menos de dos segundos en uso normal y no genera una cascada de
  solicitudes por tarjeta.
- [x] Backend, frontend, OpenAPI, documentación y pruebas describen el mismo contrato.

## Plan de trabajo

### 1. Materializar contrato y navegación

- [x] Definir el schema definitivo del resumen, estados de disponibilidad y semántica de los
  contadores.
- [x] Definir el endpoint `GET /v1/dashboard` y su acceso autenticado limitado al despacho actual.
- [x] Registrar `/dashboard` como ruta protegida canónica.
- [x] Convertir `/welcome` en redirección temporal y actualizar login, landing autenticada, perfil,
  navegación y fallbacks de permisos.
- [x] Definir la política de retiro de la redirección legado en un ticket posterior, sin mantener
  dos páginas equivalentes.

### 2. Backend: resumen del despacho

- [x] Crear el slice vertical `dashboard` con router, service, repository si resulta necesario,
  schemas y metadata OpenAPI.
- [x] Resolver usuario y despacho exclusivamente desde la sesión autenticada.
- [x] Entregar valores vacíos deterministas para dominios aún no implementados y hacer explícita su
  disponibilidad.
- [x] Preparar puertos o consultas de agregación mínimas para que clientes, asuntos, tareas y BYOK
  puedan integrarse después sin dependencias cruzadas indebidas.
- [x] Mantener errores normalizados y autorización de lectura explícita.
- [x] Añadir pruebas de service, router, aislamiento por despacho, contrato OpenAPI y política de
  acceso.

### 3. Frontend: dashboard de producto

- [x] Crear `features/dashboard` y retirar la responsabilidad visual de `features/welcome`.
- [x] Crear contrato/parser y consumidor del resumen mediante el cliente HTTP compartido.
- [x] Consultar el resumen con política explícita de caché, retry y refetch.
- [x] Implementar saludo, tarjetas de métricas, próximos pendientes, estado de IA y acciones
  rápidas.
- [x] Implementar estados de carga, vacío, no disponible y error recuperable con request ID.
- [x] Mantener logout accesible desde el layout o dashboard sin duplicar el manejo de sesión.
- [x] Añadir pruebas unitarias, de rutas, navegación, responsive y accesibilidad.

### 4. Contratos, documentación y tracking

- [x] Sincronizar el artefacto OpenAPI del frontend.
- [x] Actualizar `backend/docs/operations/api_endpoints.md` y
  `backend/docs/operations/authorization_matrix.md`.
- [x] Actualizar `frontend/docs/operations/route_inventory.md`,
  `api_consumer_matrix.md`, `mutation_policy.md` si cambia el consumidor de logout y
  `e2e_smoke_suite.md`.
- [x] Actualizar pruebas de contrato documental y todas las referencias canónicas de `/welcome`.
- [x] Actualizar `docs/BACKLOG_ABOGADO_FACIL.md` a `En progreso` al comenzar implementación y a
  `Hecho` únicamente tras cumplir todos los gates.
- [x] Mantener este archivo al día con avances, decisiones, validaciones y riesgos.

#### Archivos Markdown requeridos para el cierre

PROD-003 no podrá marcarse como `Hecho` hasta revisar y, cuando aplique, actualizar estos archivos:

- `docs/PROD-003_DASHBOARD_PLAN.md`: estado, criterios, avance, validaciones y riesgos residuales.
- `docs/BACKLOG_ABOGADO_FACIL.md`: transición de `En progreso` a `Hecho` solo al superar los gates.
- `backend/docs/operations/api_endpoints.md`: contrato de `GET /v1/dashboard`.
- `backend/docs/operations/authorization_matrix.md`: clasificación de acceso autenticado y frontera de despacho.
- `backend/docs/operations/authentication.md`: destino canónico posterior al login, si el contrato lo documenta.
- `frontend/docs/operations/route_inventory.md`: `/dashboard`, redirección legado y fallbacks.
- `frontend/docs/operations/api_consumer_matrix.md`: consumidor y manejo de errores de `/dashboard`.
- `frontend/docs/operations/e2e_smoke_suite.md`: recorridos de login, redirección, error y logout.
- `frontend/docs/operations/accessibility_gate.md`: cobertura accesible del dashboard y sus estados.
- `frontend/docs/operations/performance_budget.md`: impacto medido del nuevo feature si resulta material.

Se revisarán, pero solo se modificarán si cambian sus reglas o contratos:

- `backend/docs/foundation_status.md`.
- `frontend/docs/foundation_status.md`.
- `frontend/docs/operations/api_contract_sync.md`.
- `frontend/docs/operations/mutation_policy.md`.
- `frontend/docs/operations/runtime_error_pipeline.md`.
- `frontend/docs/operations/observability_events.md`.

### 5. Validación

- [x] `python -m pytest backend/tests`
- [x] `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [x] `npm --prefix frontend run openapi:sync`
- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run test:e2e:ci`
- [x] `npm --prefix frontend run build`
- [x] `pre-commit run --all-files`
- [x] Probar manualmente login -> dashboard -> estado vacío -> navegación -> logout con el stack
  local si Docker está disponible.

## Matriz inicial de archivos afectados

| Superficie        | Archivos o áreas esperadas                                            |
| ----------------- | --------------------------------------------------------------------- |
| Backend dashboard | slice `dashboard`, DI, router registration, OpenAPI y pruebas         |
| Autorización      | catálogo/política de lectura autenticada y pruebas de aislamiento     |
| Frontend          | feature dashboard, consumidor API, textos, componentes y pruebas      |
| Navegación        | rutas, login, landing, perfil, layout y fallbacks de permisos         |
| Contrato          | schemas backend, parser frontend y artefacto OpenAPI                  |
| Calidad           | pruebas unitarias, integración, accesibilidad, smoke e2e y bundle     |
| Docs              | endpoints, autorización, rutas, consumidores, e2e, backlog y tracking |

La lista es orientativa; no autoriza implementar los módulos legales o de IA que pertenecen a
tickets posteriores.

## Riesgos y mitigaciones

| Riesgo                                                   | Mitigación prevista                                                   |
| -------------------------------------------------------- | --------------------------------------------------------------------- |
| Mostrar actividad ficticia antes de tener módulos reales | Estados vacíos y disponibilidad explícita; sin fixtures en producción |
| Confundir cero con módulo disponible                     | Campo de disponibilidad separado del valor del contador               |
| Crear dependencias cruzadas entre features               | Contrato agregado y puertos/consultas respetando slices verticales    |
| Acceso a métricas de otro despacho                       | Resolver despacho desde sesión y añadir pruebas negativas             |
| Romper enlaces y fallbacks basados en `/welcome`         | Redirección temporal y actualización exhaustiva de referencias        |
| Cascada de solicitudes y dashboard lento                 | Un endpoint agregado, payload acotado y prueba de comportamiento      |
| Acción rápida hacia funcionalidad inexistente            | Control deshabilitado o “próximamente”, sin rutas placeholder         |
| Deriva entre backend, OpenAPI y consumidor               | Sync inmediato y pruebas de contrato en el mismo cambio               |

## Dependencias y evolución

- `CORE-001` conectará el conteo de clientes y habilitará “Crear cliente”.
- `CORE-002` conectará asuntos activos y habilitará “Crear asunto”.
- `CORE-007` aportará tareas pendientes y próximos vencimientos.
- `AI-001`/`AI-002` sustituirán `not_available` por el estado BYOK persistido.
- `AI-101` habilitará “Analizar relato inicial”.

Estas dependencias no bloquean la estructura inicial, pero sí bloquean datos y acciones reales de
sus respectivos módulos.

## Registro de avance

| Fecha      | Estado      | Nota                                                                                                                                                                        |
| ---------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-07-10 | Plan listo  | Se auditó la bienvenida, navegación, contratos disponibles y orden del backlog; se definieron alcance, estados vacíos, contrato propuesto y gates.                          |
| 2026-07-11 | En progreso | Se inició la implementación full-stack, se revisaron playbooks y contratos afectados, y se explicitó el inventario Markdown de cierre.                                      |
| 2026-07-11 | En progreso | Se materializó el contrato inicial, router, servicio, consumidor, UI y ruta canónica; validaciones enfocadas detectaron ajustes menores en curso.                           |
| 2026-07-11 | En progreso | Backend y frontend funcionales; 314 backend y 187 frontend tests verdes, e2e 10/10. Pendiente cerrar cobertura backend y presupuesto de bundle.                             |
| 2026-07-11 | En progreso | Se autorizó ajustar el presupuesto JS a 395000 raw y 117000 gzip; Docker quedó disponible para repetir los gates finales.                                                   |
| 2026-07-11 | Hecho       | Gates completos, smoke e2e 11/11 y validación real con Docker de frontend, registro, login y resumen autenticado del despacho.                                              |
| 2026-07-11 | Hecho       | Corrección documental posterior al cierre: se explicitó en `authentication.md` que `/dashboard` es el destino canónico tras el login y `/welcome` una redirección temporal. |

## Resultado de validaciones

Estado al 2026-07-11:

- `npm --prefix frontend run openapi:sync`: completado; artefacto actualizado.
- `python -m pytest backend/tests`: completado, `315 passed`.
- `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`:
  completado, `315 passed`, cobertura `100.00%`.
- `npm --prefix frontend run check`: completado, `187 passed`, cobertura y auditoría de
  dependencias aprobadas.
- `npm --prefix frontend run test:e2e:ci`: completado, `11 passed`.
- `npm --prefix frontend run build`: completado; `392774 B` raw y `116209 B` gzip dentro del
  presupuesto autorizado.
- `pre-commit run --all-files`: completado; todos los hooks pasaron con Docker disponible.
- `docker compose config -q`: completado.
- Stack local: frontend y API respondieron `200`; registro, login y `GET /v1/dashboard` reales
  devolvieron el despacho de la sesión, contadores vacíos, IA `not_available` y tres acciones.

`PROD-003` queda `Hecho` sin riesgos residuales que bloqueen el cierre. Los slices futuros
conectarán datos reales conforme a la sección de dependencias.
