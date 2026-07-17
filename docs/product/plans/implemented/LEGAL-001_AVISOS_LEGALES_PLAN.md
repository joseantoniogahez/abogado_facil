# LEGAL-001 - Plan de avisos legales mínimos y revisión humana

## Estado del tracking

- ID: `LEGAL-001`
- Tipo: Legal
- Prioridad: P1
- Estado del plan: Completo
- Estado de implementación: Hecho
- Última actualización: 2026-07-11
- Fuente: `docs/product/REQUERIMIENTOS_ABOGADO_FACIL_IA.md`, secciones 5, 6.1, 7.7, 8.2, 12,
  15 y 17.2

## Objetivo

Definir un conjunto mínimo, consistente y visible de avisos para comunicar que Abogado Fácil es una
herramienta de organización y asistencia para profesionales del derecho, que las salidas de IA son
borradores o sugerencias sujetas a revisión humana y que la aplicación no sustituye el criterio
jurídico profesional ni garantiza exactitud o resultados legales.

El resultado de este ticket será la base editorial y de experiencia para la landing y para todas
las funciones de IA que se incorporen después. Debe evitar tanto promesas excesivas como textos
ambiguos, sin intentar sustituir la revisión jurídica formal de los avisos, términos y políticas
del producto antes de un despliegue público.

## Diagnóstico de partida

La fundación ya proporciona:

- una landing pública con el bloque visible `Revisión humana obligatoria`;
- el texto actual: “Las respuestas generadas por IA son apoyo de redacción y organización. Deben
  ser revisadas por un profesional del derecho antes de utilizarse.”;
- un mensaje adicional que aclara que la aplicación no automatiza envíos, presentaciones ni
  decisiones jurídicas;
- un catálogo centralizado de textos de interfaz en `frontend/src/shared/i18n/ui-text.ts`;
- pruebas unitarias y de accesibilidad para la landing.

Brechas frente al producto:

- el texto visible actual no incluye expresamente que Abogado Fácil no garantiza exactitud
  jurídica ni sustituye el criterio profesional;
- todavía no existe un catálogo aprobado de mensajes por contexto y nivel de prominencia;
- no están definidas las reglas que obligarán a mostrar la advertencia junto a cada salida de IA;
- no están definidos el estado, etiqueta y acciones seguras de un resultado generado por IA;
- no existe una regla explícita para impedir que el texto se oculte únicamente en términos,
  tooltips o enlaces secundarios;
- el aviso de privacidad, los términos y la aceptación previa al uso de IA pertenecen a `SEC-002`
  y aún no están materializados.

## Decisiones de alcance

### Incluido

- Aprobar textos mínimos en español para la landing y para resultados generados por IA.
- Definir variantes breves cuando el espacio sea limitado, sin perder el significado esencial.
- Definir ubicación, prominencia, repetición y comportamiento accesible de los mensajes.
- Identificar toda salida de IA como `Borrador generado con IA` o `Sugerencia generada con IA`,
  según corresponda.
- Exigir revisión y edición humana antes de copiar, exportar, guardar como versión final o usar el
  contenido fuera de la aplicación.
- Mantener los avisos en el catálogo centralizado de textos y cubrirlos con pruebas.
- Preparar criterios reutilizables para `AI-101`, `AI-102`, `AI-103`, `AI-201`, `AI-202`, `AI-203`
  y `DOC-002`/`DOC-003`.

### Fuera de alcance

- Redactar o publicar aviso de privacidad, términos y condiciones, política de cookies o política
  de conservación/eliminación de datos.
- Implementar la aceptación de términos antes de usar IA; corresponde a `SEC-002` y a los tickets
  BYOK afectados.
- Definir información societaria, domicilio, jurisdicción, legislación aplicable o mecanismos de
  contacto legal que todavía no han sido decididos.
- Explicar en detalle la transmisión de contenido al proveedor elegido, precios o tratamiento de
  API keys; corresponde a `SEC-002`, `AI-001` y `AI-002`.
- Implementar funciones de IA, documentos, exportaciones o envíos.
- Garantizar que los textos constituyan asesoría legal o cumplimiento normativo suficiente para un
  lanzamiento productivo.

## Decisiones cerradas para implementar

- [x] La landing conservará un aviso visible sin depender de interacción del visitante.
- [x] Cada resultado de IA tendrá una etiqueta persistente que lo identifique como borrador o
  sugerencia, además de una advertencia contextual visible.
- [x] El mensaje no se presentará exclusivamente en un tooltip, modal descartable, pie de página o
  documento enlazado.
- [x] La advertencia no usará formulaciones que trasladen toda responsabilidad al usuario de forma
  vaga ni afirmará que elimina riesgos jurídicos.
- [x] No se utilizarán frases como “documento listo para presentar”, “resultado correcto”,
  “asesoría legal” o “garantizado” para contenido generado por IA.
