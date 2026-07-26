# Metricas iniciales de IA

## Contrato

`AIMetricsRegistry` registra exactamente una observacion al terminar cada llamada de proveedor. La
instrumentacion vive en `_ObservedAiProvider`, por lo que aplica de forma uniforme a OpenAI,
Gemini y Mock.

Cada serie usa solamente estas etiquetas de cardinalidad acotada:

- `provider`: adaptador interno (`openai`, `gemini` o `mock`);
- `function`: identificador estable de funcion declarado en `AiTextRequest`;
- `outcome`: `success` o `failure`;
- `error_code`: ausente en exito; codigo normalizado de `AI-011` en fallos conocidos o
  `internal_error` en fallos inesperados.

Por serie, el snapshot expone `call_count`, `total_duration_ms`, `max_duration_ms` y
`average_duration_ms`. No contiene `request_id`, `execution_id`, usuario, despacho, modelo, prompt,
contexto, respuesta ni credencial.

## Seguridad y cardinalidad

Proveedor, funcion y codigo de error deben cumplir una etiqueta acotada de hasta 64 caracteres. No
se aceptan espacios, texto externo ni valores arbitrarios del proveedor. La duracion debe ser
finita y no negativa.

`function` identifica un tipo de operacion, no un asunto, documento, usuario o ejecucion. Los casos
de uso deben reutilizar identificadores estables como `initial-story` o `matter_summary`.

## Alcance operativo

`AI_METRICS` es un registro local por proceso y permite pruebas, diagnostico inicial e integracion
posterior con un exportador. Reiniciar o escalar workers reinicia o distribuye sus acumulados; no es
un almacen historico ni una fuente de facturacion. La exportacion y agregacion multiproceso se
dejan para `OBS-002`.

Las metricas complementan los eventos correlacionados de `OBS-001`: los eventos permiten seguir
una ejecucion, mientras las metricas permiten observar volumen, tasa de error y latencia agregada.
