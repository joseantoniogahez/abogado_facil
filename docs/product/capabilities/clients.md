# Clientes

## Propósito

Mantener el directorio de clientes del despacho y navegar desde cada cliente hacia sus asuntos.

## Flujo principal

- Crear clientes con información de contacto.
- Listar y buscar clientes por nombre o teléfono.
- Consultar el detalle de un cliente.
- Editar parcialmente los datos de un cliente.
- Navegar desde un cliente hacia sus asuntos.

## Reglas funcionales

- Los clientes pertenecen al despacho de la sesión actual.
- No se expone un selector de despacho al crear o editar.
- Los teléfonos mexicanos se normalizan y se muestran como número nacional de diez dígitos.
- Un cliente inexistente o perteneciente a otro despacho responde como no encontrado.

## Límites y advertencias

- El MVP normaliza teléfonos mexicanos y no administra múltiples países o despachos por cliente.
- Eliminar clientes no forma parte de la capacidad actual.

## Permisos

- Todas las operaciones requieren sesión autenticada y se limitan al despacho actual.

## Estados de error

- Datos inválidos conservan el formulario para corrección.
- Un cliente inexistente o ajeno devuelve el mismo estado de no encontrado.
- Fallos recuperables de listado o detalle permiten reintentar.

## Referencias técnicas

- [CORE-001](../plans/implemented/CORE-001_GESTION_CLIENTES_PLAN.md)
