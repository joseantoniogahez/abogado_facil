# PROD-002 - Plan de alineación de autenticación

## Estado del tracking

- ID: `PROD-002`
- Tipo: Full-stack
- Prioridad: P1
- Estado del plan: Listo para implementación
- Estado de implementación: Hecha; validación final completada
- Última actualización: 2026-07-10
- Fuente: `docs/product/REQUERIMIENTOS_ABOGADO_FACIL_IA.md`, sección 6.2

## Objetivo

Alinear la autenticación existente con la cuenta de producto de Abogado Fácil para que una persona
pueda registrarse con email y contraseña, iniciar y cerrar sesión, conservar una sesión segura y
consultar o editar un perfil básico. Cada alta crea un despacho propio cuyo nombre efectivo nunca
es nulo y asigna al usuario el rol `account_owner` limitado a ese despacho.

## Diagnóstico de partida

La fundación ya proporciona:

- registro público en `POST /v1/users/register`;
- login OAuth2 en `POST /v1/token`;
- lectura y actualización de cuenta en `GET/PATCH /v1/users/me`;
- logout local y sesión protegida en frontend;
- políticas de contraseña, normalización de errores, JWT y pruebas unitarias/e2e.

Brechas frente al producto:

- la identidad de acceso actual es `username`, no email;
- el modelo y los contratos no incluyen nombre de despacho;
- el registro público no asigna explícitamente el rol inicial de propietario de cuenta;
- la experiencia y los textos siguen exponiendo conceptos de la fundación (`username`,
  `/welcome`) en vez de una cuenta de Abogado Fácil;
- falta una prueba e2e que recorra registro, login, perfil y logout como un solo journey;
- recuperación de contraseña no tiene proveedor de correo/autenticación definido.

## Decisiones de alcance

### Incluido

- Usar email normalizado como identificador único de registro e inicio de sesión.
- Persistir `first_name` y `last_name` obligatorios, `middle_name` opcional y `display_name`
  obligatorio. El cliente precarga `display_name` con los componentes del nombre, pero permite
  personalizarlo. `firm_name` usa `display_name` como fallback.
- Crear exactamente un despacho por cada alta pública y asociarlo al nuevo usuario.
- Asignar a cada alta pública el rol `account_owner`, limitado al despacho creado y sin herencia ni
  permisos del rol administrativo técnico.
- Mantener login con bearer JWT y almacenamiento de sesión actual, salvo que el análisis de
  seguridad durante la implementación detecte un incumplimiento concreto.
- Alinear formularios, contratos, textos, navegación, errores y pruebas.
- Partir del contrato nuevo de email sin alias de username ni transformación de datos legados,
  porque el proyecto todavía no tiene usuarios.

### Fuera de alcance

- Recuperación de contraseña hasta elegir proveedor de email o autenticación.
- Verificación de email, MFA, OAuth social y refresh tokens.
- Gestión de miembros de despacho o invitaciones.
- Dashboard funcional de producto, cubierto por `PROD-003`.
- Cambios a módulos legales o BYOK.

## Decisiones cerradas para implementar

- [x] `DEC-009`: el rol público es `account_owner`, limitado al despacho propio y sin herencia del
  rol administrativo técnico.
- [x] `DEC-013`: email normalizado sustituye a username; no habrá alias legado ni migración de datos
  porque no existen usuarios.
- [x] `DEC-014`: cada alta crea un despacho propio; `display_name` es obligatorio y el nombre
  efectivo del despacho usa `display_name` cuando no se proporciona `firm_name`.
- [x] Durante el MVP, el usuario registrado es el único owner de su despacho; membresías,
  invitaciones y múltiples owners quedan fuera de alcance.

La ausencia de datos legados elimina la migración de contenido de usuarios. El cambio de esquema
debe quedar representado en Alembic según la estrategia vigente del repositorio para que una base
nueva pueda crear las tablas y restricciones correctas.

## Criterios de aceptación

- [x] Un visitante puede registrarse con nombre, segundo nombre opcional, apellidos, nombre para
  mostrar editable, email válido, contraseña conforme a política y despacho opcional.
- [x] El email se normaliza de manera determinista y no admite duplicados equivalentes.
- [x] El alta crea exactamente un despacho; si se omite su nombre, se persiste el nombre completo
  del usuario como fallback, por lo que nunca queda nulo o vacío.
