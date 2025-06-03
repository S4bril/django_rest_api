from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from fu_api.features.common.serializers.user_serializer import FullUserSerializer
from fu_api.models.custom_user_model import CustomUser


class UsersCreateView(CreateAPIView):
    serializer_class = FullUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
