# ADR: BYOK y arquitectura multi-provider

- Estado: aceptado
- Fecha de decisión: 2026-07-25
- Revalidado: 2026-08-02

## Contexto

Abogado Fácil necesita IA controlada sin absorber consumo variable ni acoplar el producto a un
SDK. Las credenciales pertenecen a cada usuario y los datos legales requieren aislamiento,
minimización y errores seguros.

## Decisión

Se adopta BYOK por usuario, cifrado con AES-GCM en reposo y nunca expuesto al frontend. Los casos de
uso dependen de `AiProviderPort`; `OpenAIProvider`, `GeminiProvider` y `MockProvider` usan el mismo
contrato. Los SDK oficiales quedan confinados a adaptadores inyectables, con retries internos
deshabilitados para conservar un único propietario de retry. Proveedor y modelo se seleccionan de
la credencial vigente y se registran junto con versiones de prompt y schema.

## Alternativas consideradas

| Alternativa                                                 | Motivo de descarte                                                           |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Clave única de plataforma                                   | traslada costo y riesgo de abuso al producto y mezcla cuotas entre despachos |
| Integración directa del SDK en cada feature                 | duplica seguridad, errores y pruebas; impide sustituir proveedor             |
| Un solo proveedor                                           | reduce portabilidad y contradice el alcance OpenAI/Gemini                    |
| Claves en navegador o almacenamiento reversible por cliente | expone secretos y rompe el límite backend                                    |
| Retry dentro de SDK y aplicación                            | multiplica intentos, costo y latencia de forma no determinista               |

## Consecuencias

- A favor: costo atribuible al usuario, adapters intercambiables, mock determinista y taxonomía
  común; secretos, outputs y observabilidad atraviesan controles compartidos.
- Costos: onboarding adicional, soporte por proveedor, rotación de claves a cargo del usuario y
  diferencias de modelos/capacidades que deben probarse.
- Riesgos residuales: una clave válida no garantiza cuota, disponibilidad ni calidad; actualizar un
  SDK exige revalidar errores, JSON estructurado, timeouts, redacción y ausencia de herramientas.

## Reglas de revisión

Cambiar propiedad de credenciales, añadir un proveedor, habilitar tool calling, mover retries o
persistir contenido crudo requiere actualizar este ADR, el threat model y las pruebas contractuales.
