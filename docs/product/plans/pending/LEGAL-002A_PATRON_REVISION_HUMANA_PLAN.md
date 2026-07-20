# LEGAL-002A - Patrón obligatorio de revisión humana

## Estado del tracking

- ID: `LEGAL-002A`
- Tipo: Frontend
- Prioridad: P0-IA
- Estado: Listo
- Competencia de portafolio: `AI-PRODUCT`

## Objetivo

Crear el patrón compartido para identificar contenido generado por IA y exigir revisión humana
antes de cualquier uso externo.

## Alcance

- Etiqueta de contenido generado por IA.
- Advertencia contextual de borrador o sugerencia.
- Edición previa y aceptación explícita.
- Prohibición de envío automático.
- Relación accesible entre aviso, resultado y acciones.

## Criterios de aceptación

- [ ] El patrón es reutilizable por todas las funciones IA.
- [ ] El usuario puede editar y aceptar explícitamente un resultado.
- [ ] Copiar, guardar o exportar conserva la identificación y el aviso.
- [ ] Las pruebas de accesibilidad y consumidoras cubren el comportamiento.
- [ ] `LEGAL-002B` puede auditar varias funciones sin crear pantallas ficticias.

## Dependencias y exclusiones

Depende de `LEGAL-001` y habilita `LEGAL-002B`. No implementa funciones de IA ni sustituye la
aprobación jurídica de `SEC-002`.

## Validación

- `npm --prefix frontend run check`
- `npm --prefix frontend run build`
- Pruebas enfocadas de teclado, accesibilidad y consumidores reales.
