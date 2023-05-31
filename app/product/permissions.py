from rest_framework import permissions
from account import RoleType


class ProductPermissions(permissions.DjangoModelPermissions):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        if request.user.role == RoleType.MANAGER or request.user.role == RoleType.DIRECTOR \
                or request.user.role == RoleType.CLIENT:
            return True
        return False

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.user.role == RoleType.MANAGER or request.user.role == RoleType.DIRECTOR \
                or request.user.role == RoleType.CLIENT:
            return True
        return False


class ProductPreviewPermissions(permissions.DjangoModelPermissions):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        if request.user.role == RoleType.MANAGER or request.user.role == RoleType.DIRECTOR:
            return True
        return False

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.user.role == RoleType.MANAGER or request.user.role == RoleType.DIRECTOR:
            return True
        return False


class CommentPermissions(permissions.DjangoModelPermissions):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE' and obj.user != request.user:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        if request.user.role == RoleType.CLIENT:
            return True
        return False

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.user.role == RoleType.MANAGER or request.user.role == RoleType.DIRECTOR \
                or request.user.role == RoleType.CLIENT:
            return True
        return False
