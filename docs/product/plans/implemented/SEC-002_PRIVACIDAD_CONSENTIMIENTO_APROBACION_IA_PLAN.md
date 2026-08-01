# SEC-002 - Plan de pruebas de privacidad, consentimiento y aprobación IA

## Tracking Status

- ID: `SEC-002`
- Type: `Legal`
- Priority: `P0-IA`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-08-01`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Verificar que una llamada real de IA solo pueda ocurrir después de presentar información vigente,
obtener consentimiento explícito y registrar evidencia auditable, y que los textos hayan recibido
aprobación jurídica para la jurisdicción de lanzamiento.

## Responsibility Boundary

QA valida comportamiento, accesibilidad, persistencia, versionado, revocación y evidencia. Un
profesional jurídico designado aprueba el contenido y su adecuación jurisdiccional. QA no debe
declarar conformidad legal por cuenta propia.

## Prerequisites

- Jurisdicción y fecha objetivo de lanzamiento identificadas.
- Responsable jurídico, responsable de producto y responsable de privacidad identificados.
- Textos candidatos versionados: aviso de privacidad, términos y consentimiento IA BYOK.
- Matriz de proveedores soportados y enlaces vigentes a sus políticas.
- Entorno QA con proveedor mock y opción controlada para una prueba real sin datos personales.

## Contenido que debe revisar Legal

- Responsable del tratamiento, contacto y finalidades.
- Categorías de datos que el usuario puede enviar y minimización esperada.
- Identidad o categoría del proveedor externo y transferencia de datos.
- Modelo BYOK, costos, responsabilidades del usuario y ausencia de garantía de exactitud.
- Retención, eliminación, derechos aplicables y canal para ejercerlos.
- Revisión humana obligatoria y prohibición de uso automático como asesoría definitiva.
- Fecha efectiva, versión, idioma y regla de reconsentimiento ante cambios materiales.

## Matriz funcional obligatoria

| Caso                  | Procedimiento                                            | Resultado esperado                                                                 |
| --------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Usuario nuevo         | configurar BYOK e intentar preview/ejecución             | información visible y ejecución bloqueada hasta aceptar                            |
| Rechazo               | cerrar o rechazar consentimiento                         | ninguna llamada real; usuario puede seguir usando funciones sin IA                 |
| Aceptación            | aceptar mediante control no preseleccionado              | registrar usuario, despacho, versión, fecha y finalidad                            |
| Persistencia          | cerrar sesión y volver a entrar                          | no pedir de nuevo si la misma versión sigue vigente                                |
| Cambio material       | activar una versión nueva                                | bloquear siguiente llamada real hasta nueva aceptación                             |
| Cambio no material    | corrección marcada como no material                      | conservar aceptación conforme a decisión registrada                                |
| Revocación            | retirar consentimiento                                   | bloquear llamadas posteriores sin borrar evidencia histórica requerida             |
| Proveedor distinto    | cambiar OpenAI/Gemini                                    | mostrar destino y exigir nueva aceptación si cambia la finalidad o texto aplicable |
| Token obsoleto        | aceptar y luego ejecutar con estado/versiones anteriores | backend rechaza; frontend vuelve a presentar información vigente                   |
| API directa           | omitir UI e invocar endpoint de ejecución                | backend bloquea antes de proveedor/job                                             |
| Multiusuario          | aceptar como `owner_a` y ejecutar como otro usuario      | la aceptación solo aplica según el alcance jurídico documentado                    |
| Error de persistencia | simular fallo al guardar aceptación                      | no mostrar aceptación exitosa ni ejecutar IA                                       |

## Superficies que debe recorrer QA

- Configuración y eliminación de credenciales BYOK.
- Todas las funciones del detalle del asunto: `AI-101` a `AI-106` y `AI-201` a `AI-203`.
- Preview, ejecución, regeneración, revisión y conversión de resultados.
- Generación de borradores `DOC-002` y copia/exportación posterior.
- Acceso público al aviso de privacidad y términos sin iniciar sesión.

## Seguridad, privacidad y auditoría

- La aceptación debe ser explícita, granular cuando corresponda y nunca preseleccionada.
- El backend, no solo la interfaz, debe imponer el gate antes de cada llamada real.
- El registro debe ser inmutable o auditable y no almacenar API keys, prompts ni contenido legal.
- Logs y eventos pueden registrar IDs, versión y resultado, pero no datos sensibles.
- Probar acceso cruzado al registro de consentimiento como parte de `SEC-001C`.
- Probar concurrencia entre revocación/cambio de versión y ejecución.
- El modo mock debe estar identificado y no debe simular que hubo transferencia real.

## Accesibilidad y experiencia

- Controles alcanzables con teclado, foco visible y orden lógico.
- Etiquetas y mensajes comprensibles con lector de pantalla.
- Zoom al 200 %, viewport móvil y escritorio sin ocultar texto ni acciones.
- Enlaces a textos completos disponibles antes de aceptar.
- Rechazar o cerrar debe ser tan claro como aceptar; sin patrones manipulativos.
- Errores deben explicar cómo continuar sin marcar consentimiento ficticio.

## Acceptance Criteria

- [x] Ninguna llamada real puede comenzar sin consentimiento vigente verificado en backend.
- [x] Aceptación, rechazo, revocación y reconsentimiento tienen pruebas automatizadas.
- [x] La evidencia registra versión, actor, alcance, fecha y resultado sin datos sensibles.
- [x] Todos los consumidores IA y `DOC-002` cumplen el mismo contrato.
- [x] Accesibilidad, responsive y escenarios de error pasan.
- [x] Aviso, términos y consentimiento tienen aprobación jurídica firmada y trazable.
- [x] No quedan defectos P0/P1 ni observaciones jurídicas abiertas para release.
- [x] Documentación, OpenAPI, inventarios y backlog están sincronizados.

## Evidencia que debe entregar QA y Legal

- Matriz con caso, versión de texto, actor, proveedor, resultado esperado/real y evidencia.
- Pruebas automatizadas de backend, frontend y e2e vinculadas a cada criterio.
- Capturas sanitizadas de los estados principales y reporte de accesibilidad.
- Evidencia de cero llamadas al proveedor cuando falta o se revoca consentimiento.
- Export o consulta sanitizada del registro de consentimiento.
- Acta jurídica con jurisdicción, versión aprobada, fecha, responsable y resultado.
- Acta final de QA con commit/build probado y decisión `PASS`/`FAIL`.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -q
.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100
npm --prefix frontend run openapi:check
npm --prefix frontend run check
npm --prefix frontend run build
npm --prefix frontend run test:e2e:ci
pre-commit run --all-files
```

