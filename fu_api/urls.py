from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView, 
    TokenObtainPairView
)
from fu_api.views.messages.chat_members_view import ChatRoomMembersView
from fu_api.views.messages.add_member_view import AddMemberView
from fu_api.views.messages.remove_member_view import RemoveMemberView
from fu_api.views.messages.chat_view import ChatRoomListCreateView
from fu_api.views.messages.message_view import MessageListCreateView
from fu_api.views.events.location_view import EventLocationDetailView
from fu_api.views.events.event_views import EventsDetailView, EventsListCreateView
from fu_api.views.forms.form_view import FormRetrieveView
from fu_api.views.friend_request.friend_request_views import FriendRequestListCreateView, FriendRequestUpdateView, SentFriendRequestListView
from fu_api.views.notifications.list_notification_view import NotificationListView
from fu_api.views.notifications.mark_notification_read_view import MarkNotificationReadView
from fu_api.views.suggested_friends.suggested_friends_view import UserSuggestedFriendsRetrieveView
from fu_api.views.user_block.blocking_view import BlockUserView
from fu_api.views.user_profile.friends_views import RemoveFriendView, UserFriendsListView
from fu_api.views.user_profile.profile_managment_view import UserDetailView
from fu_api.views.users.users_views import UsersListCreateView, UsersRetrieveView
from fu_api.views.user_profile.location_view import (
    UserLocationDetailView
)


urlpatterns = [
    path('api/users/', UsersListCreateView.as_view()),
    path('api/users/<int:pk>/', UsersRetrieveView.as_view()),

    path('api/me/', UserDetailView.as_view()),
    path('api/me/friends/', UserFriendsListView.as_view()),
    path('api/me/friends/<int:pk>/remove/', RemoveFriendView.as_view()),
    path('api/me/location/', UserLocationDetailView.as_view()),
    path('api/me/suggested-friends/', UserSuggestedFriendsRetrieveView.as_view()),

    path('api/friend-requests/', FriendRequestListCreateView.as_view()),
    path('api/friend-requests/sent/', SentFriendRequestListView.as_view()),
    path('api/friend-requests/<int:pk>/', FriendRequestUpdateView.as_view()),

    path('api/chats/', ChatRoomListCreateView.as_view()),
    path('api/chats/<int:chat_room_id>/members/', ChatRoomMembersView.as_view()),
    path('api/chats/<int:chat_room_id>/messages/', MessageListCreateView.as_view()),
    path('api/chats/<int:chat_room_id>/add-member/', AddMemberView.as_view()),
    path('api/chats/<int:chat_room_id>/delete-member/', RemoveMemberView.as_view()),

    path("api/notifications/", NotificationListView.as_view(), name="notification-list"),
    path("api/notifications/<int:notification_id>/read/", MarkNotificationReadView.as_view(), name="mark-notification-read"),

    path('users/<int:user_id>/block/', BlockUserView.as_view(), name='block-user'),

    path('api/events/', EventsListCreateView.as_view()),
    path('api/events/<int:pk>/', EventsDetailView.as_view()),
    path('api/events/<int:pk>/location/', EventLocationDetailView.as_view()),

    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    path("api/form/", FormRetrieveView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
