from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from app import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('fu/', include(router.urls)),
    path('fu/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('fu/login/', views.LoginView.as_view(), name='login'),
    path('fu/logout/', views.LogoutView.as_view(), name='logout')
]