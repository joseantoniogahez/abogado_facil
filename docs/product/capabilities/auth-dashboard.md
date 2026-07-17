# Autenticación y dashboard

## Capacidades disponibles

- Registro público con nombre, correo, contraseña y despacho opcional.
- Inicio y cierre de sesión con correo normalizado.
- Perfil autenticado con edición de datos personales, despacho y contraseña.
- Dashboard con resumen del despacho, tareas próximas y estado de las capacidades disponibles.

## Reglas funcionales

- Cada alta crea un despacho y asigna al usuario como propietario inicial.
- El usuario solo consulta datos del despacho asociado a su sesión.
- La sesión usa token bearer; una sesión inválida dirige al flujo de acceso.
- El dashboard no permite seleccionar manualmente otro despacho.

## Referencias técnicas

- [PROD-002](../plans/implemented/PROD-002_AUTH_ALIGNMENT_PLAN.md)
- [PROD-003](../plans/implemented/PROD-003_DASHBOARD_PLAN.md)
