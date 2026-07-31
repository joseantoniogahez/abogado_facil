# Asuntos y expediente

## Capacidades disponibles

- Crear, listar, buscar y editar asuntos asociados a un cliente.

- Seleccionar el tipo de asunto desde un catálogo cerrado que incluye `Otro`.

- Gestionar notas: crear, editar, eliminar y marcar como relevantes.

- Gestionar checklists con estados completo, pendiente y no aplica, además de elementos personalizados.

- Gestionar tareas con fecha límite y estado completado.

- Configurar honorarios, registrar anticipos y pagos parciales, y consultar saldo.

- Ejecutar calculadoras determinísticas de adeudos, rentas vencidas e interés simple.

- Guardar y listar resultados de cálculo como instantáneas inmutables.

- Consultar el detalle del asunto organizado en tabs de resumen, seguimiento, finanzas y documentos y notas.

- Generar un resumen estructurado del expediente con IA BYOK, revisarlo y reutilizar el resultado
  guardado sin recomputarlo al consultar el asunto.

- Generar una cronología editable con fechas validadas, eventos sin fecha explícitos y fuente
  visible cuando fue aportada.

## Reglas funcionales

- Todos los recursos del expediente están aislados por despacho.
- Los recursos inexistentes o ajenos producen el mismo resultado de no encontrado.
- Los cálculos son estimaciones y no sustituyen asesoría jurídica.
- Los importes del MVP usan MXN y precisión de dos decimales.
- Los abonos son inmutables y los resultados guardados no se editan ni eliminan.
- El tab activo del detalle se conserva en la URL mediante el parámetro `tab`; valores inválidos vuelven a `summary`.

## Referencias técnicas

- [CORE-002](../plans/implemented/CORE-002_GESTION_ASUNTOS_PLAN.md)
- [CORE-003](../plans/implemented/CORE-003_NOTAS_EXPEDIENTE_PLAN.md)
- [CORE-006](../plans/implemented/CORE-006_CHECKLISTS_BASE_PLAN.md)
- [CORE-007](../plans/implemented/CORE-007_TAREAS_RECORDATORIOS_PLAN.md)
- [CORE-008](../plans/implemented/CORE-008_CONTROL_PAGOS_PLAN.md)
- [CORE-009](../plans/implemented/CORE-009_CALCULADORAS_BASICAS_PLAN.md)
- [CORE-011](../plans/implemented/CORE-011_CATALOGO_TIPOS_ASUNTO_PLAN.md)
- [UX-002](../plans/implemented/UX-002_TABS_DETALLE_ASUNTOS_PLAN.md)
- [AI-201](../plans/implemented/AI-201_RESUMEN_EXPEDIENTE_PLAN.md)
- [AI-202](../plans/implemented/AI-202_CRONOLOGIA_HECHOS_PLAN.md)
