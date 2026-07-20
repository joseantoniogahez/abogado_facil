# Backlog - Abogado Fácil

Estado inicial: 2026-07-08
Fuente principal: `docs/product/REQUERIMIENTOS_ABOGADO_FACIL_IA.md`
Repositorio base: template FastAPI + React + PostgreSQL + Docker

Este archivo conserva únicamente el estado resumido de cada elemento. El alcance detallado,
decisiones, avance, pausas, validaciones y cierre se registran en el plan correspondiente según
`docs/ai/backlog_tracking.md`.

## Leyenda

- Estado: `Identificado`, `Listo`, `En progreso`, `Bloqueado`, `Hecho`
- Prioridad: `P0` imprescindible para arrancar, `P1` MVP, `P2` posterior al MVP, `P0-IA` release gate que bloquea el lanzamiento de cualquier función que llame a un proveedor de IA
- Tipo: `Setup`, `Producto`, `Backend`, `Frontend`, `Full-stack`, `IA`, `Docs`, `Legal`, `Ops`
- Competencia de portafolio: `BE-AI`, `AI-PRODUCT`, `AMBAS`, `FOUNDATION`

### Release gates de IA

Una función que envíe información a OpenAI, Gemini u otro proveedor no puede pasar a `Hecho` ni
liberarse mientras permanezca pendiente cualquiera de estos gates: aislamiento general por
despacho, aislamiento del contexto enviado, pruebas negativas multiusuario, cifrado de credenciales,
logs sin datos sensibles, consentimiento y privacidad, minimización del contexto y validación de
salidas estructuradas. Estos gates son `P0-IA` para la Fase 2 y las fases posteriores de IA; no
bloquean el uso del núcleo del producto sin IA.

## Punto de Partida Histórico

Este bloque conserva el contexto del bootstrap inicial y no representa el estado operativo actual.
La identidad de Abogado Fácil ya fue aplicada y las features marcadas como `Hecho` abajo ya fueron
implementadas y validadas en sus planes individuales.

Las viñetas siguientes describen exclusivamente el estado inicial del 2026-07-08.

- El repositorio todavía conserva identidad de template en `README.md`, Compose, JWT, env y package
  metadata.
- El documento de requerimientos ya define el producto `Abogado Fácil`, el MVP, el modelo BYOK y el
  roadmap funcional.
- El bootstrap inicial debe ser identity-only: nombres, slugs, Compose, JWT, base de datos,
  package metadata, README y textos visibles mínimos.
- Las funcionalidades legales y de IA deben tratarse como features posteriores al bootstrap, no como
  parte del rename inicial.
- El comando de preview del bootstrap ya corre usando `.\.venv\Scripts\python.exe`.

## Decisiones de Producto

| ID      | Decisión                     | Propuesta inicial                                                                                                      | Estado    |
| ------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------- | --------- |
| DEC-001 | Nombre público               | Abogado Fácil                                                                                                          | Listo     |
| DEC-002 | Slug interno                 | `abogado-facil`                                                                                                        | Listo     |
| DEC-003 | Env prefix                   | `abogado_facil`                                                                                                        | Listo     |
| DEC-004 | Frontend package             | `abogado-facil-frontend`                                                                                               | Listo     |
| DEC-005 | Compose dev/test/prod        | `abogado-facil-dev`, `abogado-facil-tests`, `abogado-facil-prod`                                                       | Listo     |
| DEC-006 | DB name                      | `abogado_facil_main`                                                                                                   | Listo     |
| DEC-007 | JWT issuer/audience          | `abogado-facil`, `abogado-facil-api`                                                                                   | Listo     |
| DEC-008 | Descripción corta            | SaaS web para abogados independientes y despachos pequeños con expedientes, tareas, documentos e IA BYOK.              | Listo     |
| DEC-009 | Roles MVP                    | `account_owner` público, limitado a su despacho y sin herencia del rol administrativo técnico.                         | Listo     |
| DEC-010 | Storage de documentos        | MinIO en Compose mediante API S3; archivos fuera de PostgreSQL y metadata en la base.                                  | Listo     |
| DEC-011 | Proveedor despliegue inicial | Local/Docker primero; elegir target productivo después.                                                                | Pendiente |
| DEC-012 | Tracker principal            | Estado resumido aquí y detalle en un plan Markdown por ticket; migrar a GitHub Issues cuando el alcance se estabilice. | Listo     |
| DEC-013 | Identidad de acceso MVP      | Email normalizado; no se requiere compatibilidad ni migración de datos de usernames existentes.                        | Listo     |
| DEC-014 | Despacho inicial             | Un despacho por alta; nombre no nulo con fallback a `display_name`; el alta es su único owner.                         | Listo     |

