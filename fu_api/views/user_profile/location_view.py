from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from fu_api.serializers.location_serializer import LocationSerializer


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
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return super().update(request, *args, **kwargs)