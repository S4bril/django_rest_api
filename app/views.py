from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.decorators import action

from .models import CustomUser
from .serializers import CustomUserSerializer
from .permissions import IsOwnerOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        ids = self.request.query_params.getlist('ids')
        if ids:
            return CustomUser.objects.filter(id__in=ids)
        return super().get_queryset()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_ids(self, request):
        ids = request.query_params.getlist('ids')
        if not ids:
            return Response({"detail": "No IDs provided."}, status=400)

        users = CustomUser.objects.filter(id__in=ids)
        if not users.exists():
            return Response({"detail": "No users found for the given IDs."}, status=404)

        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"detail": "Invalid credentials"}, status=401)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            user_id = token["user_id"]
            token.blacklist()
            return Response({"detail": f"{CustomUser.objects.get(id=user_id)} logged out successfully"})
        except Exception as e:
            return Response({"detail": "Invalid token"}, status=400)