## Fase 0 - Bootstrap y Base Pública

| ID        | Tipo       | Prioridad | Estado | Trabajo                                                   | Entregable / Criterio                                                                                       |
| --------- | ---------- | --------- | ------ | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| SETUP-001 | Setup      | P0        | Hecho  | Ejecutar preview del bootstrap inicial.                   | `scripts/bootstrap_new_app.py` muestra archivos a tocar sin `--write`. Preview ejecutado con la venv local. |
| SETUP-002 | Setup      | P0        | Hecho  | Aplicar bootstrap identity-only.                          | README/env/Compose/JWT/package/título/textos visibles usan identidad Abogado Fácil.                         |
| SETUP-003 | Ops        | P0        | Hecho  | Crear `.env` desde `.env_examples` después del bootstrap. | Stack local puede resolver variables nuevas.                                                                |
| SETUP-004 | Ops        | P0        | Hecho  | Validar Compose dev/test/prod.                            | `docker compose config` y variantes test/prod pasan.                                                        |
| SETUP-005 | Backend    | P0        | Hecho  | Validar backend base después del bootstrap.               | Tests backend y coverage gate pasan sin cambios funcionales.                                                |
| SETUP-006 | Frontend   | P0        | Hecho  | Validar frontend base después del bootstrap.              | `npm --prefix frontend run check` y build pasan.                                                            |
| SETUP-007 | Docs       | P0        | Hecho  | Actualizar documentación raíz con identidad de producto.  | README describe Abogado Fácil sin perder instrucciones operativas.                                          |
| PROD-001  | Frontend   | P1        | Hecho  | Rediseñar landing pública para Abogado Fácil.             | Visitante entiende valor, BYOK y aviso legal en menos de un minuto.                                         |
| PROD-002  | Full-stack | P1        | Hecho  | Alinear auth existente con registro/login del producto.   | Registro, rechazo de credenciales incorrectas, login y logout validados; pasan todos los gates.             |
| PROD-003  | Full-stack | P1        | Hecho  | Crear dashboard autenticado inicial.                      | Muestra contadores base, tareas próximas y estado de IA.                                                    |
| LEGAL-001 | Legal      | P1        | Hecho  | Definir textos mínimos de aviso legal y revisión humana.  | Mensajes visibles en landing y patrón compartido para funciones de IA.                                      |

## Fase 1 - Núcleo Legal Sin IA