- [x] Los controles de copiar, exportar o finalizar no ocultarán ni eliminarán la identificación de
  borrador antes de que exista una acción explícita de revisión humana.
- [x] Los textos legales de producto estarán centralizados y serán revisables sin duplicarlos en
  componentes.
- [x] `LEGAL-001` no cerrará los requisitos de privacidad y consentimiento de `SEC-002`.

## Catálogo editorial propuesto

### Aviso principal de la landing

> Las respuestas generadas por IA son apoyo de redacción y organización. Deben ser revisadas y
> validadas por un profesional del derecho antes de utilizarse. Abogado Fácil no garantiza su
> exactitud jurídica ni sustituye el criterio profesional.

Título recomendado: `Revisión humana obligatoria`.

### Aviso contextual para resultados de IA

> Borrador generado con IA. Revisa y valida su contenido, hechos, fechas, cálculos, fundamentos y
> adecuación al asunto antes de utilizarlo. Abogado Fácil no garantiza exactitud jurídica ni
> resultados legales.

La lista de elementos a revisar puede adaptarse al tipo de salida, pero no debe eliminar el deber
de revisión ni las limitaciones sobre exactitud y resultados.

### Variante breve

> Contenido generado con IA: revisa y valida antes de utilizarlo.

La variante breve solo será válida cuando el aviso contextual completo permanezca visible o
disponible en la misma vista, asociado inequívocamente al resultado.

### Etiquetas de estado

- `Borrador generado con IA` para mensajes, resúmenes, cronologías y documentos editables.
- `Sugerencia generada con IA` para preguntas, checklists y recomendaciones que no constituyan un
  documento final.
- No usar `Aprobado`, `Validado`, `Correcto` o equivalentes salvo que una futura función implemente
  una revisión humana explícita y auditable con semántica documentada.

## Reglas de presentación y experiencia

- El aviso de landing aparecerá dentro del contenido principal, con contraste suficiente y lectura
  disponible para tecnologías de asistencia.
- En una función de IA, la etiqueta y el aviso contextual se mostrarán junto al resultado y antes
  de sus acciones de uso externo.
- El aviso persistirá después de regenerar, editar o guardar el resultado mientras conserve su
  condición de contenido asistido por IA.
- Color e iconografía serán complementarios; el significado no dependerá solo de ellos.
- La advertencia no interrumpirá repetidamente el flujo mediante modales si puede mantenerse
  visible en contexto.
- Los errores técnicos, estados de carga y ausencia de BYOK no se confundirán con este aviso.
- Copias o exportaciones conservarán la condición de borrador cuando el formato y el alcance del
  ticket consumidor lo permitan; cada ticket deberá decidir y probar esa representación.
- El lenguaje será claro para abogados y despachos pequeños, sin tecnicismos de modelos o
  proveedores que no ayuden a decidir cómo usar el resultado.

## Criterios de aceptación

- [x] La landing muestra el aviso principal completo y visible sin abrir menús, modales o enlaces.
- [x] El aviso declara revisión y validación profesional, ausencia de garantía de exactitud jurídica
  y que la aplicación no sustituye el criterio profesional.
- [x] El contenido no promete asesoría directa, resultados legales ni documentos listos para
  presentar.
- [x] Existe una regla documentada y reutilizable para distinguir borradores de sugerencias de IA.
- [x] Toda función de IA futura debe mostrar una etiqueta y el aviso contextual antes de acciones
  de copiar, exportar o uso externo.
- [x] La variante breve nunca sustituye por sí sola al aviso contextual completo.
- [x] Los avisos son perceptibles en móvil y escritorio, navegables con teclado y comprensibles por
  lector de pantalla.
- [x] Los textos se obtienen del catálogo centralizado y las pruebas los consultan mediante `t(...)`.
- [x] Las pruebas cubren presencia, contenido esencial y accesibilidad del aviso en la landing.
- [x] `LEGAL-002` exige pruebas consumidoras que impiden presentar una salida de IA sin su
  identificación y advertencia.
- [x] La documentación distingue expresamente este alcance de privacidad, términos y aceptación
  BYOK en `SEC-002`.
- [x] La revisión jurídica humana del texto queda como gate de lanzamiento de `SEC-002`, sin afirmar
  que haya sido realizada desde este ticket.

## Plan de trabajo

### 1. Cerrar lenguaje y gobernanza editorial

- [x] Registrar la aceptación de producto de la presentación y revisión manual comunicada por el
  responsable del repositorio el 2026-07-11.
- [x] Asignar a `SEC-002` la revisión de un profesional competente en la jurisdicción de lanzamiento.
- [x] Exigir en `SEC-002` el registro de versión, fecha, responsable y resultado de la aprobación
  jurídica antes del lanzamiento.
