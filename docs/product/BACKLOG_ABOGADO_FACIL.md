# Backlog - Abogado Fácil

Estado inicial: 2026-07-08
Fuente principal: `docs/REQUERIMIENTOS_ABOGADO_FACIL_IA.md`
Repositorio base: template FastAPI + React + PostgreSQL + Docker

Este archivo conserva únicamente el estado resumido de cada elemento. El alcance detallado,
decisiones, avance, pausas, validaciones y cierre se registran en el plan correspondiente según
`docs/ai/backlog_tracking.md`.

## Leyenda

- Estado: `Identificado`, `Listo`, `En progreso`, `Bloqueado`, `Hecho`
- Prioridad: `P0` imprescindible para arrancar, `P1` MVP, `P2` posterior al MVP
- Tipo: `Setup`, `Producto`, `Backend`, `Frontend`, `Full-stack`, `IA`, `Docs`, `Legal`, `Ops`

## Punto de Partida

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

| ID       | Tipo       | Prioridad | Estado       | Trabajo                                       | Entregable / Criterio                                                                    |
| -------- | ---------- | --------- | ------------ | --------------------------------------------- | ---------------------------------------------------------------------------------------- |
| CORE-001 | Full-stack | P1        | Hecho        | Gestión de clientes.                          | Crear, editar, buscar y ver detalle de cliente con aislamiento por usuario.              |
| CORE-002 | Full-stack | P1        | Hecho        | Gestión de asuntos/expedientes.               | Seleccionar cliente por nombre, crear y editar asunto, ver detalle y próxima acción.     |
| CORE-003 | Full-stack | P1        | Hecho        | Notas de expediente.                          | Crear, editar, eliminar y marcar notas relevantes.                                       |
| CORE-004 | Backend    | P1        | Identificado | API y metadata de documentos de expediente.   | API aislada para subir, listar, descargar y eliminar PDF/DOCX/TXT usando object storage. |
| CORE-005 | Backend    | P1        | Identificado | Extracción de texto de PDF cuando sea viable. | Texto extraído queda disponible para futuros flujos de IA.                               |
| CORE-006 | Full-stack | P1        | Identificado | Checklists base por tipo de asunto.           | Checklist determinístico con completo/pendiente/no aplica y elementos personalizados.    |
| CORE-007 | Full-stack | P1        | Identificado | Tareas y recordatorios simples.               | Tareas por asunto con fecha límite y estado completado.                                  |
| CORE-008 | Full-stack | P1        | Identificado | Control básico de pagos.                      | Honorarios, anticipos, pagos parciales, saldo y notas.                                   |
| CORE-009 | Full-stack | P1        | Identificado | Calculadoras básicas sin IA.                  | Cálculos copiables y guardables en asunto con advertencia de estimación.                 |
| CORE-010 | Frontend   | P1        | Identificado | Interfaz de documentos de expediente.         | Cargar, listar, descargar y eliminar documentos desde el detalle del asunto.             |

## Fase 2 - BYOK y Capa de IA

| ID     | Tipo       | Prioridad | Estado       | Trabajo                                         | Entregable / Criterio                                                           |
| ------ | ---------- | --------- | ------------ | ----------------------------------------------- | ------------------------------------------------------------------------------- |
| AI-001 | Backend    | P1        | Identificado | Modelo y servicio para credenciales BYOK.       | API keys cifradas, no expuestas al frontend y eliminables por usuario.          |
| AI-002 | Full-stack | P1        | Identificado | Pantalla de configuración IA.                   | Seleccionar proveedor, guardar key, probar conexión, eliminar key y ver estado. |
| AI-003 | Backend    | P1        | Identificado | Abstracción multi-provider.                     | `OpenAIProvider`, `GeminiProvider` y `MockProvider` detrás de un puerto común.  |
| AI-004 | Backend    | P1        | Identificado | Validación obligatoria de BYOK en funciones IA. | Sin credencial válida no se ejecutan llamadas reales.                           |
| AI-005 | Ops        | P1        | Identificado | Política de logs y datos sensibles de IA.       | Prompts/API keys no aparecen en logs técnicos sin protección.                   |
| AI-006 | Backend    | P1        | Identificado | Registro de uso/errores por función IA.         | Métricas iniciales por proveedor, función, error y tiempo de respuesta.         |

## Fase 3 - IA Inicial Controlada

| ID        | Tipo       | Prioridad | Estado       | Trabajo                                   | Entregable / Criterio                                                                                        |
| --------- | ---------- | --------- | ------------ | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| AI-101    | Full-stack | P1        | Identificado | Analizador de relato inicial.             | Entrada libre, salida JSON validada y guardable en asunto.                                                   |
| AI-102    | Full-stack | P1        | Identificado | Generador de preguntas para cliente.      | Lista editable/copiable de preguntas, datos críticos y documentos faltantes.                                 |
| AI-103    | Full-stack | P1        | Identificado | Generador de mensajes para cliente.       | Mensajes para WhatsApp/email copiables y editables antes de enviar.                                          |
| LEGAL-002 | Frontend   | P1        | Identificado | Validar avisos en funciones reales de IA. | Después de 2 o 3 funciones IA, todas conservan identificación, aviso y revisión humana en sus flujos reales. |

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

| ID      | Tipo    | Prioridad | Estado       | Trabajo                                                           | Entregable / Criterio                                                              |
| ------- | ------- | --------- | ------------ | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| SEC-001 | Backend | P1        | Identificado | Aislamiento estricto por usuario/propietario.                     | Ningún usuario ve clientes, asuntos, documentos o IA de otro usuario.              |
| SEC-002 | Legal   | P1        | Identificado | Aviso de privacidad, términos y aprobación jurídica para IA BYOK. | Explica el envío al proveedor y registra revisión jurídica antes del lanzamiento.  |
| SEC-003 | Backend | P1        | Identificado | Eliminación de datos del usuario.                                 | Usuario puede eliminar documentos/asuntos según política definida.                 |
| OPS-001 | Ops     | P1        | Identificado | Límites configurables de archivos y análisis.                     | Tamaño, número de documentos y entrada IA controlados por config.                  |
| OPS-002 | Ops     | P1        | Identificado | Backups básicos de PostgreSQL.                                    | Procedimiento documentado antes de despliegue productivo.                          |
| OPS-003 | Docs    | P1        | Identificado | Mantener matrices de operaciones actualizadas.                    | Docs backend/frontend reflejan rutas, permisos, runtime, errores y e2e.            |
| OPS-004 | Ops     | P1        | Hecho        | Base S3-compatible con MinIO.                                     | Compose levanta bucket privado persistente y backend dispone de un puerto probado. |

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

## Orden Recomendado Inmediato

1. Validar Docker Compose, backend y frontend.
1. Empezar Fase 0 funcional: landing, auth alineado, dashboard vacío.
1. Abrir el primer feature slice real: clientes + asuntos, porque desbloquea notas, documentos,
   tareas, pagos e IA contextual.
