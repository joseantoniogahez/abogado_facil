# Requerimientos del Producto — Abogado Fácil

**Nombre de la app:** Abogado Fácil
**Tipo de producto:** SaaS web para abogados independientes y despachos pequeños
**Versión del documento:** 0.1
**Estado:** Borrador inicial para MVP
**Fecha:** 2026-07-08
**Autor:** José Antonio García Hernández / ITAÑUU

______________________________________________________________________

## 1. Resumen ejecutivo

**Abogado Fácil** será una aplicación web económica, práctica y ligera para abogados independientes o despachos pequeños que atienden principalmente a personas físicas en asuntos cotidianos: familiar, laboral, civil básico, deudas, arrendamiento y sucesorio básico.

El objetivo del producto es ayudar al abogado a organizar clientes, expedientes, documentos, tareas, checklists, pagos y borradores de comunicación o documentos simples, usando inteligencia artificial únicamente dentro de flujos controlados.

Desde el MVP, la aplicación deberá funcionar bajo un modelo **BYOK — Bring Your Own Key**, es decir, cada usuario conectará su propia API key de un proveedor de IA compatible, como OpenAI o Google Gemini. La app no asumirá inicialmente el costo del consumo de IA del usuario.

______________________________________________________________________

## 2. Objetivo del MVP

Construir una primera versión funcional que permita demostrar tres cosas:

1. **Valor real para abogados pequeños:** organizar casos, reducir trabajo repetitivo y preparar información/documentos más rápido.
1. **Integración profesional de IA en flujos de trabajo:** no un chatbot genérico, sino funciones puntuales dentro de procesos legales cotidianos.
1. **Sostenibilidad operativa:** mantener bajos costos de servidor y evitar absorber costos variables de IA mediante BYOK obligatorio.

______________________________________________________________________

## 3. Público objetivo

### 3.1 Usuario principal

Abogado independiente o despacho pequeño que:

- Atiende personas físicas.
- Trabaja con expedientes pequeños o medianos.
- Usa WhatsApp, Word, PDF, Google Drive o carpetas locales.
- No quiere pagar software legal empresarial.
- Necesita orden, plantillas, seguimiento y apoyo en redacción.
- Tiene sensibilidad al precio.

### 3.2 Áreas legales iniciales

El MVP se enfocará en:

- Familiar básico.
- Laboral básico.
- Civil básico.
- Deudas y convenios de pago.
- Arrendamiento.
- Sucesorio básico.

### 3.3 Áreas fuera del MVP

Quedan fuera de la primera versión:

- Penal.
- Fiscal.
- Amparo avanzado.
- Investigación jurisprudencial avanzada.
- Integración con juzgados.
- Firma electrónica avanzada.
- Marketplace cliente-abogado.
- Asesoría legal directa al público general.

______________________________________________________________________

## 4. Propuesta de valor

**Abogado Fácil ayuda al abogado pequeño a convertir notas, documentos y relatos de clientes en expedientes organizados, checklists, cronologías, mensajes y borradores simples, sin pagar software caro ni depender de IA incluida en la plataforma.**

______________________________________________________________________

## 5. Principios de producto

1. **Web primero:** la aplicación será web responsive. No habrá app móvil nativa en el MVP.
1. **Simple antes que completo:** se priorizarán flujos fáciles de entender.
1. **IA controlada:** la IA no deberá actuar como asesor legal autónomo.
1. **BYOK obligatorio:** cada usuario deberá conectar su propia API key para usar funciones de IA.
1. **Bajo costo operativo:** el sistema debe poder mantenerse disponible con infraestructura económica.
1. **Privacidad desde el diseño:** los expedientes y documentos deben tratarse como información sensible.
1. **Revisión humana obligatoria:** cualquier contenido generado por IA será borrador o apoyo, nunca resultado final automático.
1. **Portafolio técnico:** el producto debe demostrar integración real de IA, SaaS multiusuario, seguridad, límites y flujos de negocio.

______________________________________________________________________

## 6. Alcance funcional del MVP

