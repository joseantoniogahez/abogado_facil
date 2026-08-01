# AI-013 - Descubrimiento de modelos por credencial BYOK

## Tracking Status

- ID: `AI-013`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Ready`
- Implementation status: `Listo`
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

- [ ] Sin API key de OpenAI, OpenAI no aparece y no se hace ninguna solicitud a OpenAI.
- [ ] Sin API key de Gemini, Gemini no aparece y no se hace ninguna solicitud a Gemini.
- [ ] Con credencial, el selector usa los modelos devueltos para esa API key y no listas precargadas.
- [ ] Sin credenciales, existe un estado vacío accionable hacia configuración BYOK y no se permite
  previsualizar ni ejecutar IA real.
- [ ] Un fallo de listado es seguro y reintentable, sin key ni payload sensible.
- [ ] Guardar o eliminar una credencial invalida el catálogo visible.
- [ ] Backend revalida credencial, proveedor y modelo al previsualizar/ejecutar; la UI no es frontera de seguridad.
- [ ] El endpoint queda aislado por usuario/despacho, documentado en OpenAPI y con pruebas negativas.
- [ ] Required documentation is synchronized with delivered behavior.
- [ ] Required validation gates pass and are recorded below.
- [ ] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                  | Change required |
| ------- | ------------------------------------------------------------ | --------------- |
| Runtime | credenciales/ejecución IA, catálogo API y selector Matter AI | yes             |
| Tests   | backend unit/route/security; frontend estados/a11y; e2e BYOK | yes             |
| Docs    | endpoints, autorización, consumidores, OpenAPI y UX BYOK     | yes             |

## Work Plan

### Implementation

- [ ] Definir el puerto neutral de listado y el contrato público mínimo.
- [ ] Implementar listado para OpenAI/Gemini usando la credencial descifrada solo en backend.
- [ ] Añadir endpoint protegido, errores, límites, timeout y caché segura si se justifica.
- [ ] Consumir el catálogo y retirar `MODEL_OPTIONS`/`DEFAULT_MODELS` para proveedores reales.
- [ ] Resolver carga, ausencia de credenciales/modelos, error y reintento.
- [ ] Invalidar al guardar/eliminar credenciales e integrar el mock explícito con `UX-AI-002`.

### Tests and Documentation

- [ ] Probar que proveedores sin key no se consultan ni aparecen.
- [ ] Probar aislamiento y ausencia de secretos o payloads sensibles en errores/logs.
- [ ] Probar selector dinámico, estados, invalidación y accesibilidad.
- [ ] Sincronizar OpenAPI y documentación canónica requerida por `AGENTS.md`.

### Validation

- [ ] `.\.venv\Scripts\python.exe -m pytest backend/tests`
- [ ] `npm --prefix frontend run openapi:sync`
- [ ] `npm --prefix frontend run check`
- [ ] `npm --prefix frontend run test:e2e:ci`
- [ ] `npm --prefix frontend run build`
- [ ] `.\.venv\Scripts\python.exe -m pre_commit run --all-files`

## Progress Log

| Date       | State         | Completed                                                | Pending / next safe action                   |
| ---------- | ------------- | -------------------------------------------------------- | -------------------------------------------- |
| 2026-08-01 | Plan prepared | Reglas de visibilidad, no-consulta y catálogo definidas. | Diseñar puerto y endpoint después de AI-012. |

## Validation Results

| Date | Command | Result | Notes |
| ---- | ------- | ------ | ----- |
|      |         |        |       |

## Pause / Handoff Record

- Current state: UI usa opciones precargadas; descubrimiento no implementado.
- Changed files and contracts: backlog y plan únicamente.
- Pending work: backend, OpenAPI, frontend, pruebas, e2e y documentación.
- Blockers or approvals: depende de completar o resolver técnicamente `AI-012`.
- Residual risks: los listados pueden incluir modelos incompatibles o variar por proveedor.
- Next safe action: tras AI-012, definir respuesta normalizada y compatibilidad por función.

## Completion Documentation Review

- [ ] Root and service READMEs reviewed.
- [ ] Backend operation and architecture docs reviewed.
- [ ] Frontend operation docs and inventories reviewed.
- [ ] Foundation status files reviewed and changed only if a foundation contract moved.
- [ ] AI governance docs, templates, and checklists reviewed.
- [ ] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Pendiente de implementación.

## Completion Summary

- Delivered: pendiente.
- Validation: pendiente.
- Skipped validation: planificación documental; no se modificó runtime.
- Human approvals: no aplican por ahora.
- Residual risk: variación del catálogo y metadatos entre proveedores.
