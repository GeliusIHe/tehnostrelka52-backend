from rest_framework import permissions

class IsOwnerOrIsSupportStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role.name == 'support':
            return True
        return obj.message.author == request.user