## 6.1 Landing page pública

### Descripción

Página pública para explicar el producto, mostrar beneficios y permitir registro o solicitud de acceso.

### Requerimientos

- Mostrar nombre de la app: **Abogado Fácil**.
- Explicar el valor principal.
- Mostrar módulos incluidos.
- Explicar que el uso de IA requiere conectar una API key propia.
- Incluir aviso de que la app no sustituye criterio jurídico profesional.
- Incluir botón de registro/inicio de sesión.

### Criterios de aceptación

- El visitante puede entender qué hace la app en menos de un minuto.
- La página se visualiza correctamente en celular y escritorio.
- La landing no requiere backend para cargarse.

______________________________________________________________________

## 6.2 Autenticación y cuenta de usuario

### Descripción

Sistema básico de registro, inicio de sesión y administración de cuenta.

### Requerimientos

- Registro con email y contraseña.
- Inicio de sesión.
- Cierre de sesión.
- Recuperación de contraseña, si el proveedor de autenticación lo permite.
- Perfil básico del usuario.
- Nombre del despacho opcional.
- Rol inicial: propietario de cuenta.

### Criterios de aceptación

- Un usuario puede crear cuenta e iniciar sesión.
- Los datos de un usuario no son visibles para otro.
- La sesión se mantiene de forma segura.

______________________________________________________________________

## 6.3 Configuración BYOK de IA

### Descripción

Módulo obligatorio para que el usuario conecte su propia API key de IA. Sin API key válida, las funciones de IA deberán permanecer bloqueadas o en modo demo sin llamadas reales.

### Proveedores iniciales

- OpenAI.
- Google Gemini.

### Requerimientos funcionales

- Permitir seleccionar proveedor de IA.
- Permitir guardar API key del proveedor seleccionado.
- Permitir probar conexión.
- Permitir eliminar API key.
- Permitir cambiar proveedor activo.
- Mostrar estado: configurado / no configurado / error de conexión.
- No mostrar la API key completa después de guardarla.
- Mostrar advertencia clara de que el proveedor de IA puede cobrar al usuario por uso.
- Todas las funciones de IA deberán validar que el usuario tenga proveedor configurado.

### Requerimientos de seguridad

- Las API keys deben cifrarse antes de guardarse.
- Las API keys no deben registrarse en logs.
- Las API keys no deben enviarse al frontend después de guardarse.
- Solo el backend deberá ejecutar llamadas a proveedores de IA.
- Debe existir opción para eliminar credenciales.

### Criterios de aceptación

- Un usuario puede guardar una API key válida.
- El sistema puede probar la conexión con el proveedor.
- Si la API key no existe o es inválida, la función de IA no se ejecuta.
- El usuario puede eliminar su API key.
- La API key nunca aparece completa en pantalla después de guardarse.

______________________________________________________________________

## 6.4 Dashboard principal

### Descripción

Pantalla inicial del usuario autenticado con resumen de actividad.

### Requerimientos

- Mostrar número de clientes.
- Mostrar número de asuntos activos.
- Mostrar tareas pendientes.
- Mostrar próximos vencimientos o recordatorios.
- Mostrar estado de configuración de IA.
- Acceso rápido a crear cliente, crear asunto y analizar relato inicial.

### Criterios de aceptación

- El usuario puede identificar rápidamente qué asuntos requieren atención.
- El usuario puede saber si ya configuró su proveedor de IA.

______________________________________________________________________

## 6.5 Gestión de clientes

### Descripción

Módulo para registrar y consultar clientes.

### Campos mínimos

- Nombre completo.
- Teléfono.
- Email opcional.
- Dirección opcional.
- Notas.
- Fecha de creación.

### Requerimientos

- Crear cliente.
- Editar cliente.
- Ver detalle del cliente.
- Buscar clientes por nombre o teléfono.
- Ver asuntos asociados al cliente.

### Criterios de aceptación

- El usuario puede registrar un cliente en menos de un minuto.
- El usuario puede encontrar un cliente existente.
- La información del cliente queda asociada a sus asuntos.