- [x] El usuario registrado recibe `account_owner` limitado a su despacho y no recibe ni hereda
  privilegios administrativos técnicos.
- [x] El usuario puede iniciar sesión con email y contraseña.
- [x] La sesión autenticada permite recargar y navegar por rutas protegidas durante la pestaña
  actual; una credencial inválida o expirada limpia la sesión.
- [x] El usuario puede cerrar sesión y deja de acceder a rutas protegidas.
- [x] El perfil muestra nombre completo, email y nombre de despacho, permite actualizar los campos
  autorizados y conserva el cambio de contraseña existente.
- [x] Un `account_owner` no puede leer ni mutar datos pertenecientes a otro despacho.
- [x] Ninguna respuesta expone hash de contraseña, token u otros datos sensibles.
- [x] Los errores de validación, conflicto, autenticación y red son claros y conservan diagnóstico
  por request ID.
- [x] El journey crítico funciona en viewport móvil y escritorio y cumple los controles de
  accesibilidad existentes.
- [x] Backend, frontend, OpenAPI, documentación y pruebas describen el mismo contrato.

## Plan de trabajo

### 1. Materializar contrato y esquema

- [x] Documentar las decisiones finales de rol, despacho e inexistencia de datos legados.
- [x] Definir los nombres definitivos de campos API (`first_name`, `middle_name`, `last_name`,
  `display_name`, `email`, `firm_name`) y reglas de
  normalización/validación/fallback.
- [x] Definir las entidades y relaciones de persistencia para usuario, despacho y owner.
- [x] Reflejar en Alembic las tablas, restricciones, índices únicos y claves foráneas del esquema
  final; no se necesita una transformación de datos existentes.
- [x] Revisar el impacto del subject JWT al sustituir `username` por email.

### 2. Backend: cuenta de producto

- [x] Actualizar modelos, records, repositorios y esquema Alembic de usuario/despacho.
- [x] Actualizar schemas API/aplicación y servicio de auth para registro, login, usuario actual y
  edición de perfil.
- [x] Crear usuario, despacho, ownership y asignación de `account_owner` dentro de una sola frontera
  transaccional durante el registro público.
- [x] Mantener errores normalizados para email inválido, duplicado, credenciales inválidas y
  actualización conflictiva.
- [x] Actualizar metadata OpenAPI sin cambiar el prefijo `/v1`.
- [x] Añadir/ajustar pruebas de repositorio, servicio, router, migración y autorización.

### 3. Frontend: experiencia de registro y cuenta

- [x] Actualizar contratos y cliente auth para consumir los componentes de nombre, `display_name`,
  `email` y `firm_name`.
- [x] Alinear formularios de registro, login y perfil con validación accesible y autocomplete
  adecuado.
- [x] Tras un registro exitoso, ofrecer una transición inequívoca al login sin crear una sesión
  implícita si el backend no entrega token.
- [x] Mantener logout determinista: limpiar token y caché de sesión y redirigir a una ruta pública.
- [x] Sustituir textos técnicos de username por lenguaje de cuenta de Abogado Fácil.
- [x] Mantener las rutas públicas/protegidas actuales; cualquier cambio de destino hacia el futuro
  dashboard se coordinará con `PROD-003`.

### 4. Contratos, documentación y tracking

- [x] Sincronizar el artefacto OpenAPI del frontend después del cambio backend.
- [x] Actualizar `backend/docs/operations/authentication.md`.
- [x] Actualizar `backend/docs/operations/api_endpoints.md` y, si cambia la asignación RBAC,
  `backend/docs/operations/authorization_matrix.md`.
- [x] Actualizar `frontend/docs/operations/route_inventory.md`,
  `api_consumer_matrix.md`, `mutation_policy.md` y `e2e_smoke_suite.md` cuando corresponda.
- [x] Actualizar `docs/product/BACKLOG_ABOGADO_FACIL.md` a `En progreso` al comenzar implementación y a
  `Hecho` únicamente tras cumplir todos los gates.
- [x] Mantener este archivo al día con avances, decisiones, validaciones y riesgos.

### 5. Validación

- [x] `python -m pytest backend/tests`
- [x] `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [x] `npm --prefix frontend run openapi:sync`
- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run test:e2e:ci`
- [x] `npm --prefix frontend run build`
- [x] `pre-commit run --all-files`
- [x] Ejecutar una prueba manual del journey registro -> login -> perfil -> logout con el stack
  local si Docker está disponible.

