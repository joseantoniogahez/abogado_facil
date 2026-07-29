# LEGAL-002A - Patrón obligatorio de revisión humana

## Estado del tracking

- ID: `LEGAL-002A`
- Tipo: Frontend
- Prioridad: P0-IA
- Estado: Hecho
- Competencia de portafolio: `AI-PRODUCT`

## Objetivo

Crear el patrón compartido para identificar contenido generado por IA y exigir revisión humana
antes de cualquier uso externo. El ticket entrega el contrato reusable; su primera integración
visible se realiza en `AI-101`, no en una pantalla demostrativa.

## Alcance

- Etiqueta de contenido generado por IA.
- Advertencia contextual de borrador o sugerencia.
- Edición previa y aceptación explícita.
- Prohibición de envío automático.
- Relación accesible entre aviso, resultado y acciones.
- Estados y callbacks que permitan a un consumidor invalidar la aceptación al cambiar el contenido.

## Exclusiones

- Crear una ruta o pantalla sin una función de IA real.
- Ejecutar el analizador de relato inicial, cubierto por `AI-101`.
- Persistir decisiones de revisión o aceptación, cubierto por `AI-104`.
- Auditar consistencia entre varias funciones, cubierto por `LEGAL-002B`.

## Criterios de aceptación

- [x] El patrón es reutilizable por todas las funciones IA.
- [x] El usuario puede editar y aceptar explícitamente un resultado.
- [x] El contrato obliga a que copiar, guardar o exportar parta de contenido revisado y conserve su
  identificación; la persistencia concreta queda en `AI-104`.
- [x] Las pruebas unitarias, de accesibilidad y del contrato público cubren el comportamiento.
- [x] `LEGAL-002B` puede auditar varias funciones sin crear pantallas ficticias.

## Dependencias y exclusiones

Depende de `LEGAL-001`. Habilita la integración de `AI-101`; `AI-104` añade persistencia y
`LEGAL-002B` audita el patrón cuando existan al menos dos consumidores reales. No implementa
funciones de IA ni sustituye la aprobación jurídica de `SEC-002`.

## Validación

- `npm --prefix frontend run check`
- `npm --prefix frontend run build`
- Pruebas enfocadas de teclado, accesibilidad y contrato del componente.
- Las pruebas consumidoras reales se ejecutan en `AI-101` y después en `LEGAL-002B`.
