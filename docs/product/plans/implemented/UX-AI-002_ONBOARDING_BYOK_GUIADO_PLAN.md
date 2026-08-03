# UX-AI-002 - Onboarding BYOK guiado

## Tracking Status

- ID: `UX-AI-002`
- Type: `Frontend`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-08-02`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Guiar a una persona sin experiencia previa con API keys desde la elección del proveedor hasta una
conexión utilizable, con instrucciones accionables, validación mediante el catálogo dinámico y un
recorrido demostrativo inequívoco que no contacte proveedores ni consuma saldo.

## Starting Point

`/settings/ai` permite guardar y eliminar claves de OpenAI y Gemini, pero presenta ambos formularios
a la vez, no explica dónde obtener la clave y no muestra si la credencial permite descubrir modelos.
El backend expone el catálogo dinámico para proveedores reales. `MockProvider` es un adaptador
interno de pruebas y no forma parte del contrato público, por lo que el modo demo debe permanecer
local y declararse como simulación sin llamadas de IA.

## Scope

### Included

- Flujo guiado para elegir OpenAI, Gemini o un recorrido demostrativo.
- Instrucciones específicas, advertencia de costo y tratamiento seguro de la clave.
- Guardado de una credencial real seguido de validación mediante el catálogo de modelos.
- Estados accionables para validación pendiente, exitosa o fallida.
- Demo local explícita con datos mock, sin persistencia ni llamadas a proveedores.
- Gestión posterior para reemplazar o eliminar credenciales existentes.

### Excluded

- Exponer `MockProvider` como proveedor público del backend.
- Videos externos, enlaces de afiliación o catálogos de modelos precargados.
- Cambiar cifrado, endpoints, OpenAPI, autenticación o autorización.

## Dependencies and Decisions

- Dependencies: `AI-002` y `AI-013`, ambos `Hecho`.
- Decisions closed: la validación real usa `/ai/credentials/models`; la demo es local, explícita y
  no genera contenido jurídico ni tráfico a proveedor; no se agregan dependencias.
- Open questions: ninguna bloqueante.

## Acceptance Criteria

- [x] La pantalla guía la elección de proveedor, obtención de clave, guardado y comprobación.
- [x] Cada proveedor muestra instrucciones y costo/responsabilidad de forma clara.
- [x] Una clave guardada se considera conectada solo cuando el catálogo devuelve modelos para ella.
- [x] Los fallos de comprobación conservan un estado seguro y ofrecen reintento o reemplazo.
- [x] El modo demo se identifica como simulación mock, no pide clave y no hace solicitudes de IA.
- [x] Las credenciales ya configuradas siguen pudiéndose reemplazar y eliminar.
- [x] Los estados principales son accesibles y están cubiertos por pruebas.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                 | Change required |
| ------- | ----------------------------------------------------------- | --------------- |
| Runtime | `features/ai-settings`, catálogo compartido e i18n          | yes             |
| Tests   | `AiSettingsPage.test.tsx`, accesibilidad enfocada           | yes             |
| Docs    | capacidad IA, README frontend, consumidores y accesibilidad | review/update   |

## Work Plan

### Implementation

- [x] Convertir la pantalla en un onboarding progresivo con gestión de credenciales.
- [x] Integrar la comprobación del catálogo después del guardado y bajo reintento explícito.
- [x] Añadir el recorrido mock local sin solicitudes de IA.

### Tests and Documentation

- [x] Actualizar pruebas de interacción, error, demo y accesibilidad.
- [x] Revisar y sincronizar la documentación canónica afectada.

### Validation

- [x] Prueba enfocada de `AiSettingsPage`.
- [x] `npm --prefix frontend run openapi:check`
- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run build`
- [x] Pre-commit en archivos cambiados.

## Progress Log

| Date       | State       | Completed                                                                                     | Pending / next safe action               |
| ---------- | ----------- | --------------------------------------------------------------------------------------------- | ---------------------------------------- |
| 2026-08-02 | En progreso | Alcance recuperado; contratos y límites del mock verificados; backlog sincronizado.           | Implementar el onboarding y sus pruebas. |
| 2026-08-02 | Hecho       | Onboarding, comprobación dinámica, demo mock local, pruebas, e2e y documentación completados. | Ninguno.                                 |

## Validation Results

| Date       | Command                                                    | Result | Notes                                           |
| ---------- | ---------------------------------------------------------- | ------ | ----------------------------------------------- |
| 2026-08-02 | Prueba enfocada de `AiSettingsPage`                        | Passed | 5 pruebas.                                      |
| 2026-08-02 | `npm --prefix frontend run check`                          | Passed | Lint, tipos, cobertura, OpenAPI y dependencias. |
| 2026-08-02 | `npm --prefix frontend run build`                          | Passed | Build y presupuestos de rendimiento.            |
| 2026-08-02 | `npm --prefix frontend run test:e2e:ci`                    | Passed | 14 escenarios Chromium.                         |
| 2026-08-02 | `.\.venv\Scripts\python.exe -m pre_commit run --all-files` | Passed | Todos los hooks.                                |

## Pause / Handoff Record

- Current state: implementación y gates completos.
- Changed files and contracts: onboarding IA, textos, smoke e2e y documentación de capacidad,
  consumidor, mutaciones y accesibilidad.
- Pending work: ninguno.
- Blockers or approvals: ninguno.
- Residual risks: la comprobación depende de disponibilidad y permisos del proveedor real.
- Next safe action: continuar con `DOCS-AI-001`, siguiente grupo priorizado del backlog.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- README raíz y backend docs: sin cambios porque no cambió backend, instalación ni despliegue.
- Route inventory y foundation status: sin cambios porque la ruta, acceso y gates no cambiaron.
- OpenAPI: sin cambios, confirmado por `openapi:check`.

## Completion Summary

- Delivered: onboarding BYOK progresivo, comprobación dinámica accionable y demo mock local explícita.
- Validation: prueba enfocada, check, build, 14 e2e y pre-commit pasaron.
- Skipped validation: ninguna requerida.
- Human approvals: no aplican.
- Residual risk: el descubrimiento real depende de disponibilidad, cuota y permisos del proveedor;
  la interfaz lo comunica y ofrece reintento o reemplazo.
