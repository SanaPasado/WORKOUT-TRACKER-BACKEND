from rest_framework.permissions import BasePermission

from .models import UserProfile


class IsPremiumUserOrAdmin(BasePermission):
    message = "Premium membership is required to view full exercise details."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_staff:
            return True

        return UserProfile.objects.filter(user=user, is_premium=True).exists()