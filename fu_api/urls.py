from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView, 
    TokenObtainPairView
)
from fu_api.views.friend_request.views import FriendRequestAcceptView, FriendRequestListCreateView, FriendRequestRejectView
from fu_api.views.views import (
    EventLocationDetailView,
    EventsListCreateView,
    EventsDetailView,
    FormRetrieveView,
    UsersListCreateView,
    UsersRetrieveView,
    UserDetailView,
    UserFriendsListView,
    UserLocationDetailView,
    UserSuggestedFriendsRetrieveView
)


urlpatterns = [
    path('api/users/', UsersListCreateView.as_view()),
    path('api/users/<int:pk>/', UsersRetrieveView.as_view()),

    path('api/me/', UserDetailView.as_view()),
    path('api/me/friends/', UserFriendsListView.as_view()),
    path('api/me/location/', UserLocationDetailView.as_view()),
    path('api/me/suggested-friends/', UserSuggestedFriendsRetrieveView.as_view()),
    path('api/me/friend-requests/', FriendRequestListCreateView.as_view()),
    path('api/me/friend-requests/<int:pk>/accept/', FriendRequestAcceptView.as_view()),
    path('api/me/friend-requests/<int:pk>/reject/', FriendRequestRejectView.as_view()),

    path('api/events/', EventsListCreateView.as_view()),
    path('api/events/<int:pk>/', EventsDetailView.as_view()),
    path('api/events/<int:pk>/location/', EventLocationDetailView.as_view()),

    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    path("api/form/", FormRetrieveView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
