# Ciclo de vida persistente de ejecuciones de IA

## Alcance

`app.features.ai_jobs` registra ejecuciones de IA como una capacidad backend interna. No expone un
router ni ejecuta proveedores por sí misma. Las funciones IA futuras deben crear y transicionar un
`AIJob` mediante el servicio antes de persistir o mostrar un resultado.

## Datos y aislamiento

Cada job conserva:

- `execution_id` opaco y único, además del `request_id` de la solicitud;
- `firm_id` y `user_id`, obligatorios en toda lectura y mutación;
- función, proveedor, modelo, versión de prompt y versión de schema;
- estado, número de intentos y timestamps de inicio/finalización;
- resultado JSON estructurado o un código de error seguro.

No se almacenan prompts, credenciales, texto de documentos, respuestas sin validar ni mensajes de
error del proveedor. Las consultas sin coincidencia exacta de despacho y usuario se comportan como
recurso inexistente.

## Estados y transiciones

| Estado origen | Transición permitida  | Estado destino |
| ------------- | --------------------- | -------------- |
| `queued`      | iniciar               | `running`      |
| `queued`      | cancelar              | `cancelled`    |
| `running`     | completar             | `succeeded`    |
| `running`     | fallar                | `failed`       |
| `running`     | cancelar              | `cancelled`    |
| `failed`      | iniciar nuevo intento | `running`      |

`succeeded` y `cancelled` son terminales. Cada inicio incrementa `attempt_count`. Las transiciones
bloquean la fila dentro de Unit of Work y rechazan estados incompatibles. Un job exitoso exige
resultado y no permite error; un job fallido exige `error_code` y no permite resultado.

## Límites de responsabilidad

- `AI-010` añadirá política de retry, backoff y prevención de duplicados.
- `AI-011` definirá la taxonomía completa que alimentará `error_code`.
- `OBS-001` conectará la correlación persistente con el recorrido completo hacia proveedor.
- Los endpoints de producto decidirán qué resultados estructurados están autorizados y validados.