______________________________________________________________________

## 6.6 Gestión de asuntos / expedientes

### Descripción

Módulo central del producto. Un asunto representa un expediente o caso legal.

### Campos mínimos

- Cliente asociado.
- Título del asunto.
- Tipo de asunto.
- Área legal.
- Estado.
- Contraparte opcional.
- Descripción breve.
- Fecha de apertura.
- Próxima acción.

### Estados sugeridos

- Prospecto.
- Activo.
- En espera de documentos.
- En revisión.
- Cerrado.
- Archivado.

### Áreas iniciales

- Familiar.
- Laboral.
- Civil.
- Deudas.
- Arrendamiento.
- Sucesorio básico.
- Otro.

### Requerimientos

- Crear asunto desde cliente.
- Crear asunto nuevo y asociar cliente.
- Editar asunto.
- Cambiar estado.
- Agregar notas.
- Ver documentos asociados.
- Ver tareas asociadas.
- Ver resumen IA, si existe.
- Ver cronología IA, si existe.

### Criterios de aceptación

- El usuario puede crear un expediente básico.
- El expediente concentra notas, documentos, tareas y resultados de IA.
- El usuario puede distinguir asuntos activos de cerrados.

______________________________________________________________________

## 6.7 Notas del expediente

### Descripción

Registro de notas libres dentro de un asunto.

### Requerimientos

- Crear nota.
- Editar nota.
- Eliminar nota.
- Marcar nota como relevante.
- Usar una o varias notas como entrada para funciones de IA.

### Criterios de aceptación

- El usuario puede registrar información de una llamada o reunión.
- Las notas pueden alimentar el análisis de IA.

______________________________________________________________________

## 6.8 Documentos del expediente

### Descripción

Carga y organización simple de documentos.

### Tipos permitidos en MVP

- PDF.
- DOCX opcional.
- TXT opcional.
- Imágenes quedan fuera del MVP o solo como archivo almacenado sin OCR.

### Requerimientos

- Subir documento a un asunto.
- Ver lista de documentos.
- Descargar documento.
- Eliminar documento.
- Asignar tipo de documento manualmente.
- Extraer texto de PDF cuando sea técnicamente viable.
- Usar texto extraído como entrada para resumen o cronología.

### Tipos de documento sugeridos

- Identificación.
- Acta.
- Contrato.
- Recibo.
- Comprobante.
- Escrito.
- Notificación.
- Evidencia.
- Otro.

### Límites iniciales

- Tamaño máximo por archivo configurable.
- Número máximo de documentos por asunto configurable.
- No OCR masivo en MVP.
- No análisis automático al subir; el usuario debe solicitarlo.

### Criterios de aceptación

- El usuario puede subir documentos a un asunto.
- El sistema evita archivos demasiado grandes.
- Los documentos quedan asociados correctamente al expediente.

______________________________________________________________________

## 6.9 Checklists por tipo de asunto

### Descripción

Listas de documentos y datos que el abogado debe solicitar al cliente según el tipo de asunto.

### Requerimientos

- Mostrar checklist base según área legal.
- Permitir marcar elementos como completo, pendiente o no aplica.
- Permitir agregar elementos personalizados.
- Permitir generar mensaje para cliente con documentos faltantes.
- Permitir usar IA para sugerir checklist personalizado cuando el usuario tenga BYOK configurado.

### Checklists iniciales

- Pensión alimenticia.
- Divorcio básico.
- Despido / asunto laboral inicial.
- Cobro de deuda.
- Convenio de pago.
- Arrendamiento.
- Sucesorio básico.

### Criterios de aceptación

- El usuario puede ver qué documentos pedir.
- El usuario puede marcar avances.
- El usuario puede generar un mensaje con pendientes.

______________________________________________________________________

## 6.10 Tareas y recordatorios simples

### Descripción

Gestión básica de pendientes por asunto.

### Requerimientos

- Crear tarea.
- Asignar fecha límite opcional.
- Marcar como completada.
- Asociar tarea a asunto.
- Mostrar próximas tareas en dashboard.

