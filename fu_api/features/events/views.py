from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from fu_api.core.permissions import IsOwnerOfEvent, IsOwnerOrReadOnly
from fu_api.features.common.serializers.location_serializer import LocationSerializer
from fu_api.models.event_model import Event
from fu_api.features.events.serializers import EventSerializer


class EventsDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOfEvent]


class EventsListCreateView(ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


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