- [x] Coordinar con `SEC-002` el mecanismo futuro para versionar cambios materiales.

### 2. Actualizar la landing

- [x] Sustituir el texto actual por el aviso principal propuesto, pendiente de aprobación jurídica.
- [x] Mantener el bloque dentro del contenido principal y verificar jerarquía semántica, contraste y
  responsive.
- [x] Actualizar las pruebas de landing y el catálogo centralizado; conservar el gate de accesibilidad.
- [x] Confirmar que el cambio no altera rutas, autenticación ni dependencias.

### 3. Establecer el patrón para funciones de IA

- [x] Incorporar al sistema de UI un patrón reutilizable de etiqueta y advertencia contextual cuando
  el primer ticket de IA materialice resultados.
- [x] Definir propiedades semánticas para `borrador` y `sugerencia` sin acoplar `shared` a features.
- [x] Exigir que cada ticket consumidor adapte la lista de revisión al tipo de salida.
- [x] Trasladar a `LEGAL-002` la prueba de que regenerar, editar y guardar no hacen desaparecer la
  advertencia cuando existan 2 o 3 funciones reales de IA.
- [x] Trasladar a `LEGAL-002` la prueba de la relación accesible entre aviso, resultado y acciones.

### 4. Documentación y tracking

- [x] Actualizar `docs/product/BACKLOG_ABOGADO_FACIL.md` a `En progreso` al iniciar implementación y a
  `Hecho` solo después de aprobar textos y superar los gates.
- [x] Mantener este archivo actualizado con decisiones, aprobación, validaciones y riesgos.
- [x] Actualizar `frontend/docs/operations/accessibility_gate.md` solo si cambia su regla o cobertura
  contractual.
- [x] Actualizar `frontend/docs/operations/e2e_smoke_suite.md` si el aviso se incorpora a un recorrido
  e2e obligatorio.
- [x] Crear `LEGAL-002` para referenciar y validar este patrón después de 2 o 3 funciones de IA.
- [x] Mantener `SEC-002` abierto hasta contar con privacidad, términos, transmisión al proveedor y
  aceptación previa al uso de IA.

### 5. Validación

