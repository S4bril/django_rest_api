from rest_framework_simplejwt.views import TokenObtainPairView

from fu_api.features.token.serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
