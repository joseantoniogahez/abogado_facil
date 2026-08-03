# Documentación de producto

Esta carpeta separa la verdad funcional del producto en dos estados:

- [`capabilities/`](capabilities/): capacidades funcionales actuales; fuente para la IA y futuro manual.
- [`plans/implemented/`](plans/implemented/): planes con implementación técnica terminada; algunas
  capacidades pueden seguir bloqueadas para release por gates o aprobaciones.
- [`plans/pending/`](plans/pending/): planes técnicos de capacidades todavía pendientes.
- [`evidence/`](evidence/): evaluaciones, casos de estudio y evidencia reproducible de portafolio.

El índice y el backlog permanecen aquí:

- [`BACKLOG_ABOGADO_FACIL.md`](BACKLOG_ABOGADO_FACIL.md): estado resumido y prioridades.
- [`REQUERIMIENTOS_ABOGADO_FACIL_IA.md`](REQUERIMIENTOS_ABOGADO_FACIL_IA.md): requerimientos y
  visión de producto.
- [`CIERRE_MVP_2026-08-02.md`](CIERRE_MVP_2026-08-02.md): revisión final, alcance cerrado y
  condiciones explícitas para reabrir trabajo.

## Regla de clasificación

Un plan nuevo se crea en `plans/pending/`. Pasa a `plans/implemented/` cuando su implementación,
documentación y validaciones técnicas están completas y el backlog queda `Implementado` o `Hecho`.
`Implementado` no autoriza release: los gates y aprobaciones pendientes deben permanecer explícitos.
La capacidad funcional correspondiente se mantiene en `capabilities/`.

## Uso por audiencia

- IA durante desarrollo: leer `capabilities/` para conocer el producto actual y consultar
  `plans/implemented/` para decisiones y evidencia técnica; leer `plans/pending/` solo para planificar.
- Equipo de producto: usar el backlog para priorización y los planes para decisiones y evidencia.
- Manual de usuario: derivar una versión orientada a tareas y pantallas desde `capabilities/`, sin
  exponer detalles internos de arquitectura, pruebas o migraciones.

La carpeta `docs/ai/` conserva reglas de trabajo para la IA; no duplica la documentación funcional
del producto.
