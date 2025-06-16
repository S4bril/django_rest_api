from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from fu_api.features.forms.views import FormRetrieveView
from fu_api.features.messages.views import (
    CheckIfExistsUnreadMessage,
    MarkMessageAsReadView,
    MessageListCreateView,
)
from fu_api.features.notifications.views import (
    MarkNotificationReadView,
    NotificationListView,
)
from fu_api.features.private_chat_room.views import (
    ChatRoomCreateView,
    ChatRoomListView,
)
from fu_api.features.suggested_friends.views import (
    MatchesListView,
    NearYouListView,
    RecentLikesListView,
    UserLikeCreateView,
    UserRejectView,
    UserSuggestedFriendsRetrieveView,
)
from fu_api.features.token.views import CustomTokenObtainPairView
from fu_api.features.user_block.views import BlockUserView
from fu_api.features.user_profile.views import (
    ChangePasswordView,
    UserDetailView,
    UserLocationDetailView,
)
from fu_api.features.users.views import UsersCreateView

urlpatterns = [
    path("api/users/", UsersCreateView.as_view()),
    path("api/users/<int:user_id>/block/", BlockUserView.as_view(), name="block-user"),
    path("api/me/", UserDetailView.as_view()),
    path("api/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("api/me/location/", UserLocationDetailView.as_view()),
    path("api/suggested-friends/", UserSuggestedFriendsRetrieveView.as_view()),
    path("api/suggested-friends/reject/<int:pk>/", UserRejectView.as_view()),
    path("api/suggested-friends/like/<int:pk>/", UserLikeCreateView.as_view()),
    path("api/suggested-friends/recent-likes/", RecentLikesListView.as_view()),
    path("api/suggested-friends/matches/", MatchesListView.as_view()),
    path("api/suggested-friends/near-you/", NearYouListView.as_view()),
    path("api/private-chat/<int:pk>/", ChatRoomCreateView.as_view()),
    path("api/private-chat/", ChatRoomListView.as_view()),
    path("api/private-chat/unread-exists/", CheckIfExistsUnreadMessage.as_view()),
    path(
        "api/private-chat/<int:chat_room_id>/messages/", MessageListCreateView.as_view()
    ),
    path("api/mark-msg-read/<int:message_id>/", MarkMessageAsReadView.as_view()),
    path(
        "api/notifications/", NotificationListView.as_view(), name="notification-list"
    ),
    path(
        "api/notifications/<int:notification_id>/read/",
        MarkNotificationReadView.as_view(),
        name="mark-notification-read",
    ),
    path("api/token/", CustomTokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path("api/form/", FormRetrieveView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
