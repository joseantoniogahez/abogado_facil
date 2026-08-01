# Autenticación y dashboard

## Propósito

Permitir el alta, acceso y administración de la cuenta, y ofrecer un resumen inicial del despacho.

## Flujo principal

- Registro público con nombre, correo, contraseña y despacho opcional.
- Inicio y cierre de sesión con correo normalizado.
- Perfil autenticado con edición de datos personales, despacho y contraseña.
- Dashboard con resumen del despacho, tareas próximas y estado de las capacidades disponibles.

## Reglas funcionales

- Cada alta crea un despacho y asigna al usuario como propietario inicial.
- El usuario solo consulta datos del despacho asociado a su sesión.
- La sesión usa token bearer; una sesión inválida dirige al flujo de acceso.
- El dashboard no permite seleccionar manualmente otro despacho.

## Límites y advertencias

- El MVP crea un despacho por alta y no permite cambiar entre varios despachos.
- El dashboard resume información existente; no sustituye las vistas de detalle.

## Permisos

- Registro e inicio de sesión son públicos; perfil y dashboard requieren sesión autenticada.
- La sesión solo permite consultar y modificar la cuenta y el despacho asociados.

## Estados de error

- Credenciales incorrectas o una cuenta deshabilitada impiden iniciar sesión.
- Una sesión inválida se elimina y dirige al flujo de acceso.
- Conflictos de correo o datos inválidos conservan el formulario y muestran un mensaje seguro.

## Referencias técnicas

- [PROD-002](../plans/implemented/PROD-002_AUTH_ALIGNMENT_PLAN.md)
- [PROD-003](../plans/implemented/PROD-003_DASHBOARD_PLAN.md)
