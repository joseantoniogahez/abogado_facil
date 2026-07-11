export const ES_MESSAGES = {
  "admin.common.error.generic":
    "No fue posible completar la operación, intenta nuevamente.",
  "admin.common.error.title": "Error del módulo administrador",
  "admin.common.loading": "Cargando módulo administrador...",
  "admin.as.submit": "Asignar",
  "admin.as.pending": "Asignando...",
  "admin.as.rid": "ID de rol",
  "admin.as.uid": "ID de usuario",
  "admin.as.placeholder": "Selecciona un ID.",
  "admin.as.rEmpty": "Sin usuarios directos.",
  "admin.as.rTitle": "Usuarios directos",
  "admin.as.title": "Roles directos",
  "admin.as.uEmpty": "Sin roles directos.",
  "admin.as.uTitle": "Roles directos del usuario",
  "admin.auditLog.actor.system": "Sistema",
  "admin.auditLog.columns.action": "Acción",
  "admin.auditLog.columns.actor": "Actor",
  "admin.auditLog.columns.createdAt": "Fecha UTC",
  "admin.auditLog.columns.resource": "Recurso",
  "admin.auditLog.columns.summary": "Resumen",
  "admin.auditLog.empty": "No hay eventos de auditoría registrados.",
  "admin.auditLog.subtitle":
    "Revisa los eventos administrativos mas recientes registrados por la API.",
  "admin.auditLog.title": "Bitacora de auditoría",
  "admin.pm.help": "own=propio, tenant=tenant actual, any=global.",
  "admin.pm.list": "Permisos asignados",
  "admin.pm.manual": "Sin roles:manage, usa ID manual.",
  "admin.pm.missing": "Rol fuera del catálogo.",
  "admin.pm.title": "Permisos por rol",
  "admin.roles.actions.delete": "Eliminar rol",
  "admin.roles.actions.delete.confirm": "Eliminar el rol {roleName}?",
  "admin.roles.actions.update": "Guardar rol",
  "admin.roles.actions.update.pending": "Guardando...",
  "admin.roles.card.noParents": "Sin roles padre asignados.",
  "admin.roles.card.noPermissions": "Sin permisos asignados.",
  "admin.roles.card.parents": "Jerarquía de roles",
  "admin.roles.card.permissions": "Permisos del rol",
  "admin.roles.create.name": "Nombre del rol",
  "admin.roles.create.submit": "Crear rol",
  "admin.roles.create.submit.pending": "Creando rol...",
  "admin.roles.create.title": "Crear rol",
  "admin.roles.list.empty": "No hay roles registrados.",
  "admin.roles.parents.add": "Asignar rol padre",
  "admin.roles.parents.remove": "Remover",
  "admin.roles.parents.select": "Selecciona rol padre",
  "admin.roles.permissions.add": "Asignar permiso",
  "admin.roles.permissions.remove": "Quitar",
  "admin.roles.permissions.scope.any": "Alcance: any",
  "admin.roles.permissions.scope.label": "Alcance",
  "admin.roles.permissions.select": "Selecciona permiso",
  "admin.roles.subtitle": "Gestiona roles, jerarquía y permisos predefinidos.",
  "admin.roles.title": "Administración de roles y permisos",
  "admin.users.actions.delete": "Deshabilitar usuario",
  "admin.users.actions.delete.confirm": "¿Deshabilitar la cuenta {email}?",
  "admin.users.actions.edit": "Editar usuario",
  "admin.users.columns.actions": "Acciones",
  "admin.users.columns.roles": "Roles",
  "admin.users.columns.status": "Estado",
  "admin.users.columns.email": "Correo electrónico",
  "admin.users.create.password": "Contraseña", // pragma: allowlist secret
  "admin.users.create.roles": "Roles",
  "admin.users.create.submit": "Crear usuario",
  "admin.users.create.submit.pending": "Creando usuario...",
  "admin.users.create.title": "Crear usuario",
  "admin.users.create.email": "Correo electrónico",
  "admin.users.edit.cancel": "Cancelar",
  "admin.users.edit.currentPassword": "Contraseña actual", // pragma: allowlist secret
  "admin.users.edit.disabled": "Usuario deshabilitado",
  "admin.users.edit.newPassword": "Nueva contraseña", // pragma: allowlist secret
  "admin.users.edit.roles": "Roles",
  "admin.users.edit.submit": "Guardar cambios",
  "admin.users.edit.submit.pending": "Guardando...",
  "admin.users.edit.title": "Editar usuario",
  "admin.users.edit.email": "Correo electrónico",
  "admin.users.list.empty": "No hay usuarios registrados.",
  "admin.users.list.title": "Usuarios",
  "admin.users.roles.hidden.error":
    "Los controles de roles estan ocultos porque no fue posible cargar el catálogo.",
  "admin.users.roles.hidden.permission":
    "Los controles de roles estan ocultos porque esta sesión no puede consultar el catálogo de roles.",
  "admin.users.roles.loading": "Cargando catálogo de roles para esta vista...",
  "admin.users.status.active": "Activo",
  "admin.users.status.disabled": "Inactivo",
  "admin.users.subtitle":
    "Crea, actualiza y deshabilita usuarios; los controles de roles aparecen cuando el catálogo esta disponible.",
  "admin.users.title": "Administración de usuarios",
  "auth.login.badge": "Login",
  "auth.login.error.generic":
    "No fue posible iniciar sesión, intenta nuevamente.",
  "auth.login.fields.password": "Contraseña", // pragma: allowlist secret
  "auth.login.fields.email": "Correo electrónico",
  "auth.login.footer.backToLanding": "Regresa a Abogado Fácil",
  "auth.login.footer.createAccount": "Crea tu cuenta",
  "auth.login.footer.firstTime": "Primera vez aquí?",
  "auth.login.submit.default": "Entrar",
  "auth.login.submit.pending": "Validando...",
  "auth.login.subtitle":
    "Usa tus credenciales para continuar al panel de bienvenida.",
  "auth.login.title": "Inicia sesión",
  "auth.login.validating.title": "Validando sesión...",
  "auth.register.badge": "Registro",
  "auth.register.error.generic":
    "No fue posible crear la cuenta, intenta nuevamente.",
  "auth.register.footer.haveAccount": "Ya tienes cuenta?",
  "auth.register.footer.signIn": "Inicia sesión",
  "auth.register.submit.default": "Crear cuenta",
  "auth.register.submit.pending": "Creando cuenta...",
  "auth.register.subtitle":
    "Crea un acceso local usando el contrato actual de autenticación.",
  "auth.register.success.body":
    "La cuenta {email} quedo lista. Inicia sesión para continuar.",
  "auth.register.fields.firstName": "Nombre",
  "auth.register.fields.middleName": "Segundo nombre (opcional)",
  "auth.register.fields.lastName": "Apellidos",
  "auth.register.fields.displayName": "Nombre para mostrar",
  "auth.register.fields.firmName": "Nombre del despacho (opcional)",
  "auth.register.success.title": "Cuenta creada",
  "auth.register.title": "Crea tu cuenta",
  "auth.shared.password.hint":
    "La contraseña requiere al menos 8 caracteres, una minúscula, una mayúscula y un número, y no puede contener el correo electrónico.", // pragma: allowlist secret
  "auth.shared.email.hint":
    "El correo se normaliza a minúsculas y sera tu identificador de acceso.",
  "auth.validation.email.format": "Ingresa un correo electrónico válido.",
  "auth.validation.legalName.required": "Ingresa nombre y apellidos.",
  "auth.validation.displayName.required": "Ingresa un nombre para mostrar.",
  "auth.validation.password.containsUsername":
    "La contraseña no puede contener el correo electrónico.", // pragma: allowlist secret
  "auth.validation.password.length":
    "La contraseña debe tener al menos 8 caracteres.", // pragma: allowlist secret
  "auth.validation.password.lowercase":
    "La contraseña debe incluir al menos una letra minúscula.", // pragma: allowlist secret
  "auth.validation.password.number":
    "La contraseña debe incluir al menos un número.", // pragma: allowlist secret
  "auth.validation.password.uppercase":
    "La contraseña debe incluir al menos una letra mayúscula.", // pragma: allowlist secret
  "landing.brand": "Abogado Fácil",
  "landing.badge.portal": "Abogado Fácil",
  "landing.byok.body":
    "Cada usuario conecta su propia API key de OpenAI o Google Gemini. La plataforma no absorbe el costo variable de IA y el backend valida la configuración antes de cualquier llamada.",
  "landing.byok.title": "IA BYOK desde el MVP",
  "landing.cta.register": "Crear cuenta",
  "landing.cta.login": "Ir a login",
  "landing.hero.disclaimer":
    "La app organiza el trabajo del abogado; no automatiza envíos, presentaciones ni decisiones jurídicas.",
  "landing.hero.eyebrow": "SaaS legal ligero para despachos pequeños",
  "landing.legal.body":
    "Las respuestas generadas por IA son apoyo de redacción y organización. Deben ser revisadas por un profesional del derecho antes de utilizarse.",
  "landing.legal.title": "Revisión humana obligatoria",
  "landing.loading.title": "Cargando Abogado Fácil...",
  "landing.modules.ai.body":
    "Análisis de relatos, preguntas para cliente, mensajes y borradores simples solo cuando BYOK esté configurado.",
  "landing.modules.ai.title": "IA en flujos controlados",
  "landing.modules.calculators.body":
    "Estimaciones de adeudos, rentas, intereses, liquidación básica y honorarios sin depender de IA.",
  "landing.modules.calculators.title": "Calculadoras prácticas",
  "landing.modules.checklists.body":
    "Listas base por tipo de asunto para pedir documentos, marcar avances y detectar faltantes.",
  "landing.modules.checklists.title": "Checklists y pagos",
  "landing.modules.clients.body":
    "Clientes, asuntos, estados, contraparte, próxima acción y actividad clave en un solo lugar.",
  "landing.modules.clients.title": "Clientes y expedientes",
  "landing.modules.documents.body":
    "Notas, archivos PDF/DOCX/TXT, tareas y resultados guardados para consultar sin repetir trabajo.",
  "landing.modules.documents.title": "Notas y documentos",
  "landing.modules.drafts.body":
    "Plantillas para cartas, convenios y mensajes que siempre quedan como borradores editables.",
  "landing.modules.drafts.title": "Borradores revisables",
  "landing.modules.subtitle":
    "El MVP se concentra en los flujos diarios de abogados independientes: ordenar, dar seguimiento y preparar material revisable.",
  "landing.modules.title": "Módulos incluidos en el MVP",
  "landing.nav.label": "Navegación pública",
  "landing.preview.area": "Familiar básico",
  "landing.preview.byokBadge": "IA configurada",
  "landing.preview.checklist.first": "Acta de matrimonio",
  "landing.preview.checklist.second": "Comprobantes de ingresos",
  "landing.preview.checklist.third": "Domicilio de contraparte",
  "landing.preview.checklist.title": "Documentos faltantes",
  "landing.preview.client.label": "Cliente",
  "landing.preview.client.value": "María López",
  "landing.preview.label": "Vista previa de expediente organizado",
  "landing.preview.next.label": "Próxima acción",
  "landing.preview.next.value": "Pedir documentos",
  "landing.preview.status.label": "Estado",
  "landing.preview.status.value": "Activo",
  "landing.preview.timeline.first.body":
    "Relato inicial convertido en hechos relevantes.",
  "landing.preview.timeline.first.date": "10 jul",
  "landing.preview.timeline.second.body":
    "Preguntas pendientes listas para revisar con el cliente.",
  "landing.preview.timeline.second.date": "12 jul",
  "landing.preview.timeline.title": "Cronología sugerida",
  "landing.preview.title": "Expediente: Pensión alimenticia",
  "landing.subtitle":
    "Organiza clientes, expedientes, documentos, tareas, pagos y borradores con IA BYOK en flujos controlados.",
  "landing.title": "Abogado Fácil",
  "dashboard.actions": "Acciones rápidas",
  "dashboard.action.client": "Crear cliente",
  "dashboard.action.matter": "Crear asunto",
  "dashboard.action.intake": "Analizar relato inicial",
  "dashboard.ai": "Configuración de IA",
  "dashboard.ai.notAvailable": "La configuración de IA estará disponible en una próxima etapa.",
  "dashboard.available": "Disponible",
  "dashboard.badge": "Panel del despacho",
  "dashboard.clients": "Clientes",
  "dashboard.comingSoon": "Próximamente",
  "dashboard.error.body": "No fue posible cargar el resumen. Intenta nuevamente.",
  "dashboard.error.title": "No fue posible cargar el dashboard",
  "dashboard.firm": "Resumen de {firmName}",
  "dashboard.greeting": "Hola, {displayName}",
  "dashboard.loading": "Cargando resumen del despacho...",
  "dashboard.matters": "Asuntos activos",
  "dashboard.retry": "Reintentar",
  "dashboard.summary": "Resumen del despacho",
  "dashboard.tasks": "Tareas pendientes",
  "dashboard.upcoming": "Próximos pendientes",
  "dashboard.upcoming.empty": "Todavía no hay tareas o vencimientos disponibles.",
  "profile.actions.cancel": "Cancelar",
  "profile.badge": "Perfil",
  "profile.currentUser": "Sesion activa para {email}",
  "profile.error.generic":
    "No fue posible actualizar el perfil, intenta nuevamente.",
  "profile.fields.currentPassword": "Contraseña actual", // pragma: allowlist secret
  "profile.fields.newPassword": "Nueva contraseña", // pragma: allowlist secret
  "profile.fields.firstName": "Nombre",
  "profile.fields.middleName": "Segundo nombre",
  "profile.fields.lastName": "Apellidos",
  "profile.fields.displayName": "Nombre para mostrar",
  "profile.fields.email": "Correo electrónico",
  "profile.fields.firmName": "Despacho",
  "profile.password.optional":
    "Deja ambos campos de contraseña vacíos si solo cambiarás los datos del perfil.",
  "profile.submit.default": "Guardar perfil",
  "profile.submit.pending": "Guardando perfil...",
  "profile.subtitle":
    "Actualiza los datos de tu cuenta y, si lo necesitas, cambia tu contraseña.",
  "profile.success.body": "La sesión local ya refleja los cambios de {email}.",
  "profile.validation.names.required":
    "Nombre completo y despacho son obligatorios.",
  "profile.success.title": "Perfil actualizado",
  "profile.title": "Administra tu cuenta",
  "profile.validation.currentPassword.required":
    "Ingresa la contraseña actual para cambiar la contraseña.", // pragma: allowlist secret
  "profile.validation.newPassword.different":
    "La nueva contraseña debe ser diferente a la actual.", // pragma: allowlist secret
  "profile.validation.newPassword.required":
    "Ingresa la nueva contraseña para completar el cambio.", // pragma: allowlist secret
  "profile.validation.noChanges": "No hay cambios para guardar.",
  "routing.error.body": "No fue posible cargar esta ruta.",
  "routing.error.title": "Error de navegacion",
  "routing.notFound.body": "La ruta solicitada no existe.",
  "routing.notFound.title": "Pagina no encontrada",
  "routing.nav.admin.auditLog": "Audit Log",
  "routing.nav.admin.assignments": "Asignaciones",
  "routing.nav.admin.group": "Administrar",
  "routing.nav.admin.permissions": "Permisos",
  "routing.nav.admin.roles": "Roles",
  "routing.nav.admin.users": "Usuarios",
  "routing.nav.home": "Inicio",
  "routing.nav.menu.toggle": "Abrir menu de navegacion",
  "routing.nav.profile": "Perfil",
  "routing.logout": "Cerrar sesión",
  "routing.logout.pending": "Cerrando sesión...",
  "routing.protected.error.body":
    "Revisa la conexion con la API e intenta nuevamente.",
  "routing.protected.error.title": "No fue posible validar la sesión",
  "routing.protected.validating.body": "Espera un momento.",
  "routing.protected.validating.title": "Validando sesión...",
  "shared.centeredMessage.stateLabel": "Estado",
  "welcome.badge": "Bienvenida",
  "welcome.greeting": "Hola, {displayName}",
  "welcome.logout": "Cerrar sesión",
  "welcome.logout.pending": "Cerrando sesión...",
  "welcome.noSession.body": "Vuelve a iniciar sesión.",
  "welcome.noSession.title": "No hay sesión activa",
  "welcome.sessionActive.body":
    "Tu sesión esta activa y validada contra la API. Desde aquí puedes continuar al siguiente módulo.",
} as const;

export type UiTextKey = keyof typeof ES_MESSAGES;

const PARAM_PATTERN = /\{(\w+)\}/g;

export const t = (
  key: UiTextKey,
  params?: Record<string, string | number>,
): string => {
  const template = ES_MESSAGES[key];
  if (!params) {
    return template;
  }

  let resolvedText = template;
  for (const match of template.matchAll(PARAM_PATTERN)) {
    const [placeholder, paramName] = match;
    if (!paramName) {
      continue;
    }
    const value = params[paramName];
    if (value !== undefined) {
      resolvedText = resolvedText.replace(placeholder, String(value));
    }
  }

  return resolvedText;
};
