from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class IsOwnerOrReadOnly(permissions.BasePermission):
    # def has_permission(self, request, view):
    #     jwt_authenticator = JWTAuthentication()
    #     try:
    #         authentication_result = jwt_authenticator.authenticate(request)
    #         if authentication_result is None:
    #             return False
    #         user, _ = authentication_result
    #         request.user = user
    #         return True
    #     except AuthenticationFailed:
    #         return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user