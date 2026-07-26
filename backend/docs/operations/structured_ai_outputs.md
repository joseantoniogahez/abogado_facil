# Validación de salidas estructuradas de IA

## Contrato

El texto devuelto por cualquier proveedor es dato externo no confiable. Antes de guardar, mostrar,
copiar, exportar o usar un resultado, cada función IA debe:

1. declarar un schema Pydantic cerrado y una `schema_version`;
1. pasar el texto completo a `validate_ai_output`;
1. operar únicamente con el `ValidatedAIOutput` resultante;
1. completar el `AIJob` mediante `AIJobsService.succeed`.

`validate_ai_output` parsea JSON, valida tipos, campos requeridos y las restricciones declaradas por
el schema, y normaliza el resultado a valores JSON-safe. Los schemas de producto deben usar
`extra="forbid"` cuando no acepten propiedades adicionales.

## Gate de persistencia

`AIJobsService.succeed` rechaza diccionarios y otros valores sin la marca `ValidatedAIOutput`.
También exige que `ValidatedAIOutput.schema_version` coincida exactamente con
`AIJob.schema_version`. Sólo entonces entrega los datos normalizados al repositorio.

Este gate impide que un caso de uso olvide la validación antes de persistir. Las futuras superficies
de lectura, copia o exportación deben consumir exclusivamente el resultado estructurado ya
persistido; nunca deben recuperar texto crudo del proveedor.

## Fallos seguros

JSON malformado, shape incorrecto, tipos incompatibles, campos adicionales prohibidos o un root no
basado en objeto producen `provider_invalid_response`. El error es no reintentable y no contiene el
texto recibido ni detalles internos de Pydantic.

Una versión distinta a la registrada en el job produce un error interno de entrada inválida antes
de escribir. Ni el texto original ni los detalles de validación se persisten o registran.

No existe reparación automática de JSON. Un caso de uso futuro que implemente una corrección debe
tratarla como otra llamada versionada, observable y limitada, y volver a pasar por el mismo gate.

## Verificación

- `backend/tests/integrations/test_ai_outputs.py` cubre parseo, normalización, copia defensiva y
  fallos seguros.
- `backend/tests/features/ai_jobs/test_service.py` demuestra que resultados arbitrarios o con una
  versión distinta no pueden completar un job.
