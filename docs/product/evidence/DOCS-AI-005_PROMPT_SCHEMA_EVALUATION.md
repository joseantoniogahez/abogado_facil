# Evaluación de prompts y schemas de IA

## Método

La línea base `phase3-v1` se evalúa como contrato, no como benchmark de exactitud de un modelo. Cada
caso verifica instrucción versionada, contexto permitido, schema cerrado, manejo del fallo y gate de
revisión humana. Los proveedores reales se sustituyen por dobles deterministas; por tanto, estos
resultados prueban seguridad y reproducibilidad, no calidad comparativa OpenAI/Gemini.

## Matriz de evaluación

| Función                 | Invariantes del prompt                     | Schema / límites principales           | Casos de fallo cubiertos                              |
| ----------------------- | ------------------------------------------ | -------------------------------------- | ----------------------------------------------------- |
| `intake_analysis`       | no asesoría definitiva; no inventar        | resumen 4,000; hechos y listas máx. 20 | JSON inválido, campos extra, aceptación sin contenido |
| `client_questions`      | preguntas neutrales; no inventar           | preguntas máx. 30; listas máx. 20      | lista vacía, tipos incorrectos                        |
| `client_message`        | tono prudente; no prometer                 | canal cerrado; mensaje 8,000           | canal desconocido, mensaje vacío                      |
| `matter_summary`        | neutral, verificable, distingue pendientes | resumen 5,000; listas máx. 30          | shape incompleto, resultado stale                     |
| `matter_timeline`       | no inventar fechas; citar fuente           | 1–50 eventos; fecha válida o `null`    | fecha inválida; orden no cronológico se normaliza     |
| `checklist_suggestions` | no repetir base ni marcar completo         | 1–30 sugerencias                       | lista vacía, elemento inválido                        |
| `document_draft.*`      | sólo datos aportados; sin citas inventadas | `content` 1–30,000                     | campo desconocido, preview stale, JSON inválido       |

## Resultados observados

- El contexto excluye por defecto notas, documentos, pagos y tareas; la descripción del asunto es
  opt-in visible en preview.
- Datos adversariales permanecen en el canal no confiable, escapados y sin herramientas.
- Gemini recibe el JSON schema esperado y todos los proveedores vuelven a validarse localmente.
- Una salida inválida se clasifica `provider_invalid_response`, no se reintenta ni persiste.
- Aceptación parcial/total vuelve a validar el contenido editado contra el schema de la función.

## Gestión de cambios

`prompt_version` y `schema_version` deben cambiar cuando una modificación altera significado,
campos, restricciones o interpretación. Cada cambio añade casos a esta matriz, conserva fixtures de
regresión y compara al menos: validez estructural, invención de datos, omisiones críticas, manejo de
entrada adversarial y utilidad reportada. La selección de una versión nueva requiere revisión
humana; no se promueve sólo porque produzca más texto.
