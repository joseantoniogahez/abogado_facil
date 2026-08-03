# AI-013 - Descubrimiento de modelos por credencial BYOK

## Tracking Status

- ID: `AI-013`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Completed`
- Implementation status: `Hecho`
- Last updated: `2026-08-01`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Construir el selector de proveedor y modelo desde las credenciales BYOK configuradas y los modelos
que cada API key puede consultar, eliminando los catálogos GPT/Gemini precargados.

## Starting Point

La UI muestra siempre OpenAI y Gemini mediante `MODEL_OPTIONS` y `DEFAULT_MODELS` estáticos. El
backend cifra las credenciales por usuario/despacho, pero no ofrece un catálogo seguro de
proveedores configurados y modelos disponibles.

## Scope

### Included

- Exponer un endpoint autenticado que liste solo proveedores con credencial configurada para el
  usuario y despacho actuales.
- Consultar desde backend la API de cada proveedor configurado y normalizar sus modelos.
- No invocar un proveedor que no tenga credencial.
- Filtrar o marcar modelos según su compatibilidad con las funciones IA del producto.
- Sustituir opciones y defaults estáticos por estados dinámicos de carga, vacío, éxito y error.
- Actualizar el catálogo después de guardar o eliminar una credencial.
- Conservar `mock` solo como modo demostrativo explícito coordinado con `UX-AI-002`.

### Excluded

- Enviar API keys al navegador o persistirlas fuera del almacén cifrado.
- Mostrar proveedores sin credencial, consultar sus APIs o suponer modelos por nombre.
- Elegir silenciosamente un proveedor cuando no existe una credencial real.
- Garantizar acceso posterior a un modelo sujeto a cuota, región o política del proveedor.

## Dependencies and Decisions

- Dependencies: `AI-001`, `AI-002`, `AI-003`; ejecutar después de `AI-012` para reutilizar los
  clientes oficiales de listado.
- Decisions closed: descubrimiento y descifrado ocurren solo en backend; el frontend recibe nombres
  e identificadores normalizados, nunca secretos; sin credencial no hay opción ni consulta.
- Open questions: TTL de caché breve y criterio para modelos compatibles cuando el proveedor no
  publique capacidades suficientes en su listado.

## Acceptance Criteria

- [x] Sin API key de OpenAI, OpenAI no aparece y no se hace ninguna solicitud a OpenAI.
- [x] Sin API key de Gemini, Gemini no aparece y no se hace ninguna solicitud a Gemini.
- [x] Con credencial, el selector usa los modelos devueltos para esa API key y no listas precargadas.
- [x] Sin credenciales, existe un estado vacío accionable hacia configuración BYOK y no se permite
  previsualizar ni ejecutar IA real.
- [x] Un fallo de listado es seguro y reintentable, sin key ni payload sensible.
- [x] Guardar o eliminar una credencial invalida el catálogo visible.
- [x] Backend revalida credencial, proveedor y modelo al previsualizar/ejecutar; la UI no es frontera de seguridad.
- [x] El endpoint queda aislado por usuario/despacho, documentado en OpenAPI y con pruebas negativas.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                  | Change required |
| ------- | ------------------------------------------------------------ | --------------- |
| Runtime | credenciales/ejecución IA, catálogo API y selector Matter AI | yes             |
| Tests   | backend unit/route/security; frontend estados/a11y; e2e BYOK | yes             |
| Docs    | endpoints, autorización, consumidores, OpenAPI y UX BYOK     | yes             |

## Work Plan

### Implementation

- [x] Definir el puerto neutral de listado y el contrato público mínimo.
- [x] Implementar listado para OpenAI/Gemini usando la credencial descifrada solo en backend.
- [x] Añadir endpoint protegido, errores, límites, timeout y caché segura si se justifica.
- [x] Consumir el catálogo y retirar `MODEL_OPTIONS`/`DEFAULT_MODELS` para proveedores reales.
- [x] Resolver carga, ausencia de credenciales/modelos, error y reintento.
- [x] Invalidar al guardar/eliminar credenciales e integrar el mock explícito con `UX-AI-002`.

### Tests and Documentation

- [x] Probar que proveedores sin key no se consultan ni aparecen.
- [x] Probar aislamiento y ausencia de secretos o payloads sensibles en errores/logs.
- [x] Probar selector dinámico, estados, invalidación y accesibilidad.
- [x] Sincronizar OpenAPI y documentación canónica requerida por `AGENTS.md`.

### Validation

- [x] `.\.venv\Scripts\python.exe -m pytest backend/tests`
- [x] `npm --prefix frontend run openapi:sync`
- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run test:e2e:ci`
- [x] `npm --prefix frontend run build`
- [x] `.\.venv\Scripts\python.exe -m pre_commit run --all-files`

## Progress Log

| Date       | State         | Completed                                                                                                           | Pending / next safe action                      |
| ---------- | ------------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| 2026-08-01 | Plan prepared | Reglas de visibilidad, no-consulta y catálogo definidas.                                                            | Diseñar puerto y endpoint después de AI-012.    |
| 2026-08-01 | Hecho         | Catálogo SDK, endpoint protegido, revalidación, selectores dinámicos, OpenAPI, pruebas y documentación completados. | Sin trabajo pendiente; continuar con UX-AI-002. |

## Validation Results

| Date       | Command                                                                                                                    | Result | Notes                                        |
| ---------- | -------------------------------------------------------------------------------------------------------------------------- | ------ | -------------------------------------------- |
| 2026-08-01 | `.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed | 597 pruebas; cobertura total 100%.           |
| 2026-08-01 | `npm --prefix frontend run openapi:sync`                                                                                   | Passed | Artefacto sincronizado con el endpoint.      |
| 2026-08-01 | `npm --prefix frontend run check`                                                                                          | Passed | Lint, tipos, cobertura, OpenAPI y auditoría. |
| 2026-08-01 | `npm --prefix frontend run test:e2e:ci`                                                                                    | Passed | 14 escenarios Chromium.                      |
| 2026-08-01 | `npm --prefix frontend run build`                                                                                          | Passed | Build y presupuestos de rendimiento.         |
| 2026-08-01 | `.\.venv\Scripts\python.exe -m pre_commit run --all-files`                                                                 | Passed | Todos los hooks.                             |

## Pause / Handoff Record

- Current state: implementación y gates completos.
- Changed files and contracts: catálogo BYOK backend, autorización, OpenAPI, consumidores compartidos,
  selectores de asuntos/borradores, invalidación, pruebas y documentación.
- Pending work: ninguno para AI-013.
- Blockers or approvals: ninguno; no requiere aprobación humana adicional.
- Residual risks: proveedores pueden variar nombres/capacidades; el filtro conservador puede omitir
  modelos nuevos hasta adaptar la regla.
- Next safe action: continuar con `UX-AI-002`.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- README raíz revisado sin cambios: no cambió la instalación ni la identidad del producto.
- Foundation status backend/frontend sin cambios: no cambió una regla o gate fundacional.
- Arquitectura y docs AI governance revisadas sin cambios adicionales: se extendió una integración
  existente siguiendo sus límites documentados.

## Completion Summary

- Delivered: descubrimiento BYOK dinámico con SDK oficiales, aislamiento, revalidación de modelos y
  selectores sin opciones reales precargadas.
- Validation: backend 597 pruebas/100% coverage; frontend check, OpenAPI, build, 14 e2e y pre-commit verdes.
- Skipped validation: ninguna requerida.
- Human approvals: no aplican.
- Residual risk: variación futura del catálogo y metadatos de capacidades entre proveedores.
