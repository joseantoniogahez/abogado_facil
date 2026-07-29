# Capacidades implementadas

Estos documentos describen capacidades entregadas y validadas. Cada plan conserva decisiones,
criterios de aceptación, límites, riesgos residuales y evidencia de validación.

Funcionan como referencia técnica para la IA y como evidencia del trabajo entregado. La referencia
funcional estable está en [`../../capabilities/`](../../capabilities/); el manual futuro debe
derivarse de esa carpeta, no de estos planes técnicos.

| Área                        | Documento                                                                 |
| --------------------------- | ------------------------------------------------------------------------- |
| Clientes                    | [`CORE-001`](CORE-001_GESTION_CLIENTES_PLAN.md)                           |
| Asuntos                     | [`CORE-002`](CORE-002_GESTION_ASUNTOS_PLAN.md)                            |
| Notas                       | [`CORE-003`](CORE-003_NOTAS_EXPEDIENTE_PLAN.md)                           |
| Documentos                  | [`CORE-004`](CORE-004_DOCUMENTOS_EXPEDIENTE_PLAN.md)                      |
| Extracción de texto PDF     | [`CORE-005`](CORE-005_EXTRACCION_TEXTO_PDF_PLAN.md)                       |
| Checklists                  | [`CORE-006`](CORE-006_CHECKLISTS_BASE_PLAN.md)                            |
| Tareas                      | [`CORE-007`](CORE-007_TAREAS_RECORDATORIOS_PLAN.md)                       |
| Pagos                       | [`CORE-008`](CORE-008_CONTROL_PAGOS_PLAN.md)                              |
| Calculadoras                | [`CORE-009`](CORE-009_CALCULADORAS_BASICAS_PLAN.md)                       |
| Interfaz de documentos      | [`CORE-010`](CORE-010_INTERFAZ_DOCUMENTOS_EXPEDIENTE_PLAN.md)             |
| Catálogo de asuntos         | [`CORE-011`](CORE-011_CATALOGO_TIPOS_ASUNTO_PLAN.md)                      |
| Avisos legales              | [`LEGAL-001`](LEGAL-001_AVISOS_LEGALES_PLAN.md)                           |
| Storage de objetos          | [`OPS-004`](OPS-004_MINIO_OBJECT_STORAGE_PLAN.md)                         |
| Autenticación               | [`PROD-002`](PROD-002_AUTH_ALIGNMENT_PLAN.md)                             |
| Dashboard                   | [`PROD-003`](PROD-003_DASHBOARD_PLAN.md)                                  |
| Jerarquía visual            | [`UX-001`](UX-001_JERARQUIA_VISUAL_ACCIONES_PLAN.md)                      |
| Tabs de detalle de asuntos  | [`UX-002`](UX-002_TABS_DETALLE_ASUNTOS_PLAN.md)                           |
| Credenciales BYOK           | [`AI-001`](AI-001_CREDENCIALES_BYOK_PLAN.md)                              |
| Configuración de IA         | [`AI-002`](AI-002_PANTALLA_CONFIGURACION_IA_PLAN.md)                      |
| Proveedores de IA           | [`AI-003`](AI-003_MULTI_PROVIDER_PLAN.md)                                 |
| Validación BYOK para IA     | [`AI-004`](AI-004_VALIDACION_BYOK_PLAN.md)                                |
| Logs y datos sensibles IA   | [`AI-005`](AI-005_POLITICA_LOGS_DATOS_SENSIBLES_PLAN.md)                  |
| Metricas de IA              | [`AI-006`](AI-006_METRICAS_USO_ERRORES_LATENCIA_PLAN.md)                  |
| Salidas estructuradas IA    | [`AI-007`](AI-007_VALIDACION_SALIDAS_ESTRUCTURADAS_PLAN.md)               |
| Minimizacion de contexto IA | [`AI-008`](AI-008_MINIMIZACION_CONTEXTO_IA_PLAN.md)                       |
| Ciclo de vida de IA         | [`AI-009`](AI-009_CICLO_VIDA_EJECUCIONES_IA_PLAN.md)                      |
| Resiliencia RQ/Redis        | [`AI-010`](AI-010_RESILIENCIA_RQ_REDIS_PLAN.md)                           |
| Taxonomía de errores IA     | [`AI-011`](AI-011_TAXONOMIA_ERRORES_IA_PLAN.md)                           |
| Observabilidad de IA        | [`OBS-001`](OBS-001_OBSERVABILIDAD_CORRELACIONADA_IA_PLAN.md)             |
| Contratos multi-provider    | [`TEST-AI-001`](TEST-AI-001_CONTRATOS_FALLOS_MULTI_PROVIDER_PLAN.md)      |
| Threat model de IA          | [`DOCS-AI-002`](DOCS-AI-002_FLUJO_DATOS_THREAT_MODEL_PLAN.md)             |
| Auditoría backend inicial   | [`AUDIT-001`](AUDIT-001_AUDITORIA_BACKEND_FASTAPI_INICIAL_PLAN.md)        |
| Auditoría backend final     | [`AUDIT-002`](AUDIT-002_AUDITORIA_BACKEND_FASTAPI_POST_HARDENING_PLAN.md) |
| OpenAPI en producción       | [`OPS-005`](OPS-005_OPENAPI_PRODUCCION_PLAN.md)                           |
| CORS endurecido             | [`OPS-006`](OPS-006_CORS_ENDURECIDO_PLAN.md)                              |
| Readiness checks            | [`OPS-007`](OPS-007_READINESS_CHECKS_PLAN.md)                             |
| Rate limiting               | [`OPS-008`](OPS-008_RATE_LIMITING_PLAN.md)                                |
| Streaming y observabilidad  | [`OPS-009`](OPS-009_STREAMING_OBSERVABILIDAD_IA_PLAN.md)                  |
| Aislamiento por despacho    | [`SEC-001A`](SEC-001A_AISLAMIENTO_GENERAL_POR_DESPACHO_PLAN.md)           |
| Prompt injection documental | [`SEC-004`](SEC-004_PROTECCION_PROMPT_INJECTION_DOCUMENTAL_PLAN.md)       |
| Analizador IA               | [`AI-101`](AI-101_ANALIZADOR_RELATO_PLAN.md)                              |
| Preguntas IA                | [`AI-102`](AI-102_PREGUNTAS_CLIENTE_PLAN.md)                              |
| Mensajes IA                 | [`AI-103`](AI-103_MENSAJES_CLIENTE_PLAN.md)                               |
| Revisión y aceptación IA    | [`AI-104`](AI-104_REVISION_ACEPTACION_PLAN.md)                            |
| Acciones desde IA           | [`AI-105`](AI-105_CONVERSION_ACCIONES_PLAN.md)                            |
| Procedencia IA              | [`AI-106`](AI-106_PROCEDENCIA_ACTUALIZACION_PLAN.md)                      |
| Revisión humana de IA       | [`LEGAL-002A`](LEGAL-002A_PATRON_REVISION_HUMANA_PLAN.md)                 |
| Auditoría de avisos IA      | [`LEGAL-002B`](LEGAL-002B_VALIDACION_AVISOS_IA_PLAN.md)                   |
| Preview de contexto IA      | [`UX-AI-001`](UX-AI-001_PREVIEW_CONTEXTO_PLAN.md)                         |
| Aislamiento de contexto IA  | [`SEC-001B`](SEC-001B_AISLAMIENTO_CONTEXTO_IA_PLAN.md)                    |
| Fase 3 IA controlada        | [`PHASE-3`](PHASE-3_IA_INICIAL_CONTROLADA_PLAN.md)                        |
