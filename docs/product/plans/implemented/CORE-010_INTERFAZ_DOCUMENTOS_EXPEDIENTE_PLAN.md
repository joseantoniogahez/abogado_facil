# CORE-010 - Interfaz de documentos de expediente

## Estado del tracking

- ID: `CORE-010`
- Tipo: Frontend
- Prioridad: P1
- Estado del plan: Hecho
- Estado de implementación: Hecho
- Última actualización: 2026-07-14
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

- [x] El usuario puede seleccionar tipo y subir un archivo permitido desde un asunto propio.
- [x] La UI explica formatos/límites y muestra errores backend seguros y recuperables.
- [x] El listado presenta metadata y permite descargar el archivo con nombre correcto.
- [x] El borrado exige confirmación y actualiza la lista sin recargar datos no relacionados.
- [x] Los estados son responsive, navegables por teclado y pasan axe.
- [x] Consumidor, OpenAPI, matrices, i18n, pruebas y e2e permanecen sincronizados.
- [x] `check`, e2e y build pasan.

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

- [x] Cambiar CORE-010 a `En progreso` al iniciar.
- [x] Ejecutar scaffold frontend en `--dry-run` y ajustar destino bajo `features/matters`.
- [x] Implementar contratos, query keys, multipart, descarga binaria y mutaciones.
- [x] Integrar formulario, listado, descarga, confirmación y estados accesibles.
- [x] Añadir textos i18n y liberar recursos temporales de descarga.

### Tests y documentación

- [x] Cubrir vacío, carga, éxito, límite, error/retry, descarga y eliminación.
- [x] Actualizar `api_consumer_matrix.md`, `mutation_policy.md`, `route_inventory.md`,
  `e2e_smoke_suite.md` y `accessibility_gate.md` cuando corresponda.
- [x] Revisar runtime config, seguridad del navegador, observabilidad y performance.

### Validación

- [x] `npm --prefix frontend run openapi:check`
- [x] `npm --prefix frontend run check` (lint, typecheck y coverage pasan; build se registra aparte)
- [x] `npm --prefix frontend run test:e2e:ci`
- [x] `npm --prefix frontend run build`
- [x] `pre-commit run --all-files`
- [x] Recorrido e2e: login -> asunto -> subir -> listar -> descargar -> eliminar.

## Riesgos y mitigaciones

| Riesgo                       | Mitigación                                            |
| ---------------------------- | ----------------------------------------------------- |
| Fuga de memoria al descargar | Revocar object URLs en éxito/error/unmount            |
| Duplicar límites backend     | Consumir contrato estable y tratar API como autoridad |
| UI inaccesible de archivos   | Labels, foco, teclado, estados anunciados y axe       |
| Import cross-feature         | Mantener implementación dentro de `features/matters`  |

## Registro de avance

| Fecha      | Estado      | Completado                                                 | Pendiente / siguiente acción segura  |
| ---------- | ----------- | ---------------------------------------------------------- | ------------------------------------ |
| 2026-07-13 | Plan listo  | UI separada del contrato backend                           | Completar CORE-004 y revisar OpenAPI |
| 2026-07-14 | En progreso | CORE-004 y OpenAPI confirmados; scaffold dry-run intentado | Implementar consumidor y UI          |
| 2026-07-14 | En progreso | UI, pruebas, e2e y docs terminados                         | Aprobar ajuste mínimo de performance |
| 2026-07-14 | Hecho       | Presupuesto autorizado, build y tracking cerrados          | Ninguno                              |

## Resultados de validación

| Fecha      | Comando                                                                                             | Resultado  | Notas                                                                                                      |
| ---------- | --------------------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------- |
| 2026-07-13 | Revisión de partición                                                                               | Pasó       | Planificación; frontend no implementado                                                                    |
| 2026-07-14 | `python scripts/scaffold_feature.py frontend matter-documents --route /matters/:matterId --dry-run` | No ejecutó | El launcher global de Python no pudo iniciar; el destino se mantendrá manualmente bajo `features/matters`. |
| 2026-07-14 | `npm --prefix frontend run test:coverage -- --silent --reporter=dot`                                | Pasó       | 49 archivos, 218 pruebas; 94.63% statements, 85.3% branches, 96.9% functions y 95.04% lines.               |
| 2026-07-14 | `npm --prefix frontend run openapi:check`                                                           | Pasó       | Artefacto backend OpenAPI vigente.                                                                         |
| 2026-07-14 | `npm --prefix frontend run test:e2e:ci`                                                             | Pasó       | 13/13; incluye upload, lista, descarga y borrado.                                                          |
| 2026-07-14 | `npm --prefix frontend run build`                                                                   | Pasó       | 425052 B raw y 124429 B gzip; pasan los límites autorizados 836000/247000 y los límites CSS.               |
| 2026-07-14 | `.\\.venv\\Scripts\\pre-commit.exe run --all-files`                                                 | Pasó       | Hooks del repositorio ejecutados.                                                                          |

## Pausa / handoff

- Estado actual: CORE-010 completado y validado.
- Pendiente: ninguno.
- Bloqueos: ninguno.
- Riesgo residual: la capacidad adicional de bundle debe seguir revisándose por feature; el gate permanece activo.
- Siguiente acción segura: continuar con el siguiente ticket priorizado.

## Revisión documental de cierre

- [x] README frontend revisado y actualizado.
- [x] Operaciones e inventarios frontend revisados y actualizados.
- [x] Foundation status revisado y actualizado con el presupuesto aprobado.
- [x] Plan y backlog sincronizados.

Revisados sin cambios: runtime config, browser security, observabilidad y runtime error pipeline,
porque CORE-010 no cambia variables, políticas del navegador ni el esquema de diagnóstico.

## Resumen de cierre

- Entregado: interfaz de documentos integrada al detalle del asunto con carga, lista, descarga y borrado.
- Validación: check/coverage, OpenAPI, e2e, build/performance y pre-commit pasan.
- Validación omitida: ninguna obligatoria.
- Aprobaciones humanas: propietario autorizó duplicar los límites JS a 836000/247000 B.
- Riesgo residual: vigilar el crecimiento futuro del bundle aunque exista capacidad aprobada.
