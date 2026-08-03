# Caso de estudio: relato inicial a expediente accionable

## Problema

Un abogado recibe un relato desordenado y necesita identificar hechos, faltantes y próximos pasos
sin perder control sobre qué datos salen del expediente ni tratar una respuesta probabilística como
criterio jurídico.

## Solución entregada

El flujo crea primero cliente y asunto; luego muestra un preview con fuentes, proveedor, modelo,
tamaño y costo BYOK. La confirmación firmada liga esos datos a la ejecución. El resultado atraviesa
un schema cerrado, se guarda con procedencia y queda pendiente de revisión. Sólo tras editar y
aceptar puede convertirse explícitamente en una nota, tarea, pregunta, checklist, documento faltante
o mensaje.

```mermaid
flowchart LR
    R[Relato] --> P[Preview y consentimiento]
    P --> E[Ejecución BYOK]
    E --> V[Validación estructurada]
    V --> H[Revisión humana]
    H --> A[Acción del expediente]
```

## Decisiones y riesgos

- Preview y ejecución se separan para impedir consentimiento implícito o contexto stale.
- BYOK evita costo centralizado, a cambio de fricción de configuración y cuota externa.
- El modelo no tiene herramientas; la conversión es una acción posterior y explícita.
- Aislamiento por `firm_id`, contexto mínimo, redacción, schemas y revisión reducen riesgo, pero no
  garantizan exactitud. El abogado conserva responsabilidad sobre el uso del borrador.

## Evidencia y métricas

El E2E `completes the initial-narrative hero flow into an actionable expediente` recorre preview,
ejecución, aceptación y creación de una nota visible. Los contratos backend cubren tenant, preview
stale, errores seguros y schemas. El dashboard ofrece éxito/fallo, latencia, tokens estimados,
retries, jobs atascados, aceptación, edición, conversión, regeneración, abandono y feedback.

No se declara una mejora cuantitativa de tiempo o calidad: el repositorio no contiene una muestra
de producción ni mediciones longitudinales. El resultado observado y reproducible es funcional:
una salida estructurada revisada se convierte en una entidad persistida sin acción autónoma.

## Próxima medición útil

En un piloto autorizado se deben fijar tamaño de muestra y periodo, y reportar por función tasa de
aceptación, corrección, fabricación, conversión y tiempo hasta acción, sin mezclar despachos ni
exponer contenido legal.
