# Fase 3 - IA inicial controlada

## Estado

- Tickets: `AI-101`, `AI-102`, `AI-103`, `UX-AI-001`, `AI-104`, `AI-105`, `AI-106`, `LEGAL-002B`
- Estado: Implementado
- Última actualización: 2026-08-01

La segunda auditoría de cierre del 2026-07-29 reabrió `AI-104` y `AI-105`: el estado local de
aceptación podía sobrevivir a un error de persistencia y una edición posterior a la aceptación no
bloqueaba la conversión.

## Entregado

- Tres funciones reales: análisis de relato, preguntas y mensaje para cliente.
- Vista previa obligatoria de fuentes, proveedor, modelo, tamaño y costo BYOK.
- Contexto minimizado, salida JSON validada y ciclo de vida `AIJob`.
- Resultado persistente y aislado por despacho/asunto/usuario, con procedencia y versión.
- Edición, aceptación total/parcial, rechazo, reporte y acciones derivadas.
- Revisión humana reusable y accesible; copiar queda bloqueado hasta aceptar.
- Aviso de resultado desactualizado cuando cambia el asunto.

## Validación

- `.\.venv\Scripts\python.exe -m pytest backend/tests/features/ai_assistance backend/tests/docs/test_documentation_contracts.py -q`:
  39 pruebas pasan.
- `npm --prefix frontend run check`: lint, tipos, contratos, cobertura y 261 pruebas pasan.
- `npm --prefix frontend run build`: build y presupuestos de rendimiento aprobados.
- `npm --prefix frontend run test:e2e:ci`: 14 pruebas pasan.

## Hallazgos de reapertura

- [x] Completar `SEC-001B` y registrar evidencia negativa multiusuario antes de liberar llamadas
  reales; el backlog lo mantiene como gate `P0-IA`.
- [x] Vincular criptográficamente o mediante token opaco la vista previa con el payload ejecutado;
  cambiar relato, proveedor, modelo o fuentes debe invalidar la confirmación.
- [x] Revalidar el contenido editado contra el esquema de su función antes de aceptar o convertir.
- [x] Reemplazar la edición y copia de JSON crudo por presentaciones estructuradas para análisis,
  preguntas y mensajes.
- [x] Restaurar correctamente el estado de copia para resultados aceptados después de recargar.
- [x] Implementar regeneración explícita con procedencia respecto del resultado anterior.
- [x] Convertir resultados en entidades reales de nota, tarea y checklist cuando corresponda; las
  acciones `question`, `missing_document` y `message` deben tener persistencia y semántica explícitas.
- [x] Mostrar procedencia, versión de fuentes y estado desactualizado en la interfaz.
- [x] Sincronizar OpenAPI y actualizar matrices, endpoints, mutaciones y e2e con los contratos finales.
- [x] Añadir e2e del hero flow: preview, ejecución, revisión, copia y conversión.

## Orden de corrección

1. Cerrar el contrato preview/execute y la revalidación backend.
1. Corregir revisión, copia y presentación estructurada frontend.
1. Implementar regeneración y conversión en acciones reales.
1. Completar procedencia/desactualización y el gate `SEC-001B`.
1. Sincronizar documentación/OpenAPI y ejecutar todos los gates.

## Registro de progreso

| Fecha      | Estado      | Completado                                                                                                                                                                                  | Pendiente / próxima acción segura                                                        |
| ---------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 2026-07-29 | Reabierto   | Auditoría full-stack, backlog sincronizado y plan movido nuevamente a `pending`.                                                                                                            | Implementar vínculo obligatorio entre preview y ejecución, con pruebas backend/frontend. |
| 2026-07-29 | En progreso | Token HMAC vinculado a entradas y versión de fuentes; preview se invalida al editar; revisión revalidada por esquema; copia persistida restaurada y contenido copiable sin envoltura JSON.  | Implementar UI de edición estructurada y conversiones de dominio reales.                 |
| 2026-07-29 | En progreso | Edición principal estructurada por función, detalles legibles, procedencia visible, regeneración enlazada y conversiones que crean notas, tareas o checklist reales e invalidan sus cachés. | Completar `SEC-001B`, e2e del hero flow y gates completos.                               |
| 2026-07-29 | Hecho       | `SEC-001B`, OpenAPI, documentación, backend 100% coverage, frontend check/build y 14 e2e completos.                                                                                         | Ninguna.                                                                                 |
| 2026-07-29 | Reabierto   | Segunda auditoría detectó aceptación local optimista y conversión visible después de editar.                                                                                                | Corregir estado confirmado y añadir regresiones.                                         |
| 2026-07-29 | Hecho       | Aceptación depende de persistencia; editar bloquea copia/conversión; 5 pruebas dirigidas, check con 261 pruebas, build, contratos y 14 e2e aprobados.                                       | Ninguna.                                                                                 |

## Pausa / handoff

- Estado actual: backend, frontend, contratos y documentación cerrados; las dos inconsistencias de
  estado frontend quedaron corregidas y cubiertas.
- Contratos afectados: API/OpenAPI de asistencia IA, revisión humana, consumidores frontend,
  conversiones de dominio, procedencia y e2e.
- Bloqueadores de release: `SEC-001C` y `SEC-002`.
- Riesgo residual: la exactitud y costo dependen del proveedor/modelo BYOK; la revisión humana sigue
  siendo obligatoria y no existe envío automático.
- Próxima acción segura: ejecutar `SEC-001C`; luego completar `SEC-002` y revalidar el release IA.

## Exclusiones y riesgo residual

No hay envío automático, WhatsApp API, correo transaccional ni chat legal abierto. La exactitud y
el costo dependen del proveedor/modelo BYOK; todo resultado conserva el aviso y exige revisión.