| ID       | Tipo       | Prioridad | Estado | Trabajo                                        | Entregable / Criterio                                                                              |
| -------- | ---------- | --------- | ------ | ---------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| CORE-001 | Full-stack | P1        | Hecho  | Gestión de clientes.                           | Crear, editar, buscar y ver detalle de cliente con aislamiento por usuario.                        |
| CORE-002 | Full-stack | P1        | Hecho  | Gestión de asuntos/expedientes.                | Seleccionar cliente por nombre, crear y editar asunto, ver detalle y próxima acción.               |
| CORE-003 | Full-stack | P1        | Hecho  | Notas de expediente.                           | Crear, editar, eliminar y marcar notas relevantes.                                                 |
| CORE-004 | Backend    | P1        | Hecho  | API y metadata de documentos de expediente.    | API aislada para subir, listar, descargar y eliminar PDF/DOCX/TXT usando object storage.           |
| CORE-005 | Backend    | P1        | Hecho  | Extracción de texto de PDF cuando sea viable.  | Texto extraído queda disponible para futuros flujos de IA.                                         |
| CORE-006 | Full-stack | P1        | Hecho  | Checklists base por tipo de asunto.            | Checklist determinístico con completo/pendiente/no aplica y elementos personalizados.              |
| CORE-007 | Full-stack | P1        | Hecho  | Tareas y recordatorios simples.                | Tareas por asunto con fecha límite y estado completado.                                            |
| CORE-008 | Full-stack | P1        | Hecho  | Control básico de pagos.                       | Honorarios, anticipos, pagos parciales, saldo y notas.                                             |
| CORE-009 | Full-stack | P1        | Hecho  | Calculadoras básicas sin IA.                   | Cálculos copiables y guardables en asunto con advertencia de estimación.                           |
| CORE-010 | Frontend   | P1        | Hecho  | Interfaz de documentos de expediente.          | Cargar, listar, descargar y eliminar documentos desde el detalle del asunto.                       |
| CORE-011 | Full-stack | P1        | Hecho  | Catálogo de tipos de asunto y checklists base. | `matter_type` se elige de un catálogo backend cerrado, incluido `Otro`, y se persiste como string. |
| UX-001   | Frontend   | P1        | Hecho  | Jerarquía visual de botones y acciones.        | Acciones y estados deshabilitados se distinguen del texto sin depender de `hover`.                 |

| UX-002 | Frontend | P1 | Hecho | Reorganizar el detalle de asuntos por tabs. | El detalle conserva un resumen visible y agrupa seguimiento, finanzas, documentos y notas sin scroll excesivo. |

### Cierre FastAPI de Fase 1

Los siguientes tickets deben ejecutarse en orden. `AUDIT-001` establece la línea base, los cinco
tickets de hardening implementan las mejoras priorizadas y `AUDIT-002` verifica el resultado antes
de iniciar la siguiente fase funcional.

| ID        | Tipo    | Prioridad | Estado       | Trabajo                                                             | Entregable / Criterio                                                                                                                                                                                                            |
| --------- | ------- | --------- | ------------ | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AUDIT-001 | Backend | P1        | Listo        | Auditoría formal inicial del backend con el agente de programación. | Informe con hallazgos ordenados por severidad sobre FastAPI, API/OpenAPI, auth/RBAC, aislamiento, errores, configuración, observabilidad, pruebas y documentación; cada hallazgo tiene evidencia, archivo/línea y recomendación. |
| OPS-005   | Backend | P1        | Identificado | Proteger la documentación OpenAPI en producción.                    | `/docs`, `/redoc` y `/openapi.json` se deshabilitan o protegen explícitamente según `APP_ENV`, con pruebas de configuración y decisión documentada.                                                                              |
| OPS-006   | Backend | P1        | Identificado | Endurecer CORS.                                                     | Orígenes, métodos y headers permitidos son explícitos por entorno; credenciales solo se habilitan con una configuración segura y quedan cubiertos por pruebas.                                                                   |
| OPS-007   | Backend | P1        | Identificado | Separar health y readiness checks.                                  | Liveness confirma proceso; readiness verifica dependencias críticas como base de datos y object storage sin filtrar secretos.                                                                                                    |
| OPS-008   | Backend | P1        | Identificado | Añadir rate limiting para superficies sensibles.                    | Login, registro, uploads y futuras llamadas IA tienen límites configurables, respuesta normalizada y pruebas de exceso, sin romper tests locales.                                                                                |
| OPS-009   | Backend | P1        | Identificado | Preparar streaming/SSE y observabilidad para funciones IA.          | Existe un patrón probado de streaming cancelable y eventos correlacionados con `request_id`, sin datos sensibles, listo para consumidores IA y con métricas de latencia/errores.                                                 |
| AUDIT-002 | Backend | P1        | Identificado | Auditoría formal posterior con el agente de programación.           | Revisión de cierre confirma cada criterio, detecta regresiones y actualiza el informe; no quedan hallazgos P0/P1 abiertos sin decisión explícita antes de Fase 2.                                                                |

Cada ticket de IA debe registrar en su plan la competencia principal y la evidencia verificable
esperada: pruebas de contrato, métricas, ADR, threat model, caso de fallo o demo del flujo.

## Fase 2 - BYOK y Capa de IA

