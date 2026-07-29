# LEGAL-002B - Auditoría de consistencia de avisos IA

## Estado del tracking

- ID: `LEGAL-002B`
- Tipo: Frontend
- Prioridad: P0-IA
- Estado del plan: Hecho
- Estado de implementación: Hecho
- Última actualización: 2026-07-29
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

- [x] Al menos dos funciones reales de IA usan el patrón compartido.
- [x] Cada salida se identifica correctamente como borrador o sugerencia.
- [x] El aviso completo permanece visible junto al resultado y antes de acciones externas.
- [x] Regenerar, editar y guardar no eliminan la identificación ni el aviso.
- [x] Resultado, aviso y acciones tienen una relación accesible verificable.
- [x] Las pruebas consumidoras fallan si se omite la identificación o advertencia.
- [x] La revisión documental de frontend y de cada ticket consumidor queda registrada.
- [x] Los gates frontend requeridos pasan.

## Plan de trabajo

### Integración

- [x] Inventariar las funciones IA disponibles y clasificar sus resultados.
- [x] Integrar `AiGeneratedContentNotice` en los tres flujos de Fase 3.
- [x] Asociar los IDs del aviso con resultados y controles relacionados.

### Pruebas y documentación

- [x] Cubrir regeneración, edición, guardado y acciones externas disponibles.
- [x] Ejecutar axe y verificar controles nativos de teclado sobre los estados reales.
- [x] Actualizar documentación operativa y e2e con el contrato entregado.
- [x] Registrar documentos revisados pero intencionalmente sin cambios.

### Validación

- [x] Pruebas enfocadas de los consumidores.
- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run build`
- [x] Pre-commit sobre archivos modificados.

## Registro de avance

| Fecha      | Estado     | Nota                                                                                                    |
| ---------- | ---------- | ------------------------------------------------------------------------------------------------------- |
| 2026-07-11 | Plan listo | Creado al cerrar `LEGAL-001`; debe iniciar después de contar con dos o tres funciones reales de IA.     |
| 2026-07-29 | Hecho      | Tres consumidores reales integrados; revisión, accesibilidad, check, build, e2e y pre-commit aprobados. |

## Resultado de validaciones

Los tres consumidores de Fase 3 usan `AiHumanReview` y `AiGeneratedContentNotice`. Las pruebas del
componente cubren identificación, relación accesible, edición, aceptación y copia; axe no detecta
violaciones. El check frontend con 261 pruebas, build, 14 e2e y pre-commit completo pasan.

## Registro de pausa y reanudación

- Estado actual: auditoría aplicada a los tres consumidores reales de Fase 3.
- Archivos y contratos cambiados: componente reusable, consumidores IA, pruebas, e2e y documentación
  de Fase 3.
- Trabajo pendiente: ninguno dentro de `LEGAL-002B`.
- Bloqueos o aprobaciones: ninguno.
- Riesgo residual: futuras funciones deben reutilizar el patrón y conservar sus pruebas.
- Próxima acción segura: aplicar el mismo contrato a cualquier función IA nueva.