### Fuera del MVP

- Notificaciones push.
- Sincronización con Google Calendar.
- Recordatorios por WhatsApp automático.

### Criterios de aceptación

- El usuario puede registrar pendientes del caso.
- El dashboard muestra tareas próximas.

______________________________________________________________________

## 6.11 Control básico de pagos

### Descripción

Registro simple de honorarios, anticipos, pagos y saldos por asunto.

### Requerimientos

- Registrar monto acordado.
- Registrar anticipo.
- Registrar pagos parciales.
- Calcular saldo.
- Agregar notas de pago.
- Generar mensaje de recordatorio de pago con IA o plantilla.

### Criterios de aceptación

- El usuario puede saber cuánto le debe un cliente.
- El sistema calcula saldo básico.

______________________________________________________________________

## 6.12 Calculadoras básicas

### Descripción

Herramientas de cálculo de bajo costo operativo y alto valor práctico.

### Calculadoras iniciales sugeridas

- Control de adeudo con abonos.
- Rentas vencidas.
- Interés simple.
- Estimación básica de liquidación/finiquito laboral.
- Honorarios y pagos parciales.

### Requerimientos

- Las calculadoras deben funcionar sin IA.
- Deben mostrar advertencia de que son estimaciones.
- Deben permitir copiar resultado.
- Deben permitir guardar resultado en un asunto.

### Criterios de aceptación

- El usuario puede realizar cálculos sin configurar IA.
- El resultado puede asociarse al expediente.

______________________________________________________________________

# 7. Funcionalidades de IA del MVP

Todas las funcionalidades de IA requieren BYOK configurado.

## 7.1 Analizador de relato inicial

### Descripción

El usuario pega un texto libre con el relato de un cliente y la IA lo convierte en información estructurada.

### Entrada

Texto libre escrito o pegado por el abogado.

### Salida esperada

- Tipo probable de asunto.
- Resumen breve.
- Hechos relevantes.
- Personas involucradas.
- Fechas mencionadas.
- Documentos sugeridos.
- Preguntas pendientes para el cliente.
- Próximos pasos sugeridos.

### Requerimientos técnicos

- La salida debe pedirse en formato JSON estructurado.
- La respuesta debe validarse antes de guardarse.
- Si la respuesta es inválida, debe mostrarse error controlado.

### Criterios de aceptación

- El usuario puede convertir un relato en ficha preliminar.
- El usuario puede guardar la ficha dentro de un asunto.

______________________________________________________________________

## 7.2 Generador de preguntas para cliente

### Descripción

Con base en el tipo de asunto y notas existentes, la IA sugiere preguntas que el abogado debe hacer al cliente.

### Salida esperada

- Preguntas faltantes.
- Datos críticos no proporcionados.
- Documentos que conviene pedir.

### Criterios de aceptación

- El usuario recibe una lista clara y editable.
- El resultado puede copiarse o guardarse.

______________________________________________________________________

## 7.3 Checklist personalizado con IA

### Descripción

La IA adapta un checklist base a la situación concreta del cliente.

### Requerimientos

- Partir de un checklist base determinístico.
- Usar IA solo para sugerir elementos adicionales o priorizar.
- Marcar claramente qué fue sugerido por IA.

### Criterios de aceptación

- El usuario puede aceptar o descartar sugerencias.
- El checklist resultante queda guardado en el asunto.

______________________________________________________________________

## 7.4 Resumen del expediente

### Descripción

La IA genera un resumen del asunto usando notas y, cuando exista, texto extraído de documentos.

### Salida esperada

- Resumen ejecutivo.
- Hechos principales.
- Partes involucradas.
- Estado actual.
- Documentos relevantes.
- Documentos faltantes.
- Riesgos o puntos de atención.
- Próximas acciones sugeridas.

### Límites

- Longitud máxima de entrada configurable.
- No analizar expedientes demasiado grandes en MVP.
- Guardar resultado para evitar llamadas repetidas.

### Criterios de aceptación

