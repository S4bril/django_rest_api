from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from fu_api.features.common.serializers.location_serializer import LocationSerializer
from fu_api.features.common.serializers.user_serializer import FullUserSerializer


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
