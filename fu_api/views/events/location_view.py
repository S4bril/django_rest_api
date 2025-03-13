from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from fu_api.models.event_model import Event
from fu_api.permissions import IsOwnerOrReadOnly
from fu_api.serializers.location_serializer import LocationSerializer


class EventLocationDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_event(self):
        return get_object_or_404(Event, pk=self.kwargs['pk'])

    def get_object(self):
        event = self.get_event()
        return event.location

    def update(self, request, *args, **kwargs):
        event = self.get_event()

        if event.location is None:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            location = serializer.save()
            event.location = location
            event.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return super().update(request, *args, **kwargs)