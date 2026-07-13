# CORE-010 - Interfaz de documentos de expediente

## Estado del tracking

- ID: `CORE-010`
- Tipo: Frontend
- Prioridad: P1
- Estado del plan: Listo
- Estado de implementación: Identificado
- Última actualización: 2026-07-13
- Fuente: `docs/product/REQUERIMIENTOS_ABOGADO_FACIL_IA.md`, sección 6.8
- Backlog: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objetivo

Integrar en el detalle del asunto una interfaz accesible para cargar, listar, descargar y eliminar
documentos mediante el contrato OpenAPI entregado por `CORE-004`.

## Alcance

### Incluido

- Consumidor multipart y descarga binaria mediante el cliente HTTP compartido.
- Selector de archivo PDF/DOCX/TXT y tipo documental obligatorio.
- Límites y formatos visibles según el contrato backend.
- Listado con nombre, tipo, tamaño y fecha.
- Descarga autenticada conservando nombre seguro.
- Eliminación con confirmación y estados de carga, vacío, error y reintento.
- Query/mutation policy, i18n, pruebas de interacción, accesibilidad y e2e.

### Excluido

- MinIO/Compose (`OPS-004`), persistencia/API (`CORE-004`) y extracción (`CORE-005`).
- Vista previa, edición, drag-and-drop múltiple, progreso byte a byte y presigned URLs.

## Dependencias y decisiones

- Dependencias: `CORE-004` en `Hecho` y OpenAPI sincronizado; indirectamente `OPS-004`.
- La UI vivirá bajo `frontend/src/features/matters` para respetar límites cross-feature.
- No se creará una ruta nueva; se amplía `/matters/:matterId`.
- Alta y borrado invalidarán sólo la lista de documentos del asunto.
- La descarga liberará object URLs y manejará errores normalizados sin exponer internals.

## Criterios de aceptación

- [ ] El usuario puede seleccionar tipo y subir un archivo permitido desde un asunto propio.
- [ ] La UI explica formatos/límites y muestra errores backend seguros y recuperables.
- [ ] El listado presenta metadata y permite descargar el archivo con nombre correcto.
- [ ] El borrado exige confirmación y actualiza la lista sin recargar datos no relacionados.
- [ ] Los estados son responsive, navegables por teclado y pasan axe.
- [ ] Consumidor, OpenAPI, matrices, i18n, pruebas y e2e permanecen sincronizados.
- [ ] `check`, e2e y build pasan.

## Archivos y contratos afectados

| Superficie | Archivos esperados                                                | Cambio  |
| ---------- | ----------------------------------------------------------------- | ------- |
| Feature    | `frontend/src/features/matters/matter-documents` y detalle        | Sí      |
| Shared     | cliente HTTP sólo si descarga binaria requiere extensión genérica | Revisar |
| Textos     | `frontend/src/shared/i18n/ui-text.ts`                             | Sí      |
| Contratos  | OpenAPI, consumidores y mutation policy                           | Sí      |
| Pruebas    | componentes, integración, a11y y e2e                              | Sí      |

## Plan de trabajo

### Implementación

- [ ] Cambiar CORE-010 a `En progreso` al iniciar.
- [ ] Ejecutar scaffold frontend en `--dry-run` y ajustar destino bajo `features/matters`.
- [ ] Implementar contratos, query keys, multipart, descarga binaria y mutaciones.
- [ ] Integrar formulario, listado, descarga, confirmación y estados accesibles.
- [ ] Añadir textos i18n y liberar recursos temporales de descarga.

### Tests y documentación

- [ ] Cubrir vacío, carga, éxito, límite, error/retry, descarga y eliminación.
- [ ] Actualizar `api_consumer_matrix.md`, `mutation_policy.md`, `route_inventory.md`,
  `e2e_smoke_suite.md` y `accessibility_gate.md` cuando corresponda.
- [ ] Revisar runtime config, seguridad del navegador, observabilidad y performance.

### Validación

- [ ] `npm --prefix frontend run openapi:check`
- [ ] `npm --prefix frontend run check`
- [ ] `npm --prefix frontend run test:e2e:ci`
- [ ] `npm --prefix frontend run build`
- [ ] `pre-commit run --all-files`
- [ ] Recorrido e2e: login -> asunto -> subir -> listar -> descargar -> eliminar.

## Riesgos y mitigaciones

| Riesgo                       | Mitigación                                            |
| ---------------------------- | ----------------------------------------------------- |
| Fuga de memoria al descargar | Revocar object URLs en éxito/error/unmount            |
| Duplicar límites backend     | Consumir contrato estable y tratar API como autoridad |
| UI inaccesible de archivos   | Labels, foco, teclado, estados anunciados y axe       |
| Import cross-feature         | Mantener implementación dentro de `features/matters`  |

## Registro de avance

| Fecha      | Estado     | Completado                       | Pendiente / siguiente acción segura  |
| ---------- | ---------- | -------------------------------- | ------------------------------------ |
| 2026-07-13 | Plan listo | UI separada del contrato backend | Completar CORE-004 y revisar OpenAPI |

## Resultados de validación

| Fecha      | Comando               | Resultado | Notas                                   |
| ---------- | --------------------- | --------- | --------------------------------------- |
| 2026-07-13 | Revisión de partición | Pasó      | Planificación; frontend no implementado |

## Pausa / handoff

- Estado actual: plan listo; implementación identificada hasta completar CORE-004.
- Pendiente: implementación completa.
- Bloqueos: ninguno fuera de la secuencia definida.
- Riesgo residual: contrato binario/multipart aún no sincronizado.
- Siguiente acción segura: completar CORE-004 y revisar su OpenAPI generado.

## Revisión documental de cierre

- [ ] README frontend revisado.
- [ ] Operaciones e inventarios frontend revisados.
- [ ] Foundation status revisado.
- [ ] Plan y backlog sincronizados.

## Resumen de cierre

- Entregado: pendiente.
- Validación: revisión del plan.
- Validación omitida: gates frontend hasta implementación.
- Aprobaciones humanas: no aplicables al plan.
- Riesgo residual: integración con API pendiente.
