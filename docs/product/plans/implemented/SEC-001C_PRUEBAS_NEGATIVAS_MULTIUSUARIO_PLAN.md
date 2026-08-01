# SEC-001C - Plan de pruebas negativas multiusuario

## Tracking Status

- ID: `SEC-001C`
- Type: `Backend`
- Priority: `P0-IA`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-08-01`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Demostrar que ningún usuario puede descubrir, leer, modificar, regenerar, convertir o reutilizar
recursos pertenecientes a otro despacho, con énfasis en las superficies IA incorporadas después de
`SEC-001A` y `SEC-001B`.

## Starting Point

`SEC-001A` validó los recursos legales existentes y `SEC-001B` validó el contexto de IA. Desde
entonces existen resultados persistidos, revisiones, regeneraciones, acciones derivadas,
sugerencias de checklist y borradores. Este gate consolida evidencia negativa reproducible sobre
la superficie actual completa.

## Roles y datos de prueba

Crear datos sintéticos, sin información real:

| Actor        | Despacho               | Recursos requeridos                                                                         |
| ------------ | ---------------------- | ------------------------------------------------------------------------------------------- |
| `owner_a`    | `firm_a`               | cliente, asunto, documento, resultado IA aceptado y pendiente, job, tarea, nota y checklist |
| `owner_b`    | `firm_b`               | conjunto equivalente y credencial BYOK propia                                               |
| `admin_tech` | administración técnica | solo para verificar que el rol no obtiene acceso tenant implícito                           |

Cada `owner` debe crearse mediante el flujo público soportado, que crea un despacho independiente.
No se crearán usuarios adicionales modificando directamente `firm_id` ni usando fixtures que
representen una membresía no disponible en el producto.

### Fuera de alcance

- Acceso permitido entre dos usuarios del mismo despacho.
- Invitación, incorporación, roles o administración de miembros del despacho.
- Pruebas de una capacidad disponible solo mediante manipulación directa del modelo backend.

Estas pruebas deberán agregarse cuando exista un flujo full-stack soportado para membresías del
mismo despacho, junto con sus permisos y contratos de producto.

Registrar IDs de ambos despachos en una hoja de evidencia. Nunca copiar credenciales, tokens ni
contenido sensible al reporte.

## Matriz obligatoria

Para cada recurso, ejecutar lectura/listado, creación vinculada, modificación y eliminación cuando
la API lo permita. Sustituir en la sesión de `owner_b` los IDs creados por `owner_a` y repetir en
sentido inverso.

| Superficie         | Casos negativos mínimos                                  | Resultado esperado                                  |
| ------------------ | -------------------------------------------------------- | --------------------------------------------------- |
| Clientes           | detalle, edición y búsqueda por ID ajeno                 | `404` opaco o rechazo documentado; sin mutación     |
| Asuntos            | detalle, edición y asociación con cliente ajeno          | mismo contrato que recurso inexistente              |
| Recursos de asunto | notas, tareas, checklist, pagos, cálculos y documentos   | sin lectura, escritura, descarga ni borrado cruzado |
| Documentos         | metadata, descarga y eliminación                         | no revelar nombre, tamaño, texto extraído ni objeto |
| Credenciales BYOK  | estado, reemplazo y eliminación                          | secreto y existencia aislados por usuario/despacho  |
| Preview IA         | `matter_id` ajeno y payload manipulado                   | no crear job ni invocar proveedor                   |
| Token de preview   | reutilización entre usuarios, despachos, asunto o inputs | `409`/rechazo seguro; cero invocaciones             |
| Resultados IA      | listado, detalle implícito, revisión y aceptación        | resultado ajeno indistinguible de inexistente       |
| Regeneración       | resultado origen ajeno o asunto mixto                    | rechazo antes de proveedor/job                      |
| Acciones derivadas | convertir resultado ajeno en nota, tarea o checklist     | rechazo y ausencia de efectos parciales             |
| Procedencia        | fuentes, versiones y estado desactualizado               | ningún dato ajeno en respuesta o logs               |
| Checklist IA       | convertir sugerencias ajenas                             | no crear elementos ni revelar sugerencias           |
| Borradores         | preview/token generado bajo otro despacho                | token inválido y ninguna llamada al proveedor       |

## Casos de enumeración y efectos laterales

- Comparar status, payload y estructura de error entre ID inexistente e ID de otro despacho.
- Probar IDs secuenciales, negativos, malformados y de tipo incorrecto sin usar fuerza bruta.
- Confirmar que listados, contadores del dashboard y paginación no incluyen datos ajenos.
- Confirmar que un rechazo no crea `AIJob`, audit event sensible, objeto S3 ni entidad derivada.
- Confirmar que logs y métricas no contienen prompts, API keys, contenido generado ni identificadores
  que permitan al usuario inferir datos ajenos.
- Repetir operaciones concurrentes sensibles para detectar validaciones separadas de la escritura.

## Acceptance Criteria

- [x] La matriz cubre todos los recursos tenant-owned y cada operación pública disponible.
- [x] Los accesos cruzados devuelven el mismo contrato seguro que un recurso inexistente, salvo
  excepción documentada y aprobada.
- [x] Ningún rechazo produce llamadas al proveedor, jobs, archivos o mutaciones parciales.
- [x] Tokens de preview no son reutilizables entre usuario, despacho, asunto, función o payload.
- [x] Las pruebas se automatizan en la frontera más cercana al riesgo y existe al menos un recorrido
  HTTP integrado por superficie crítica.
- [x] No quedan hallazgos P0/P1 abiertos; cualquier excepción tiene responsable y decisión explícita.
- [x] Documentación, matriz de autorización y backlog quedan sincronizados.

## Evidencia que debe entregar QA

- Matriz con ID de caso, actor, recurso, operación, resultado esperado, resultado real y evidencia.
- Nombre de prueba automatizada o captura sanitizada para cada fila.
- Registro de conteos antes/después para demostrar ausencia de efectos laterales.
- Evidencia del mock/spy que confirme cero llamadas al proveedor en rechazos.
- Reporte de defectos con severidad, pasos mínimos, IDs sintéticos y contrato afectado.
- Acta final `PASS`/`FAIL`, fecha, commit evaluado y responsable de QA.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/features/ai_assistance backend/tests/features/document_templates -q
.\.venv\Scripts\python.exe -m pytest backend/tests -q
.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100
npm --prefix frontend run test:e2e:ci
pre-commit run --all-files
```

