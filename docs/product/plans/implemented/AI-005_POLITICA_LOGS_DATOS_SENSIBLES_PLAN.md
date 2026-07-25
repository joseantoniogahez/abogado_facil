# AI-005 - Política de logs y datos sensibles de IA

## Estado del tracking

- ID: `AI-005`
- Tipo: Ops
- Prioridad: P0-IA
- Estado: Hecho
- Competencia de portafolio: `BE-AI`

## Objetivo

Evitar que prompts, texto documental, credenciales o detalles sensibles de proveedores lleguen a
los logs técnicos, manteniendo eventos operativos mínimos y correlacionables.

## Alcance

- Redacción centralizada de campos sensibles en eventos estructurados.
- Cobertura negativa para prompts, contenido de documentos, API keys y excepciones.
- Documentación de la política para nuevos flujos de IA.

## Criterios de aceptación

- [x] El helper de observabilidad no emite valores de campos sensibles.
- [x] Los errores de proveedor conservan un mensaje seguro sin cuerpos ni secretos.
- [x] Las pruebas negativas cubren contenido de entrada, credenciales y errores.
- [x] La política queda documentada y los gates backend pasan.
- [x] Las credenciales de proveedor se transportan en headers y nunca en URLs observables.

## Validación

- `python -m pytest backend/tests`
- `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- `pre-commit run --files ...` sobre los archivos modificados.

## Registro de avance

| Fecha      | Estado      | Nota                                                                                                |
| ---------- | ----------- | --------------------------------------------------------------------------------------------------- |
| 2026-07-24 | En progreso | Iniciada implementación desde el helper común de observabilidad.                                    |
| 2026-07-24 | Hecho       | Redacción centralizada, pruebas negativas y política documentada. 430 tests y cobertura 100% pasan. |

## Validaciones ejecutadas

- `\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` — 431 passed, 100% coverage.
- `pre-commit run --all-files` — todos los hooks pasaron.

## Revisión documental

Revisados `AGENTS.md`, `docs/ai/backlog_tracking.md`, los READMEs, ambos playbooks, arquitectura,
error mapping y contratos frontend. Se documentó el transporte de credenciales por headers; no
cambian API, auth, permisos, rutas ni OpenAPI.
