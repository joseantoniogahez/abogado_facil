# DEMO-AI-001 - Guion de demo técnica y de producto

## Objetivo

Demostrar, en 12–15 minutos, que Abogado Fácil convierte un relato en una acción de expediente con
BYOK, aislamiento, preview, salida estructurada y revisión humana; después demostrar que los fallos
son seguros y reproducibles.

## Preparación

- Levantar el entorno local de Docker y crear datos con el procedimiento de `OPS-010`.
- Tener un usuario autenticado, un asunto propio y una credencial BYOK válida; para una demo sin
  costo externo se puede recorrer la evidencia automatizada con los dobles contractuales.
- Abrir `/settings/ai`, `/matters/{matter_id}` y `/ai/insights` en pestañas separadas.
- No usar expedientes reales ni mostrar API keys, prompts, cuerpos de proveedor o datos personales.

## Recorrido principal

| Tiempo | Acción                                           | Evidencia que debe verse                                      |
| ------ | ------------------------------------------------ | ------------------------------------------------------------- |
| 0:00   | Presentar el asunto y la separación por despacho | sesión protegida y expediente propio                          |
| 1:30   | Mostrar configuración BYOK                       | proveedor configurado sin revelar el secreto                  |
| 3:00   | Capturar un relato y pedir preview               | fuentes incluidas/excluidas, modelo, tamaño y costo BYOK      |
| 5:00   | Confirmar la ejecución                           | resultado estructurado, procedencia y revisión `pending`      |
| 7:00   | Editar y aceptar el resultado                    | contenido revisado y estado `accepted`                        |
| 9:00   | Convertir el resumen en nota                     | nota persistida y visible en el expediente                    |
| 10:30  | Mostrar insights                                 | éxito, latencia, tokens estimados, aceptación y conversión    |
| 12:00  | Cerrar con límites                               | sin herramientas, sin acción autónoma y sin garantía jurídica |

## Escenarios de fallo

1. **Preview obsoleto:** cambiar relato, fuentes, modelo o asunto después del preview. La ejecución
   debe responder conflicto y exigir un preview nuevo.
1. **Credencial ausente o inválida:** intentar ejecutar sin BYOK válido. La llamada real no debe
   comenzar y el secreto nunca debe aparecer en la respuesta.
1. **Rate limit o timeout:** usar el mock contractual correspondiente. Debe mostrarse el mensaje
   seguro y la taxonomía estable; sólo fallos transitorios son reintentables.
1. **Salida inválida:** devolver JSON malformado o fuera del schema. No se guarda, no se reintenta y
   no se habilita conversión.
1. **Prompt injection documental:** incluir texto que intente cerrar el sobre o pedir herramientas.
   Debe permanecer como dato escapado; las herramientas siguen deshabilitadas.
1. **Acceso cruzado:** solicitar un asunto o resultado de otro despacho. La respuesta debe ser `404`
   opaco y no revelar existencia ni contenido.

## Reproducción automatizada

El recorrido canónico está en `frontend/e2e/foundation-smoke.spec.ts`, escenario
`completes the initial-narrative hero flow into an actionable expediente`. Se ejecuta con:

```powershell
npm --prefix frontend run test:e2e:ci
```

Los fallos multi-provider, contexto adversarial, schemas y aislamiento están cubiertos en las
suites backend. El catálogo operativo está en
`backend/docs/operations/ai_failure_catalog.md` y el caso de estudio en
`docs/product/evidence/DOCS-AI-006_HERO_FLOW_CASE_STUDY.md`.

## Criterio de cierre

La demo es reproducible cuando el E2E canónico y los gates backend/frontend pasan, cada fallo
produce el contrato esperado y no quedan tickets abiertos en el backlog del ciclo.
