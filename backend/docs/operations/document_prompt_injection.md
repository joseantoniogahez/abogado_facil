# Proteccion contra prompt injection documental

## Contrato obligatorio

Todo texto recuperado de documentos, notas u otros campos creados por usuarios es dato no confiable.
No puede ocupar el canal de instrucciones del proveedor, modificar la instruccion de la funcion ni
habilitar herramientas.

El unico flujo permitido es:

1. construir `MinimizedAIContext` mediante `build_minimized_ai_context`;
1. enviar `MinimizedAIContext.instruction` junto con `UNTRUSTED_DATA_POLICY` en el canal de sistema;
1. enviar `MinimizedAIContext.render_untrusted_data()` como contenido de usuario;
1. mantener la lista de herramientas vacia.

El sobre `<untrusted_document_data>` escapa caracteres de control XML en cada valor. Por eso un
documento que contenga `</untrusted_document_data>`, instrucciones simuladas, cambios de rol o
solicitudes de ejecutar acciones permanece dentro del campo de datos y no puede cerrar el sobre.

## Capacidades prohibidas

`AiTextRequest` no acepta herramientas, funciones, URLs, callbacks ni configuracion de ejecucion.
Los adaptadores no incluyen el campo `tools`; OpenAI ademas fija `tool_choice="none"`. Mock comparte
el mismo request sin ninguna ruta de ejecucion.

Agregar tool calling, recuperacion autonoma, navegacion o mutaciones requiere otro contrato,
threat model, allowlist de herramientas, autorizacion por accion, revision humana y pruebas. No es
una ampliacion permitida de este gate.

## Limite de la defensa

La separacion de autoridad, el escape del sobre y la ausencia de capacidades impiden que texto
documental se convierta estructuralmente en instrucciones o ejecute herramientas. Un modelo sigue
siendo probabilistico: contenido adversarial puede degradar o sesgar una respuesta. Por eso cada
funcion debe usar schema cerrado, validacion de salida y la revision humana definida por
`LEGAL-002A` antes de presentar consecuencias juridicas.

No se usan detectores basados en palabras prohibidas: producen falsos positivos y no cubren ataques
nuevos. Las pruebas incluyen contenido adversarial que intenta cerrar el sobre, cambiar
instrucciones y solicitar herramientas.
