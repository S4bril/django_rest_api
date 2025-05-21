from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from fu_api.features.user_profile.serializers import CustomUserSerializer
from fu_api.models.custom_user_model import CustomUser


class UsersListCreateView(ListCreateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]


class UsersRetrieveView(RetrieveAPIView):
    serializer_class = FriendSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
