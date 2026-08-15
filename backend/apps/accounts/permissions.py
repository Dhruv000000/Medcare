from rest_framework.permissions import BasePermission

from .models import User


class IsRole(BasePermission):
    allowed_roles = set()

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.role in self.allowed_roles
        )


class IsPatient(IsRole):
    allowed_roles = {User.Role.PATIENT}


class IsDoctor(IsRole):
    allowed_roles = {User.Role.DOCTOR}


class IsAdministrator(IsRole):
    allowed_roles = {User.Role.ADMINISTRATOR}