- El usuario puede generar y guardar un resumen.
- El sistema no vuelve a consumir IA si el usuario solo consulta el resumen guardado.

______________________________________________________________________

## 7.5 Cronología de hechos

### Descripción

La IA extrae una línea de tiempo a partir de notas o texto de documentos.

### Salida esperada

- Fecha.
- Hecho.
- Fuente o nota de origen, si está disponible.
- Relevancia.

### Criterios de aceptación

- El usuario puede ver eventos ordenados cronológicamente.
- El usuario puede editar la cronología manualmente.

______________________________________________________________________

## 7.6 Generador de mensajes para cliente

### Descripción

La IA genera mensajes claros para enviar por WhatsApp, email o copiar manualmente.

### Casos iniciales

- Pedir documentos faltantes.
- Explicar próximo paso.
- Recordar pago.
- Solicitar confirmación de cita.
- Explicar estado del asunto en lenguaje sencillo.

### Criterios de aceptación

- El usuario puede generar un mensaje corto.
- El mensaje puede copiarse al portapapeles.
- El usuario puede editar antes de enviar.

______________________________________________________________________

## 7.7 Borrador simple desde plantilla

### Descripción

La app genera borradores simples usando plantillas y datos capturados. No debe prometer generación automática de documentos legales complejos.

### Documentos iniciales sugeridos

- Carta de requerimiento de pago.
- Convenio de pago simple.
- Solicitud de documentos al cliente.
- Resumen de caso para archivo interno.
- Carta de terminación o aviso simple de arrendamiento.
- Escrito libre básico.

### Requerimientos

- Seleccionar tipo de documento.
- Capturar datos en formulario.
- Validar campos obligatorios.
- Usar IA para redactar secciones narrativas.
- Mostrar borrador editable.
- Exportar o copiar contenido.

### Criterios de aceptación

- El usuario puede generar un borrador editable.
- El sistema muestra advertencia de revisión profesional obligatoria.
- El documento no se envía ni presenta automáticamente.

______________________________________________________________________

# 8. Requerimientos no funcionales

## 8.1 Seguridad

- Autenticación segura.
- Separación de datos por usuario.
- Cifrado de API keys.
- No registrar información sensible innecesaria.
- No registrar prompts completos en logs técnicos sin protección.
- Permitir eliminación de datos del usuario.
- Control básico de acceso por propietario de cuenta.

## 8.2 Privacidad

- Mostrar aviso de privacidad.
- Explicar que el contenido enviado a IA se transmite al proveedor configurado por el usuario.
- Solicitar aceptación de términos antes de usar IA.
- Permitir al usuario eliminar documentos y asuntos.

## 8.3 Rendimiento

- La landing debe cargar rápidamente.
- El dashboard debe responder en menos de 2 segundos en uso normal.
- Las llamadas de IA pueden ser asíncronas si tardan demasiado.
- Los resultados de IA deben guardarse para evitar recomputación.

## 8.4 Costos operativos

El sistema debe diseñarse para operar con bajo costo mientras no existan ventas.

Medidas obligatorias:

- Landing estática.
- IA BYOK obligatoria.
- No IA incluida con costo absorbido por la plataforma en MVP.
- Límites de subida de archivos.
- Sin OCR masivo inicial.
- Sin chat libre con documentos.
- Cacheo/guardado de resultados IA.
- Workers apagables o escalables bajo demanda.

## 8.5 Disponibilidad

- El MVP no requiere alta disponibilidad empresarial.
- Debe poder correr en infraestructura económica.
- Debe contar con respaldos básicos de base de datos.

## 8.6 Escalabilidad

El diseño debe permitir evolucionar a:

- Planes pagados.
- Créditos IA propios.
- Más proveedores de IA.
- Equipos/despachos multiusuario.
- Exportación avanzada.
- Integraciones externas.

______________________________________________________________________

# 9. Arquitectura técnica sugerida

## 9.1 Frontend

- Next.js o React.
- Diseño responsive.
- Componentes reutilizables.
- Landing pública y app privada.

