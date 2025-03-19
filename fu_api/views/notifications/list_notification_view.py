from rest_framework import generics
from rest_framework import permissions
from fu_api.models.notification_model import Notification
from fu_api.serializers.notofication_serializer import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_read=False).order_by("-created_at")
