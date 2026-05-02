from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "super_admin")


class IsTechnicalOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ["super_admin", "technical_admin"]
        )


class IsAuthenticatedAndReadOnlyForEmployee(BasePermission):
    """
    Employee: read-only
    Technical admin + super admin: full CRUD
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if request.method in SAFE_METHODS:
            return True

        return user.role in ["super_admin", "technical_admin"]