## 9.2 Backend

- FastAPI.
- API REST.
- Pydantic para validación.
- SQLAlchemy para persistencia.
- Alembic para migraciones.

## 9.3 Base de datos

- PostgreSQL.

## 9.4 Storage

- Storage compatible con S3.
- Guardar archivos fuera de la base de datos.
- Guardar metadata en PostgreSQL.

## 9.5 Jobs / procesamiento

Para MVP puede iniciarse con:

- Procesamiento síncrono controlado para funciones pequeñas.
- Tabla de jobs en PostgreSQL para tareas largas.

Después puede evolucionar a:

- Redis + RQ.
- Celery.
- Workers separados.

## 9.6 Capa de IA

Debe implementarse una abstracción multi-provider.

```text
AIProvider
  ├── OpenAIProvider
  ├── GeminiProvider
  └── MockProvider
```

Servicios internos sugeridos:

```text
IntakeAnalyzer
ClientQuestionGenerator
ChecklistPersonalizer
CaseSummarizer
TimelineExtractor
ClientMessageGenerator
DraftGenerator
```

Cada servicio debe:

- Construir prompt controlado.
- Enviar solicitud al provider activo del usuario.
- Solicitar salida estructurada cuando aplique.
- Validar respuesta.
- Guardar resultado.
- Registrar consumo estimado cuando sea posible.

______________________________________________________________________

# 10. Modelo de datos inicial sugerido

Entidades principales:

- User.
- Organization o Workspace.
- AIProviderCredential.
- Client.
- Matter.
- MatterNote.
- MatterDocument.
- Checklist.
- ChecklistItem.
- Task.
- PaymentRecord.
- CalculatorResult.
- AIJob.
- AIResult.
- Template.
- DraftDocument.

______________________________________________________________________

# 11. Roles y permisos del MVP

## 11.1 MVP

Solo se requiere:

- Propietario de cuenta.

## 11.2 Futuro

- Administrador.
- Abogado colaborador.
- Asistente.
- Solo lectura.
- Cliente externo.

______________________________________________________________________

# 12. Restricciones legales y éticas

- La app no debe afirmar que sustituye asesoría jurídica profesional.
- Toda salida generada por IA debe mostrarse como borrador o sugerencia.
- El abogado es responsable de revisar y validar el contenido.
- No debe darse asesoría legal directa al público general en el MVP.
- No debe garantizar resultados legales.
- Debe incluir advertencias visibles en funciones de IA.

Texto sugerido:

> Las respuestas generadas por IA son apoyo de redacción y organización. Deben ser revisadas por un profesional del derecho antes de utilizarse. Abogado Fácil no garantiza exactitud jurídica ni sustituye el criterio profesional.

______________________________________________________________________

# 13. Métricas iniciales

## 13.1 Producto

- Usuarios registrados.
- Usuarios que configuran API key.
- Clientes creados.
- Asuntos creados.
- Documentos subidos.
- Checklists completados.
- Borradores generados.

## 13.2 IA

- Número de llamadas por función.
- Errores por proveedor.
- Tiempo promedio de respuesta.
- Funciones IA más usadas.
- Resultados guardados vs regenerados.

## 13.3 Negocio

- Usuarios activos semanales.
- Conversión de landing a registro.
- Conversión de registro a configuración BYOK.
- Retención a 7 y 30 días.

______________________________________________________________________

# 14. Plan de entregas sugerido

## Fase 0 — Base pública

- Landing.
- Registro/login.
- Layout de app.
- Dashboard vacío.

## Fase 1 — Núcleo legal sin IA

- Clientes.
- Asuntos.
- Notas.
- Documentos.
- Checklists base.
- Tareas.

## Fase 2 — BYOK obligatorio

- Configuración de proveedor.
- Guardado cifrado de API key.
- Prueba de conexión.
- OpenAIProvider.
- GeminiProvider.
- MockProvider.

## Fase 3 — IA inicial

- Analizador de relato inicial.
- Generador de preguntas para cliente.
- Generador de mensajes para cliente.

