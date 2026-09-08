from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    message = 'Your role does not have permission to perform this action.'

    def has_permission(self, request, view):
        allowed_roles = getattr(view, 'allowed_roles', None)
        if not allowed_roles:
            return True
        role_name = (getattr(getattr(request.user, 'role', None), 'name', '') or '').upper()
        if 'CASHIER' in role_name:
            role_name = 'CASHIER'
        if isinstance(allowed_roles, dict):
            allowed_roles = allowed_roles.get('read' if request.method in ('GET', 'HEAD', 'OPTIONS') else 'write', set())
        return role_name in allowed_roles