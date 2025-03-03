from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import (
    path, 
    include
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView, 
    TokenObtainPairView
)
from fu_api.views import (
    UserViewSet,
    EventViewSet,
    GetFormView,
    UserDetailView,
    UserCreateView,
    UserFriendsListView
)

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('api/user/', UserDetailView.as_view()),
    path('api/user/create/', UserCreateView.as_view()),
    path('api/user/friends/', UserFriendsListView.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/form/", GetFormView.as_view(), name="get_form"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