## Entry, Stop and Exit Rules

- Entry: textos candidatos versionados, responsable legal asignado y proveedor mock disponible.
- Stop: llamada real sin consentimiento vigente, aceptación ficticia, fuga de datos o texto no
  aprobado presentado como definitivo.
- Exit: suites verdes, matriz completa, cero defectos P0/P1 y acta jurídica aprobatoria registrada.

## Closed Decision

El responsable del producto confirmó que el plan completo pasó, incluida la decisión de
jurisdicción y la aprobación jurídica. Los detalles del acta no fueron proporcionados para
transcribirlos en el repositorio.

## Validation Results

| Date       | Validation                        | Result | Notes                                                    |
| ---------- | --------------------------------- | ------ | -------------------------------------------------------- |
| 2026-08-01 | Ejecución completa por QA y Legal | Pass   | El responsable del producto confirmó que `SEC-002` pasó. |

## Pause / Handoff Record

- Current state: mecanismo, pruebas y aprobación jurídica confirmados como aprobados.
- Pending work: ninguno dentro de `SEC-002`.
- Blockers or approvals: ninguno; confirmación humana registrada el 2026-08-01.
- Residual risks: el plan no constituye asesoría legal ni sustituye evaluación regulatoria.
- Next safe action: ejecutar la revalidación integral del release IA.

## Completion Summary

- Delivered: gate de privacidad, consentimiento versionado y aprobación jurídica para IA BYOK.
- Validation: el responsable del producto confirmó que el plan completo pasó.
- Evidence boundary: no se recibieron comandos, acta ni anexos para transcribir; no se inventaron.
- Human approvals: confirmación conjunta de QA y Legal recibida el 2026-08-01.
- Residual risk: falta ejecutar y registrar la revalidación integral final del release IA.
