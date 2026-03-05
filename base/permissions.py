from rest_framework.permissions import BasePermission


class IsPremiumUser(BasePermission):
    """Allows access to authenticated premium users (and admins)."""

    message = "Premium subscription required to access full exercise details."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_staff:
            return True

        profile = getattr(user, "profile", None)
        return bool(profile and profile.is_premium)