| ID     | Tipo       | Prioridad | Estado       | Trabajo                                         | Entregable / Criterio                                                             |
| ------ | ---------- | --------- | ------------ | ----------------------------------------------- | --------------------------------------------------------------------------------- |
| AI-001 | Backend    | P0-IA     | Identificado | Modelo y servicio para credenciales BYOK.       | API keys cifradas, no expuestas al frontend y eliminables por usuario.            |
| AI-002 | Full-stack | P1        | Identificado | Pantalla de configuración IA.                   | Seleccionar proveedor, guardar key, probar conexión, eliminar key y ver estado.   |
| AI-003 | Backend    | P1        | Identificado | Abstracción multi-provider.                     | `OpenAIProvider`, `GeminiProvider` y `MockProvider` detrás de un puerto común.    |
| AI-004 | Backend    | P0-IA     | Identificado | Validación obligatoria de BYOK en funciones IA. | Sin credencial válida no se ejecutan llamadas reales.                             |
| AI-005 | Ops        | P0-IA     | Identificado | Política de logs y datos sensibles de IA.       | Prompts/API keys no aparecen en logs técnicos sin protección.                     |
| AI-006 | Backend    | P1        | Identificado | Registro de uso/errores por función IA.         | Métricas iniciales por proveedor, función, error y tiempo de respuesta.           |
| AI-007 | Backend    | P0-IA     | Identificado | Validación de salidas estructuradas.            | JSON/schema validado antes de guardar, mostrar, copiar o exportar resultados IA.  |
| AI-008 | Backend    | P0-IA     | Identificado | Minimización del contexto enviado a IA.         | Cada llamada envía únicamente el contexto autorizado y necesario para la función. |

| AI-009 | Backend | P0-IA | Identificado | Ciclo de vida de ejecuciones de IA. | `AIJob` con estados, intentos, versiones, resultado, error y correlación. |
| AI-010 | Backend | P1 | Identificado | Resiliencia de proveedores. | Timeouts, reintentos recuperables, backoff, rate limits y prevención de duplicados. |
| AI-011 | Backend | P1 | Identificado | Taxonomía normalizada de errores. | OpenAI, Gemini y mock mapean errores al contrato común y seguro para frontend. |
| OBS-001 | Ops | P1 | Identificado | Observabilidad correlacionada. | `request_id` permite seguir API → `AIJob` → proveedor → resultado sin datos sensibles. |
| TEST-AI-001 | Backend | P1 | Identificado | Pruebas de contrato y fallos multi-provider. | Contratos OpenAI/Gemini/mock y escenarios de timeout, rate limit, JSON inválido y reintentos. |

## Fase 3 - IA Inicial Controlada

| ID         | Tipo       | Prioridad | Estado       | Trabajo                                  | Entregable / Criterio                                                        |
| ---------- | ---------- | --------- | ------------ | ---------------------------------------- | ---------------------------------------------------------------------------- |
| AI-101     | Full-stack | P1        | Identificado | Analizador de relato inicial.            | Entrada libre, salida JSON validada y guardable en asunto.                   |
| AI-102     | Full-stack | P1        | Identificado | Generador de preguntas para cliente.     | Lista editable/copiable de preguntas, datos críticos y documentos faltantes. |
| AI-103     | Full-stack | P1        | Identificado | Generador de mensajes para cliente.      | Mensajes para WhatsApp/email copiables y editables antes de enviar.          |
| LEGAL-002A | Frontend   | P0-IA     | Listo        | Patrón obligatorio de revisión humana.   | Aviso, etiqueta, edición y aceptación explícita sin envío automático.        |
| LEGAL-002B | Frontend   | P1        | Identificado | Auditoría de consistencia del patrón IA. | Varias funciones reales cumplen `LEGAL-002A` y sus pruebas consumidoras.     |

