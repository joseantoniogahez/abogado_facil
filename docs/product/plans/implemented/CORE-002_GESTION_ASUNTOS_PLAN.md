# CORE-002 - Plan de gestión de asuntos y expedientes

## Estado del tracking

- ID: `CORE-002`
- Tipo: Full-stack
- Prioridad: P1
- Estado del plan: Completo
- Estado de implementación: Hecho
- Última actualización: 2026-07-12
- Backlog: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objetivo

Permitir que un usuario autenticado cree un asunto asociado a uno de los clientes de su despacho,
consulte su detalle y actualice su estado y próxima acción sin exponer datos de otros despachos.

## Punto de partida

CORE-001 ya proporciona clientes aislados por `firm_id`, rutas protegidas y un estado vacío de
asuntos en el detalle. El dashboard reserva métricas y una acción rápida para asuntos, pero no
existe persistencia, API ni interfaz funcional para expedientes.

## Alcance

### Incluido

- Persistencia con despacho, cliente, título, tipo, contraparte, descripción, estado, próxima
  acción y fecha opcional.
- Alta, listado, detalle y edición parcial dentro del despacho autenticado.
- Validación de que el cliente asociado pertenece al mismo despacho.
- Listado general y listado contextual en el detalle del cliente.
- Rutas protegidas, estados accesibles, textos centralizados y dashboard con conteo real.
- Pruebas, migración, OpenAPI y documentación operativa sincronizados.

### Excluido

- Borrado, archivado, notas, documentos, tareas, pagos, checklists e IA.
- Colaboración multi-despacho y permisos configurables específicos de asuntos.
- Catálogos jurídicos exhaustivos; `matter_type` será texto acotado para el MVP.

## Dependencias y decisiones

- Dependencia: CORE-001 completado.
- La frontera de propiedad es `firm_id`; ningún contrato acepta un despacho elegido por cliente.
- Los accesos por ID combinan `matter_id` y `firm_id`; ajeno e inexistente producen el mismo 404.
- Estados permitidos: `active`, `pending`, `closed`; el estado inicial es `active`.
- La fecha de próxima acción es opcional y se representa como fecha calendario.
- No hay preguntas abiertas que impidan la implementación.

## Criterios de aceptación

- [x] Crear un asunto asociado únicamente a un cliente del despacho actual.
- [x] Listar asuntos del despacho y filtrar por cliente sin fuga entre despachos.
- [x] Ver detalle con cliente, estado, contraparte y próxima acción.
- [x] Editar estado y los demás campos del asunto mediante `PATCH`.
- [x] Un asunto o cliente ajeno se comporta como inexistente.
- [x] El detalle de cliente permite listar y crear sus asuntos contextualmente.
- [x] El dashboard muestra asuntos activos reales y habilita “Crear asunto”.
- [x] Rutas, API, OpenAPI, textos, documentación y pruebas están sincronizados.
- [x] Alta y edición seleccionan al cliente por nombre mediante un control con búsqueda.
- [x] La edición solicita confirmación antes de reasignar el asunto a otro cliente.
- [x] Los gates backend, frontend, e2e, build y pre-commit pasan.
- [x] Aprobación humana del presupuesto registrada.

## Archivos y contratos afectados

| Superficie       | Archivos o contratos esperados                                | Cambio |
| ---------------- | ------------------------------------------------------------- | ------ |
| Runtime backend  | `app/features/matters`, DI, routers, dashboard                | Sí     |
| Persistencia     | modelo y migración `matters`                                  | Sí     |
| Runtime frontend | `src/features/matters`, clientes, rutas, dashboard, textos    | Sí     |
| Pruebas          | suites backend/frontend/e2e/accesibilidad                     | Sí     |
| Docs             | matrices de endpoints, acceso, rutas, consumidores y tracking | Sí     |

## Plan de trabajo

### Implementación

- [x] Previsualizar y ejecutar scaffold full-stack.
- [x] Implementar backend vertical y migración.
- [x] Integrar conteo de asuntos activos en dashboard.
- [x] Implementar contratos, consumidor, listado, alta, detalle y edición frontend.
- [x] Integrar navegación contextual de asuntos en detalle de cliente.

### Pruebas y documentación

- [x] Añadir pruebas backend de validación, UoW, aislamiento, asociación y endpoints.
- [x] Añadir pruebas frontend de contratos y conservar gates de interacción.
- [x] Sincronizar OpenAPI y documentación canónica afectada.
- [x] Revisar READMEs y foundation status; no cambian reglas fundacionales.

### Validación

