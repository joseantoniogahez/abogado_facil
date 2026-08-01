# PROD-AI-001 - Evidencia del hero flow

## Resultado demostrado

Un abogado puede convertir un relato inicial en información accionable dentro de un expediente sin
omitir la revisión humana ni ejecutar acciones automáticas.

## Precondiciones

- Sesión autenticada y asunto perteneciente al despacho.
- Credencial BYOK válida y consentimiento vigente.
- Función `intake_analysis` disponible.

## Recorrido reproducible

1. Abrir el resumen del asunto e ingresar un relato suficientemente descriptivo.
1. Solicitar el preview y revisar proveedor, modelo, fuentes incluidas/excluidas, tamaño y costo BYOK.
1. Confirmar la ejecución con el token firmado; el backend vuelve a validar contexto y límites.
1. Recibir una salida estructurada y persistida con procedencia y estado de revisión pendiente.
1. Editar si es necesario y aceptar explícitamente el resultado.
1. Copiar o convertir contenido; la prueba convierte el resumen aceptado en una nota real.
1. Abrir documentos y notas y comprobar que la entidad creada aparece en el expediente.

## Evidencia automatizada

- E2E: `frontend/e2e/foundation-smoke.spec.ts`, escenario
  `completes the initial-narrative hero flow into an actionable expediente`.
- El mock contractual exige el token de confirmación, devuelve un resultado persistido, registra la
  aceptación, crea la nota y comprueba su visibilidad final.
- Los contratos backend cubren aislamiento tenant, validación de salida, revisión y conversión.

## Decisiones y límites

- El cliente y asunto se crean antes del análisis; el relato no crea entidades sin confirmación.
- No existe envío automático de mensajes ni actuación jurídica autónoma.
- Exactitud, costo y latencia dependen del proveedor/modelo BYOK.
- Feedback de utilidad y métricas agregadas pertenecen a tickets posteriores.

## Criterio de aprobación

El hero flow se considera aprobado cuando E2E, frontend check/build y contratos documentales pasan,
y no existen defectos P0/P1 abiertos sobre el recorrido.
