from rest_framework import permissions


class IsTaskOwner(permissions.BasePermission):
    message = "You do not have permission to access this task."

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