- [x] Ejecutar pruebas enfocadas de la landing y del catálogo de textos.
- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run build`
- [x] `pre-commit run --files docs/LEGAL-001_AVISOS_LEGALES_PLAN.md docs/product/BACKLOG_ABOGADO_FACIL.md`
- [x] Revisar manualmente el aviso en móvil y escritorio, zoom al 200 %, teclado y lector de pantalla.
- [x] Mantener la revisión jurídica humana como gate pendiente de `SEC-002`; los gates técnicos no la
  sustituyen.

## Matriz inicial de archivos afectados

| Superficie    | Archivos o áreas esperadas                                                       |
| ------------- | -------------------------------------------------------------------------------- |
| Tracking      | `docs/LEGAL-001_AVISOS_LEGALES_PLAN.md`, `docs/product/BACKLOG_ABOGADO_FACIL.md` |
| Textos        | `frontend/src/shared/i18n/ui-text.ts` y pruebas del catálogo                     |
| Landing       | `frontend/src/features/landing` y pruebas asociadas                              |
| Accesibilidad | pruebas de ruta y contrato aplicables; documentación solo si cambia la regla     |
| IA futura     | componentes de resultado de cada feature y sus pruebas, cuando existan           |
| Legal futuro  | coordinación con `SEC-002`, sin cerrarlo desde este ticket                       |

La lista es orientativa. Este plan no autoriza implementar funciones de IA, aceptación de términos
ni páginas legales completas.

## Riesgos y mitigaciones

| Riesgo                                                        | Mitigación prevista                                                                        |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Tratar un texto de producto como dictamen jurídico definitivo | Revisión profesional antes del lanzamiento y registro de aprobación                        |
| Advertencia visible en landing pero ausente al usar IA        | Patrón obligatorio junto a cada resultado y pruebas por ticket consumidor                  |
| Fatiga por avisos repetitivos                                 | Mensaje persistente en contexto y variante breve subordinada, evitando modales recurrentes |
| Usuario interpreta el resultado como listo para presentar     | Etiqueta de borrador/sugerencia, acciones posteriores y lenguaje sin promesas              |
| Pérdida del aviso al copiar o exportar                        | Decisión explícita y pruebas en cada flujo de salida                                       |
| Texto inaccesible o basado solo en color                      | Semántica, contraste, asociación y pruebas de accesibilidad                                |
| Confundir LEGAL-001 con cumplimiento de privacidad            | Frontera expresa con `SEC-002` y permanencia de ese ticket abierto                         |
| Deriva entre copias en distintas funciones                    | Catálogo central y patrón reutilizable, sin literales duplicados                           |

## Dependencias y evolución

- `PROD-001` ya proporciona el bloque de landing que deberá adoptar el texto aprobado.
- `AI-001`/`AI-002` y `SEC-002` deberán añadir información de BYOK, costos, transmisión al proveedor
  y aceptación previa sin reemplazar la advertencia de revisión humana.
- `AI-101`, `AI-102`, `AI-103`, `AI-201`, `AI-202` y `AI-203` deberán aplicar el patrón a sus
  resultados según sean borradores o sugerencias.
- `DOC-002`/`DOC-003` deberán conservar la condición de borrador y exigir revisión antes de copiar o
  exportar según el contrato final.
- Una futura revisión de cumplimiento podrá ampliar o versionar los textos por jurisdicción,
  idioma, proveedor o tipo de función.

## Preguntas que no bloquean el plan

- ¿Cuál será la primera jurisdicción de lanzamiento para asignar la revisión jurídica adecuada?
- ¿Qué persona o rol aprobará y versionará los textos legales del producto?
- ¿Las exportaciones incluirán visualmente la etiqueta de borrador o metadatos equivalentes?
- ¿Qué evidencia de revisión humana deberá persistirse, si alguna, para convertir un borrador en una
  versión final?

Estas respuestas deben cerrarse antes de los flujos productivos afectados, pero no impiden aprobar
la estructura inicial de LEGAL-001.

## Registro de avance

| Fecha      | Estado      | Nota                                                                                                                                                                                                                                                                                   |
| ---------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-07-11 | Plan listo  | Se revisaron requisitos, backlog, landing existente y fronteras con IA/BYOK/SEC-002; se definieron catálogo propuesto, reglas de presentación, criterios y gates.                                                                                                                      |
| 2026-07-11 | En progreso | Se implementó el aviso principal propuesto en la landing, se añadieron al catálogo las etiquetas y variantes reutilizables para resultados de IA y se reforzaron sus pruebas. Pendiente validación técnica y revisión jurídica humana.                                                 |
| 2026-07-11 | En progreso | Se añadió `AiGeneratedContentNotice` como patrón compartido para borradores y sugerencias, con nombre y descripción accesibles, aviso completo persistente y pruebas axe. El build excedió inicialmente el presupuesto CSS; se reutilizaron tokens existentes y el segundo build pasó. |
| 2026-07-11 | Hecho       | El responsable del repositorio confirmó la revisión manual en móvil/escritorio, zoom 200 %, teclado y lector de pantalla. La integración con 2 o 3 funciones reales se trasladó a `LEGAL-002` y la aprobación jurídica formal previa al lanzamiento permanece en `SEC-002`.            |

## Resultado de validaciones

Estado al 2026-07-11:

- Revisión documental de `docs/product/REQUERIMIENTOS_ABOGADO_FACIL_IA.md`: completada.
- Verificación de los textos actuales y su prueba en la landing: completada.
- Pruebas enfocadas de landing, catálogo, aviso compartido y accesibilidad: 15 pruebas aprobadas.
- `npm --prefix frontend run check`: aprobado; 45 archivos y 190 pruebas, coverage, OpenAPI y
  auditoría de dependencias sin fallas.
- `npm --prefix frontend run build`: aprobado; build de producción y presupuestos de rendimiento
  dentro de límite.
- `pre-commit` sobre archivos modificados: aprobado después de aplicar el formato Markdown del hook.
- Revisión manual en dispositivos reales, zoom al 200 %, teclado y lector de pantalla: aprobada por
  el responsable del repositorio el 2026-07-11.
- Revisión jurídica humana: no realizada; transferida explícitamente a `SEC-002` como gate previo a
  cualquier lanzamiento público o productivo.

## Registro de pausa y reanudación

- Estado actual: `LEGAL-001` completado; landing, catálogo y patrón compartido implementados,
  documentados y probados.
- Archivos y contratos nuevos: `frontend/src/shared/ui/AiGeneratedContentNotice.tsx`, su prueba y el
  contrato de accesibilidad frontend.
- Trabajo pendiente fuera de este ticket: `LEGAL-002` validará consumidores reales y `SEC-002`
  registrará la revisión jurídica formal antes del lanzamiento.
- Bloqueos o aprobaciones: ninguno para cerrar `LEGAL-001` con el alcance redefinido.
- Riesgo residual: el patrón todavía no tiene consumidores; queda visible y rastreado en
  `LEGAL-002`.
- Próxima acción segura: implementar las funciones `AI-101` a `AI-103`; iniciar `LEGAL-002` cuando
  existan al menos dos flujos reales.

`LEGAL-001` queda con plan `Completo` e implementación `Hecho`. Este cierre no equivale a aprobación
jurídica para lanzamiento: esa evidencia sigue siendo obligatoria en `SEC-002`.