## Fase 4 — Expediente asistido

- Resumen del expediente.
- Cronología de hechos.
- Checklist personalizado.

## Fase 5 — Documentos simples

- Plantillas.
- Borradores simples.
- Exportación o copia de contenido.

______________________________________________________________________

# 15. Definición de MVP completo

El MVP se considerará completo cuando:

1. Un usuario pueda registrarse e iniciar sesión.
1. Un usuario pueda configurar una API key propia de OpenAI o Gemini.
1. Un usuario pueda crear clientes y asuntos.
1. Un usuario pueda agregar notas y documentos a un asunto.
1. Un usuario pueda usar checklists base.
1. Un usuario pueda crear tareas y registrar pagos simples.
1. Un usuario pueda analizar un relato inicial con IA.
1. Un usuario pueda generar preguntas para cliente con IA.
1. Un usuario pueda generar un mensaje para cliente con IA.
1. Un usuario pueda generar resumen del expediente con IA.
1. Un usuario pueda generar cronología de hechos con IA.
1. Un usuario pueda generar al menos un borrador simple desde plantilla.
1. La app pueda operar sin absorber costos de IA del usuario.
1. La app tenga advertencias claras sobre revisión humana y responsabilidad profesional.

______________________________________________________________________

# 16. Fuera de alcance explícito del MVP

- Chat legal abierto.
- IA sin API key del usuario.
- Créditos IA pagados por la plataforma.
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

______________________________________________________________________

# 17. Riesgos principales

## 17.1 Fricción por BYOK

Muchos abogados no sabrán crear una API key.

Mitigación:

- Crear guía paso a paso.
- Mostrar videos cortos.
- Permitir modo demo con MockProvider.
- En el futuro, ofrecer plan con IA incluida.

## 17.2 Riesgo de confianza en IA

El usuario puede copiar contenido sin revisar.

Mitigación:

- Advertencias visibles.
- Resultados como borradores.
- Checklist de revisión.
- No automatizar envíos ni presentaciones.

## 17.3 Costos por documentos grandes

Los usuarios podrían intentar analizar expedientes grandes.

Mitigación:

- Límites por archivo.
- Límites por análisis.
- Resúmenes cacheados.
- Validación de tamaño antes de enviar a IA.

## 17.4 Seguridad de credenciales

Las API keys son sensibles.

Mitigación:

- Cifrado.
- No exposición al frontend.
- No logs.
- Eliminación por usuario.

______________________________________________________________________

# 18. Roadmap posterior al MVP

Posibles extensiones:

- Planes pagados.
- IA incluida con créditos.
- Exportación avanzada a DOCX/PDF.
- Portal para clientes.
- Integración con WhatsApp Business.
- OCR de imágenes.
- Búsqueda semántica en expedientes.
- RAG por expediente.
- Plantillas por estado/entidad federativa.
- Biblioteca de formatos.
- Multiusuario por despacho.
- Calendario avanzado.
- Integración con Google Calendar.
- Pagos en línea.
- Facturación.

______________________________________________________________________

# 19. Descripción corta para portafolio

**Abogado Fácil** es un SaaS web para abogados independientes que permite organizar clientes, asuntos, documentos, checklists, tareas y pagos, integrando inteligencia artificial mediante un modelo BYOK con OpenAI o Gemini. El sistema usa IA en flujos controlados como análisis de relatos, generación de preguntas, resúmenes de expediente, cronologías, mensajes para cliente y borradores simples desde plantilla.

______________________________________________________________________

# 20. Descripción técnica para CV o LinkedIn

Diseño y desarrollo de un SaaS legal multiusuario con FastAPI, React/Next.js, PostgreSQL y almacenamiento de documentos, integrando proveedores de IA mediante arquitectura BYOK multi-provider. Implementación de flujos asistidos con IA para análisis estructurado de relatos, generación de checklists, resúmenes de expediente, cronologías y borradores documentales, con validación de salidas, control de credenciales, seguridad básica, límites de uso y enfoque de bajo costo operativo.
