from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from fu_api.features.notifications.serializers import NotificationSerializer
from fu_api.models.notification_model import Notification


from rest_framework import generics, permissions, status


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_read=False).order_by("-created_at")


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(Notification,id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
