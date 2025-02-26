from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from fu_api import views

router = DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')
router.register(r'events', views.EventViewSet, basename='event')

urlpatterns = [
    path('fu/', include(router.urls)),
    path('fu/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('fu/login/', views.LoginView.as_view(), name='login'),
    path('fu/logout/', views.LogoutView.as_view(), name='logout'),
    path("fu/get-form/", views.GetFormView.as_view(), name="get_form"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
