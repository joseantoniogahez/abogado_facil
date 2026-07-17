# Documentación de producto

Esta carpeta separa la verdad funcional del producto en dos estados:

- [`capabilities/`](capabilities/): capacidades funcionales actuales; fuente para la IA y futuro manual.
- [`plans/implemented/`](plans/implemented/): planes técnicos de capacidades ya entregadas.
- [`plans/pending/`](plans/pending/): planes técnicos de capacidades todavía pendientes.

El índice y el backlog permanecen aquí:

- [`BACKLOG_ABOGADO_FACIL.md`](BACKLOG_ABOGADO_FACIL.md): estado resumido y prioridades.
- [`REQUERIMIENTOS_ABOGADO_FACIL_IA.md`](REQUERIMIENTOS_ABOGADO_FACIL_IA.md): requerimientos y
  visión de producto.

## Regla de clasificación

Un plan nuevo se crea en `plans/pending/`. Pasa a `plans/implemented/` únicamente cuando sus
criterios de aceptación, documentación y gates están completos y el backlog está en `Hecho`.
La capacidad funcional correspondiente se mantiene en `capabilities/`.

## Uso por audiencia

- IA durante desarrollo: leer `capabilities/` para conocer el producto actual y consultar
  `plans/implemented/` para decisiones y evidencia técnica; leer `plans/pending/` solo para planificar.
- Equipo de producto: usar el backlog para priorización y los planes para decisiones y evidencia.
- Manual de usuario: derivar una versión orientada a tareas y pantallas desde `capabilities/`, sin
  exponer detalles internos de arquitectura, pruebas o migraciones.

La carpeta `docs/ai/` conserva reglas de trabajo para la IA; no duplica la documentación funcional
del producto.
