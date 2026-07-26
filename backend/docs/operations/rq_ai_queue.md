# Cola de IA con RQ y Redis

## Runtime

El proceso FastAPI produce trabajos mediante `RQJobScheduler`; el servicio `ai-worker` de Compose
consume la cola configurada en `AI_QUEUE_NAME`. Ambos usan RQ 2.10, el mismo Redis y
`rq.serializers.JSONSerializer`. El worker se ejecuta con scheduler porque los retries diferidos lo
requieren.

PostgreSQL y `AIJob` siguen siendo la fuente de verdad. El estado de RQ es transporte operativo y
no sustituye el lifecycle persistente.

## Frontera de datos

Redis recibe únicamente:

- el nombre de un handler registrado en el catálogo interno;
- el `execution_id` opaco como único argumento;
- metadata operativa de RQ: timeout, TTL, retry e identificador determinista.

No se permiten prompts, credenciales, contexto legal, texto documental, resultados ni mensajes de
error de proveedor. Se usa JSON porque el serializer pickle predeterminado de RQ no es apropiado
para esta frontera.

## Resiliencia

- El ID RQ es `ai-<execution_id>`.
- `unique=True` evita encolados simultáneos duplicados; un duplicado devuelve el mismo ID.
- `AI_QUEUE_JOB_TIMEOUT_SECONDS` limita cada intento.
- `AI_QUEUE_MAX_RETRIES` y `AI_QUEUE_RETRY_BACKOFF_SECONDS` definen retries diferidos.
- Los TTL de espera, éxito y fallo son explícitos. Los resultados exitosos no se conservan en Redis
  por defecto (`AI_QUEUE_RESULT_TTL_SECONDS=0`).
- Compose ejecuta un worker por defecto, limitando la concurrencia inicial a uno. Una cuota
  distribuida por proveedor requiere handlers reales y se cerrará antes de habilitar una función IA
  pública; RQ 2.10 publicado no expone aún la API `RateLimit` descrita por documentación futura.

## Registro de handlers

`RQJobScheduler` recibe un mapa explícito `job_name -> dotted function path`. Un nombre no
registrado se rechaza antes de tocar Redis. AI-010 deja el catálogo de producción vacío; el primer
ticket funcional de IA debe registrar su handler y demostrar que reconstruye contexto autorizado
desde PostgreSQL usando únicamente `execution_id`.