- [x] `python -m pytest backend/tests`
- [x] Backend coverage 100%.
- [x] `npm --prefix frontend run openapi:sync`
- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run test:e2e:ci`
- [x] `npm --prefix frontend run build`.
- [x] `pre-commit run --all-files`

## Registro de avance

| Fecha      | Estado      | Completado                                                                                 | Pendiente / siguiente acción segura                                              |
| ---------- | ----------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| 2026-07-12 | En progreso | Alcance, decisiones, criterios y gates definidos                                           | Ejecutar scaffold y materializar slice backend                                   |
| 2026-07-12 | En progreso | Slice full-stack, migración, aislamiento, dashboard, OpenAPI, docs y pruebas implementados | Obtener aprobación del ajuste mínimo de presupuesto; actualizarlo y cerrar gates |
| 2026-07-12 | Hecho       | Presupuesto aprobado; build, cobertura 100% y pre-commit pasan                             | Ninguna acción obligatoria pendiente                                             |
| 2026-07-12 | Hecho       | Selector buscable de cliente y confirmación de reasignación incorporados                   | Ninguna acción obligatoria pendiente                                             |
| 2026-07-12 | Bloqueado   | Implementación, pruebas, contratos y check frontend completos                              | Aprobar presupuesto mínimo de JS/CSS y repetir build                             |
| 2026-07-12 | Hecho       | Presupuesto aprobado; build y pre-commit pasan                                             | Ninguna acción obligatoria pendiente                                             |

## Resultados de validación

| Fecha      | Comando                                  | Resultado                 | Notas                                                                                            |
| ---------- | ---------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------ |
| 2026-07-12 | `python -m pytest backend/tests`         | Pasó                      | 328 pruebas                                                                                      |
| 2026-07-12 | backend coverage gate                    | Falló y corregido         | 99.97%; faltó una rama de principal sin despacho, prueba añadida; rerun pendiente                |
| 2026-07-12 | `npm --prefix frontend run openapi:sync` | Pasó                      | Artefacto sincronizado                                                                           |
| 2026-07-12 | `npm --prefix frontend run check`        | Pasó                      | 198 pruebas y thresholds globales                                                                |
| 2026-07-12 | `npm --prefix frontend run test:e2e:ci`  | Pasó                      | 12/12 Chromium                                                                                   |
| 2026-07-12 | `npm --prefix frontend run build`        | Bloqueado por presupuesto | Compila; JS total 410,459 B y gzip 121,236 B superan 403,000/119,000; requiere aprobación humana |
| 2026-07-12 | Aprobación humana de presupuesto         | Aprobado                  | Límites JS mínimos 411,000 B/122,000 B aprobados por el propietario                              |
| 2026-07-12 | `pre-commit run --all-files`             | Pasó                      | Hooks ejecutados fuera del sandbox por caché de usuario                                          |
| 2026-07-12 | backend coverage gate final              | Pasó                      | 328 pruebas; 100.00%                                                                             |
| 2026-07-12 | `npm --prefix frontend run build` final  | Pasó                      | JS 410,459/411,000 B; gzip 121,236/122,000 B; CSS pasa                                           |
| 2026-07-12 | `pre-commit run --all-files` final       | Pasó                      | Todos los hooks pasan                                                                            |
| 2026-07-12 | Revisión de artefactos scaffold          | Pasó                      | Tres checklists cerrados; placeholder de schema eliminado; alcance e2e documentado               |
| 2026-07-12 | Pruebas enfocadas de asuntos             | Pasó                      | 4 pruebas; selección por nombre, filtro y confirmación de reasignación                           |
| 2026-07-12 | `npm --prefix frontend run check`        | Pasó                      | 205 pruebas; cobertura global de ramas por encima de 85%; OpenAPI y dependencias pasan           |
| 2026-07-12 | `npm --prefix frontend run build`        | Bloqueado por presupuesto | Compila; JS 412,622/411,000 B y CSS 20,855/20,500 B; gzip JS y CSS pasan                         |
| 2026-07-12 | Aprobación humana de presupuesto         | Aprobado                  | Límites mínimos aprobados: JS raw 413,000 B y CSS raw 21,000 B                                   |
| 2026-07-12 | `npm --prefix frontend run build` final  | Pasó                      | JS 412,622/413,000 B; CSS 20,855/21,000 B; ambos presupuestos gzip pasan                         |

## Pausa / handoff

- Estado actual: cambio de selector completo; implementación, documentación y gates verdes.
- Cambios: slice `matters`, migración, dashboard, rutas/UI, OpenAPI, docs y pruebas.
- Pendiente: ninguna acción obligatoria.
- Bloqueos o aprobaciones: ajuste mínimo de presupuesto aprobado por el propietario.
- Riesgo residual: el smoke e2e conserva los recorridos base; no incluye todavía un recorrido
  Playwright dedicado de asuntos.
- Siguiente acción segura: iniciar el siguiente ítem priorizado.
