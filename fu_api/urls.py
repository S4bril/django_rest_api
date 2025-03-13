from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView, 
    TokenObtainPairView
)
from fu_api.views.events.location_view import EventLocationDetailView
from fu_api.views.events.event_views import EventsDetailView, EventsListCreateView
from fu_api.views.forms.form_view import FormRetrieveView
from fu_api.views.friend_request.friend_request_views import FriendRequestAcceptView, FriendRequestListCreateView, FriendRequestRejectView, SentFriendRequestListView
from fu_api.views.suggested_friends.suggested_friends_view import UserSuggestedFriendsRetrieveView
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
    path('api/me/friends/<int:pk>/remove/', RemoveFriendView.as_view(), name='remove_friend'),
    path('api/me/location/', UserLocationDetailView.as_view()),
    path('api/me/suggested-friends/', UserSuggestedFriendsRetrieveView.as_view()),

    path('api/friend-requests/', FriendRequestListCreateView.as_view()),
    path('api/friend-requests/sent/', SentFriendRequestListView.as_view()),
    path('api/friend-requests/<int:pk>/accept/', FriendRequestAcceptView.as_view()),
    path('api/friend-requests/<int:pk>/reject/', FriendRequestRejectView.as_view()),

    path('api/events/', EventsListCreateView.as_view()),
    path('api/events/<int:pk>/', EventsDetailView.as_view()),
    path('api/events/<int:pk>/location/', EventLocationDetailView.as_view()),

    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    path("api/form/", FormRetrieveView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
