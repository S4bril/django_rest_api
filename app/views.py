from rest_framework import viewsets

from .models import CustomUser
from .serializers import CustomUserSerializer
from .permissions import IsOwnerOrReadOnly

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsOwnerOrReadOnly]