| UX-AI-001 | Full-stack | P1 | Identificado | Vista previa del contexto. | Usuario revisa, incluye o excluye fuentes, proveedor y posible costo antes de ejecutar. |
| AI-104 | Full-stack | P1 | Identificado | Revisión y aceptación de resultados. | Editar, aceptar parcial o totalmente, rechazar, regenerar y reportar problemas. |
| AI-105 | Full-stack | P1 | Identificado | Convertir resultados en acciones. | Salida se convierte en nota, tarea, pregunta, checklist, documento faltante o mensaje. |
| AI-106 | Full-stack | P1 | Identificado | Procedencia y estado de actualización. | Fuentes/versiones y aviso cuando un resultado guardado queda desactualizado. |

## Fase 4 - Expediente Asistido

| ID     | Tipo       | Prioridad | Estado       | Trabajo                         | Entregable / Criterio                                                       |
| ------ | ---------- | --------- | ------------ | ------------------------------- | --------------------------------------------------------------------------- |
| AI-201 | Full-stack | P1        | Identificado | Resumen del expediente.         | Resumen guardado, reutilizable y no recomputado solo por consulta.          |
| AI-202 | Full-stack | P1        | Identificado | Cronología de hechos.           | Eventos ordenados por fecha, editables y con fuente cuando esté disponible. |
| AI-203 | Full-stack | P1        | Identificado | Checklist personalizado con IA. | Parte de checklist base y marca sugerencias generadas por IA.               |

## Fase 5 - Documentos Simples

| ID      | Tipo       | Prioridad | Estado       | Trabajo                                | Entregable / Criterio                                                                        |
| ------- | ---------- | --------- | ------------ | -------------------------------------- | -------------------------------------------------------------------------------------------- |
| DOC-001 | Full-stack | P1        | Identificado | Catálogo de plantillas simples.        | Tipos iniciales: requerimiento de pago, convenio, solicitud de documentos y resumen interno. |
| DOC-002 | Full-stack | P1        | Identificado | Generador de borrador desde plantilla. | Formulario, validación, secciones IA controladas y borrador editable.                        |
| DOC-003 | Frontend   | P1        | Identificado | Copiar/exportar borrador.              | Usuario puede copiar contenido o exportarlo según alcance técnico elegido.                   |

## Seguridad, Privacidad y Operación

| ID       | Tipo    | Prioridad | Estado       | Trabajo                                                           | Entregable / Criterio                                                                                      |
| -------- | ------- | --------- | ------------ | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| SEC-001A | Backend | P1        | En progreso  | Aislamiento general por despacho.                                 | Matriz de pruebas confirma aislamiento de clientes, asuntos, documentos y resultados por `firm_id`.        |
| SEC-001B | Backend | P0-IA     | Identificado | Aislamiento del contexto enviado a IA.                            | El contexto de cada llamada se construye solo desde recursos autorizados del despacho actual.              |
| SEC-001C | Backend | P0-IA     | Identificado | Pruebas negativas multiusuario.                                   | Accesos cruzados a clientes, asuntos, documentos y resultados devuelven rechazo o `404` opaco.             |
| SEC-002  | Legal   | P0-IA     | Identificado | Aviso de privacidad, términos y aprobación jurídica para IA BYOK. | Explica el envío al proveedor, solicita consentimiento y registra revisión jurídica antes del lanzamiento. |
| SEC-003  | Backend | P1        | Identificado | Eliminación de datos del usuario.                                 | Usuario puede eliminar documentos/asuntos según política definida.                                         |
| OPS-001  | Ops     | P1        | Identificado | Límites configurables de archivos y análisis.                     | Tamaño, número de documentos y entrada IA controlados por config.                                          |
| OPS-002  | Ops     | P1        | Identificado | Backups básicos de PostgreSQL.                                    | Procedimiento documentado antes de despliegue productivo.                                                  |
| OPS-003  | Docs    | P1        | Identificado | Mantener matrices de operaciones actualizadas.                    | Docs backend/frontend reflejan rutas, permisos, runtime, errores y e2e.                                    |
| OPS-004  | Ops     | P1        | Hecho        | Base S3-compatible con MinIO.                                     | Compose levanta bucket privado persistente y backend dispone de un puerto probado.                         |