## Matriz inicial de archivos afectados

| Superficie    | Archivos o áreas esperadas                                            |
| ------------- | --------------------------------------------------------------------- |
| Persistencia  | modelos de usuario/despacho/ownership, repositorios y esquema Alembic |
| Backend auth  | schemas, service, profile updates, router/OpenAPI y pruebas auth      |
| RBAC          | bootstrap/catálogo, asignación de rol y pruebas de permisos           |
| Frontend auth | contratos, session/storage, login, registro, perfil y textos i18n     |
| Navegación    | rutas protegidas y componente que ejecuta logout                      |
| Calidad       | pruebas unitarias/integración, smoke e2e y accesibilidad              |
| Docs          | operaciones backend/frontend, backlog y este tracking                 |

La lista es orientativa; no autoriza cambios fuera del alcance y se ajustará al materializar las
decisiones ya cerradas.

## Riesgos y mitigaciones

| Riesgo                                                | Mitigación prevista                                                       |
| ----------------------------------------------------- | ------------------------------------------------------------------------- |
| Introducir compatibilidad innecesaria con username    | Contrato nuevo basado solo en email; no existen usuarios ni datos legados |
| Otorgar privilegios técnicos al propietario           | Rol de producto separado, sin herencia administrativa implícita           |
| Desalinear JWT, repositorio y contratos               | Cambiar la identidad de extremo a extremo y cubrir emisión/decodificación |
| Crear parcialmente usuario, despacho, ownership o rol | Una sola frontera transaccional para toda el alta                         |
| Deriva OpenAPI/frontend                               | Sync inmediato y pruebas de contrato en el mismo cambio                   |
| Acceso cruzado entre despachos                        | Ownership explícito, scope al despacho y pruebas negativas                |

## Registro de avance

| Fecha      | Estado                       | Nota                                                                                                                                                                                                                            |
| ---------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-07-09 | Plan listo                   | Se auditó la base existente y se documentaron alcance, brechas, decisiones, fases y gates. No se realizaron cambios de implementación.                                                                                          |
| 2026-07-09 | Decisiones cerradas          | Se fijaron email sin legado, `account_owner` no administrativo y un despacho propio por alta con nombre efectivo no nulo.                                                                                                       |
| 2026-07-10 | Implementación iniciada      | Se materializaron entidad despacho, identidad email, registro transaccional con `account_owner`, perfil de producto, formularios y OpenAPI. Los gates completos siguen abiertos por pruebas heredadas pendientes de alineación. |
| 2026-07-10 | Contrato de nombre ajustado  | `full_name` fue reemplazado por `first_name`, `middle_name`, `last_name` y `display_name`; el frontend propone el display name y permite editarlo.                                                                              |
| 2026-07-10 | Frontend unitario alineado   | Se actualizaron contratos, fixtures, formularios y consumidores RBAC al contrato de email/perfil. Pasan 43 archivos, 184 tests, lint, typecheck y el umbral de cobertura; OpenAPI y gates integrales siguen pendientes.         |
| 2026-07-10 | Backend y contrato validados | Pasan los 310 tests backend con cobertura de 100%; el artefacto OpenAPI está sincronizado y pasan lint, typecheck y `openapi:check`. Se completó la migración de fixtures e2e al perfil de producto.                            |
| 2026-07-10 | Gates automatizados cerrados | Pasan `npm run check` (43 archivos, 184 tests), build con presupuesto, los 10 smoke e2e y todos los hooks de pre-commit. Se corrigió la matriz de consumidores y el selector exacto del nombre en el smoke.                     |
| 2026-07-10 | Implementación completada    | El journey manual confirmó alta de usuario, rechazo de contraseña incorrecta, login con la contraseña correcta y logout. Con todos los gates cerrados, PROD-002 pasa a `Hecho`.                                                 |

## Resultado de validaciones

El ticket queda `Hecho`. Pasan los 310 tests backend con cobertura de 100%;
`npm --prefix frontend run check` con 43 archivos, 184 tests y 96.87% de cobertura de funciones;
`npm --prefix frontend run test:e2e:ci` con 10 smoke tests; `npm --prefix frontend run build` con
todos los presupuestos; y `.\.venv\Scripts\pre-commit.exe run --all-files`. El artefacto OpenAPI
está sincronizado y el journey manual validó registro, rechazo de credenciales incorrectas, login
correcto y logout.