## Entry, Stop and Exit Rules

- Entry: build identificable, dos despachos aislados, proveedor mock y almacenamiento de prueba.
- Stop: fuga confirmada, acceso cruzado exitoso, secreto expuesto o proveedor invocado tras rechazo.
- Exit: matriz completa, suites verdes, cero defectos P0/P1 y evidencia revisada por seguridad.

## Validation Results

| Date       | Validation                         | Result | Notes                                                     |
| ---------- | ---------------------------------- | ------ | --------------------------------------------------------- |
| 2026-08-01 | Ejecución del plan completo por QA | Pass   | El responsable del producto confirmó que `SEC-001C` pasó. |

## Pause / Handoff Record

- Current state: matriz ejecutada y aprobada por QA.
- Pending work: ninguno dentro de `SEC-001C`.
- Blockers or approvals: ninguno; confirmación humana registrada el 2026-08-01.
- Residual risks: las pruebas no sustituyen revisión de infraestructura productiva ni pentest externo.
- Next safe action: completar `SEC-002` antes de liberar las funciones IA.

## Completion Summary

- Delivered: evidencia negativa multiusuario sobre la superficie tenant e IA vigente.
- Validation: el responsable del producto confirmó que el plan completo pasó.
- Evidence boundary: no se recibieron comandos, conteos ni anexos para transcribir; no se inventaron.
- Human approvals: confirmación de QA recibida el 2026-08-01.
- Residual risk: el gate de privacidad y aprobación jurídica `SEC-002` sigue pendiente.
