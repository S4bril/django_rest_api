from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from fu_api.features.common.serializers.location_serializer import LocationSerializer
from fu_api.features.common.serializers.user_serializer import FullUserSerializer
from fu_api.features.user_profile.serializers import ChangePasswordSerializer


class UserDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = FullUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserLocationDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.location

    def update(self, request, *args, **kwargs):
        user = self.request.user

        if user.location is None:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            location = serializer.save()
            user.location = location
            user.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            return super().update(request, *args, **kwargs)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]

            if not user.check_password(old_password):
                return Response(
                    {"old_password": "Nieprawidłowe hasło."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()

            return Response(
                {"detail": "Hasło zostało pomyślnie zmienione."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
