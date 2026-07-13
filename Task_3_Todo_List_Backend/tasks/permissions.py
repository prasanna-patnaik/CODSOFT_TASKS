from rest_framework import permissions


class IsTaskOwner(permissions.BasePermission):
    message = "You do not have permission to access this task."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and obj.owner_id == request.user.id)
