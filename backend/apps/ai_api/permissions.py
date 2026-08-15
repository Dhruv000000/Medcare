from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsAiInferenceUser(BasePermission):
    """Allow only active doctors and administrators for the academic endpoint.

    Patients are denied because Phase 18 does not authorize patient-facing
    self-assessment and the frontend is intentionally not integrated.
    """

    allowed_roles = {User.Role.DOCTOR, User.Role.ADMINISTRATOR}

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and user.role in self.allowed_roles
        )
