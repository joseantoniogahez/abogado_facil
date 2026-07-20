# LEGAL-002B - Auditoría de consistencia de avisos IA

## Estado del tracking

- ID: `LEGAL-002B`
- Tipo: Frontend
- Prioridad: P0-IA
- Estado del plan: Listo
- Estado de implementación: Identificado
- Última actualización: 2026-07-11
- Fuente: cierre de `LEGAL-001` y backlog de funciones `AI-101`, `AI-102` y `AI-103`

## Objetivo

Validar el patrón de revisión humana dentro de flujos reales después de implementar al menos dos y
preferentemente tres funciones de IA. Cada resultado debe conservar su identificación, aviso
contextual y relación accesible antes de copiar, guardar, exportar o utilizar el contenido.

## Condición de inicio

`LEGAL-002A` debe existir como patrón compartido antes de iniciar esta auditoría.

- Al menos dos de `AI-101`, `AI-102` y `AI-103` están implementados con resultados utilizables.
- Los flujos incluyen las acciones reales que deban validarse, sin crear pantallas ficticias para
  adelantar este ticket.

## Alcance

### Incluido

- Aplicar `AiGeneratedContentNotice` a cada resultado real disponible.
- Clasificar cada salida como borrador o sugerencia.
- Asociar aviso, resultado y acciones con semántica accesible.
- Probar persistencia al regenerar, editar y guardar.
- Probar que copiar, exportar o cualquier uso externo no oculta la condición de contenido generado
  con IA.
- Adaptar la lista de revisión al tipo de salida sin eliminar las limitaciones esenciales.

### Excluido

- Implementar las funciones de IA que sirven como dependencia.
- Aprobar jurídicamente los textos para lanzamiento; ese gate pertenece a `SEC-002`.
- Crear privacidad, términos, consentimiento BYOK o políticas de conservación.

## Criterios de aceptación

- [ ] Al menos dos funciones reales de IA usan el patrón compartido.
- [ ] Cada salida se identifica correctamente como borrador o sugerencia.
- [ ] El aviso completo permanece visible junto al resultado y antes de acciones externas.
- [ ] Regenerar, editar y guardar no eliminan la identificación ni el aviso.
- [ ] Resultado, aviso y acciones tienen una relación accesible verificable.
- [ ] Las pruebas consumidoras fallan si se omite la identificación o advertencia.
- [ ] La revisión documental de frontend y de cada ticket consumidor queda registrada.
- [ ] Los gates frontend requeridos pasan.

## Plan de trabajo

### Integración

- [ ] Inventariar las funciones IA disponibles y clasificar sus resultados.
- [ ] Integrar `AiGeneratedContentNotice` en al menos dos flujos.
- [ ] Asociar los IDs del aviso con resultados y controles relacionados.

### Pruebas y documentación

- [ ] Cubrir regeneración, edición, guardado y acciones externas disponibles.
- [ ] Ejecutar axe y pruebas de teclado sobre los estados reales.
- [ ] Actualizar documentación operativa o e2e si cambia su contrato o cobertura.
- [ ] Registrar documentos revisados pero intencionalmente sin cambios.

### Validación

- [ ] Pruebas enfocadas de los consumidores.
- [ ] `npm --prefix frontend run check`
- [ ] `npm --prefix frontend run build`
- [ ] Pre-commit sobre archivos modificados.

## Registro de avance

| Fecha      | Estado     | Nota                                                                                                |
| ---------- | ---------- | --------------------------------------------------------------------------------------------------- |
| 2026-07-11 | Plan listo | Creado al cerrar `LEGAL-001`; debe iniciar después de contar con dos o tres funciones reales de IA. |

## Resultado de validaciones

No ejecutadas: el ticket está identificado y sus funciones consumidoras todavía no existen.

## Registro de pausa y reanudación

- Estado actual: plan preparado, sin implementación.
- Archivos y contratos cambiados: backlog y este plan.
- Trabajo pendiente: esperar dos o tres funciones reales de IA y ejecutar la integración.
- Bloqueos o aprobaciones: dependencias funcionales `AI-101` a `AI-103`.
- Riesgo residual: futuras funciones podrían crear avisos propios si no consultan este ticket.
- Próxima acción segura: referenciar `LEGAL-002A` al planificar cada ticket `AI-101` a `AI-103` e
  iniciarlo cuando al menos dos estén implementados.
