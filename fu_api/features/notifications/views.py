from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from fu_api.features.common.services.new_since_filter_service import (
    NewSinceFilterService,
)
from fu_api.features.notifications.serializers import NotificationSerializer
from fu_api.models.notification_model import Notification


class NotificationListView(APIView):
    serializer = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Notification.objects.filter(user=request.user)
        result = NewSinceFilterService.filter(request, queryset)

        serializer = self.serializer(result, many=True)
        return Response({"notifications": serializer.data})


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(
            Notification, id=notification_id, user=request.user
        )
        notification.is_read = True
        notification.save()
        return Response(
            {"message": "Notification marked as read"}, status=status.HTTP_200_OK
        )
