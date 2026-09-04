from app.authorization.dependencies import require_roles

ADMIN_ONLY = require_roles("ADMIN")
STAFF_ROLES = require_roles("ADMIN", "STAFF")
