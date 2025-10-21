from enum import Enum


class Permission(str, Enum):
    # Product permissions
    PRODUCT_READ = "product:read"
    PRODUCT_WRITE = "product:write"
    PRODUCT_DELETE = "product:delete"

    # Section permissions
    SECTION_READ = "section:read"
    SECTION_WRITE = "section:write"
    SECTION_DELETE = "section:delete"

    # Laboratory permissions
    LABORATORY_READ = "laboratory:read"
    LABORATORY_WRITE = "laboratory:write"
    LABORATORY_DELETE = "laboratory:delete"

    # Alert permissions
    ALERT_READ = "alert:read"
    ALERT_WRITE = "alert:write"
    ALERT_DELETE = "alert:delete"

    # User management permissions
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"

    # Role management permissions
    ROLE_READ = "role:read"
    ROLE_WRITE = "role:write"
    ROLE_DELETE = "role:delete"

    # Inventory permissions
    INVENTORY_READ = "inventory:read"
    INVENTORY_WRITE = "inventory:write"
    INVENTORY_DELETE = "inventory:delete"

    # Admin permissions
    ADMIN_ACCESS = "admin:access"
    SYSTEM_CONFIG = "system:config"


class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"


# Role-based permissions mapping
ROLE_PERMISSIONS: dict[str, list[str]] = {
    # Use string keys (e.g., "admin", "manager") for compatibility with stored role names
    Role.ADMIN.value: [
        # All permissions for admin
        Permission.PRODUCT_READ,
        Permission.PRODUCT_WRITE,
        Permission.PRODUCT_DELETE,
        Permission.SECTION_READ,
        Permission.SECTION_WRITE,
        Permission.SECTION_DELETE,
        Permission.LABORATORY_READ,
        Permission.LABORATORY_WRITE,
        Permission.LABORATORY_DELETE,
        Permission.ALERT_READ,
        Permission.ALERT_WRITE,
        Permission.ALERT_DELETE,
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.ROLE_READ,
        Permission.ROLE_WRITE,
        Permission.ROLE_DELETE,
        Permission.INVENTORY_READ,
        Permission.INVENTORY_WRITE,
        Permission.INVENTORY_DELETE,
        Permission.ADMIN_ACCESS,
        Permission.SYSTEM_CONFIG,
    ],
    Role.MANAGER.value: [
        # Manager permissions
        Permission.PRODUCT_READ,
        Permission.PRODUCT_WRITE,
        Permission.SECTION_READ,
        Permission.SECTION_WRITE,
        Permission.LABORATORY_READ,
        Permission.LABORATORY_WRITE,
        Permission.ALERT_READ,
        Permission.ALERT_WRITE,
        Permission.USER_READ,
        Permission.INVENTORY_READ,
        Permission.INVENTORY_WRITE,
    ],
    Role.USER.value: [
        # Basic user permissions
        Permission.PRODUCT_READ,
        Permission.PRODUCT_WRITE,
        Permission.SECTION_READ,
        Permission.LABORATORY_READ,
        Permission.ALERT_READ,
        Permission.INVENTORY_READ,
    ],
    Role.VIEWER.value: [
        # Read-only permissions
        Permission.PRODUCT_READ,
        Permission.SECTION_READ,
        Permission.LABORATORY_READ,
        Permission.ALERT_READ,
        Permission.INVENTORY_READ,
    ],
}


def get_role_permissions(role_name: str) -> list[str]:
    """Get permissions for a specific role"""
    return ROLE_PERMISSIONS.get(role_name, [])


def has_permission(user_permissions: list[str], required_permission: str) -> bool:
    """Check if user has a specific permission"""
    return required_permission in user_permissions


def has_any_permission(user_permissions: list[str], required_permissions: list[str]) -> bool:
    """Check if user has any of the required permissions"""
    return any(perm in user_permissions for perm in required_permissions)


def has_all_permissions(user_permissions: list[str], required_permissions: list[str]) -> bool:
    """Check if user has all required permissions"""
    return all(perm in user_permissions for perm in required_permissions)


# Default roles data for seeding
DEFAULT_ROLES = [
    {
        "nombre_rol": Role.ADMIN.value,
        "descripcion": "Administrator with full access",
        "permisos": ",".join([p.value for p in get_role_permissions(Role.ADMIN.value)]),
    },
    {
        "nombre_rol": Role.MANAGER.value,
        "descripcion": "Manager with read/write access",
        "permisos": ",".join([p.value for p in get_role_permissions(Role.MANAGER.value)]),
    },
    {
        "nombre_rol": Role.USER.value,
        "descripcion": "User with basic access",
        "permisos": ",".join([p.value for p in get_role_permissions(Role.USER.value)]),
    },
    {
        "nombre_rol": Role.VIEWER.value,
        "descripcion": "Viewer with read-only access",
        "permisos": ",".join([p.value for p in get_role_permissions(Role.VIEWER.value)]),
    },
]