| PROD-AI-001 | Full-stack | P1 | Identificado | Hero flow de incorporación de cliente. | Relato inicial convertido en expediente accionable con revisión y guardado. |
| OBS-002 | Ops | P1 | Identificado | Métricas operativas de IA. | Dashboard reproducible con éxito, errores, latencia, tokens, costo, reintentos y jobs atascados. |
| PROD-AI-002 | Full-stack | P1 | Identificado | Retroalimentación de utilidad. | Usuario clasifica utilidad, corrección, invención o información faltante. |
| PROD-AI-003 | Full-stack | P1 | Identificado | Métricas de producto de IA. | Medición de valor, aceptación, edición, conversión, regeneración y abandono. |
| UX-AI-002 | Frontend | P1 | Identificado | Onboarding BYOK guiado. | Guía por proveedor, validación accionable y modo demostrativo explícito con mock. |

### Gate adicional de seguridad de IA

| ID      | Tipo    | Prioridad | Estado       | Trabajo                                        | Entregable / Criterio                                                                                               |
| ------- | ------- | --------- | ------------ | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| SEC-004 | Backend | P0-IA     | Identificado | Protección contra prompt injection documental. | Documentos son datos no confiables, delimitados y sin capacidad de modificar instrucciones o ejecutar herramientas. |

## Evidencia pública de portafolio

| ID          | Tipo | Prioridad | Estado       | Trabajo                              | Entregable / Criterio                                                                 |
| ----------- | ---- | --------- | ------------ | ------------------------------------ | ------------------------------------------------------------------------------------- |
| DOCS-AI-001 | Docs | P1        | Identificado | Arquitectura de integración IA.      | Diagrama de puertos, adaptadores, jobs, resultados y límites de confianza.            |
| DOCS-AI-002 | Docs | P1        | Identificado | Flujo de datos y threat model.       | Contexto, aislamiento, prompt injection, credenciales y datos sensibles documentados. |
| DOCS-AI-003 | Docs | P1        | Identificado | ADR de BYOK y multi-provider.        | Decisiones, alternativas y trade-offs registrados.                                    |
| DOCS-AI-004 | Docs | P1        | Identificado | Catálogo de errores y reintentos.    | Taxonomía, política de retry y ejemplos de fallos reproducibles.                      |
| DOCS-AI-005 | Docs | P1        | Identificado | Evaluación de prompts y schemas.     | Casos de evaluación, resultados y cambios documentados.                               |
| DOCS-AI-006 | Docs | P1        | Identificado | Caso de estudio del hero flow.       | Problema, flujo, decisiones, riesgos, métricas y resultado observado.                 |
| DEMO-AI-001 | Docs | P1        | Identificado | Guion de demo técnica y de producto. | Recorrido reproducible del hero flow y sus escenarios de fallo.                       |

## Fuera del MVP

- Chat legal abierto.
- IA incluida pagada por la plataforma.
- App móvil nativa.
- WhatsApp Business API.
- Integración con juzgados.
- Investigación jurisprudencial automática.
- OCR avanzado de imágenes.
- Expedientes compartidos con clientes externos.
- Firma electrónica.
- Pagos en línea.
- Facturación electrónica.
- Multi-despacho avanzado.

## Siguiente Trabajo del Backlog

La secuencia de portafolio prioriza primero la plataforma confiable y después el hero flow:

1. Plataforma: `AI-009`, `AI-010`, `AI-011`, `OBS-001` y `TEST-AI-001`.
1. Seguridad adicional: `SEC-004` y `LEGAL-002A`.
1. Hero flow: `UX-AI-001`, `AI-101`, `AI-104`, `AI-105` y `PROD-AI-001`.
1. Medición: `AI-006`, `OBS-002`, `PROD-AI-002` y `PROD-AI-003`.

El siguiente trabajo priorizado es continuar con la Fase 2:

1. Cerrar los release gates de IA y la configuración segura de BYOK (`AI-001`, `AI-004`, `AI-005`, `AI-007`, `AI-008`, `SEC-001A`, `SEC-001B`, `SEC-001C`, `SEC-002`).

1. Implementar la pantalla de configuración y la abstracción multi-provider (`AI-002`, `AI-003`).

1. Mantener pendientes las políticas operativas y de privacidad de IA (`AI-005`, `AI-006`, `SEC-002`).
