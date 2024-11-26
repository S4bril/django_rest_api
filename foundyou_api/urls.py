from django.urls import path, include

urlpatterns = [
    path('', include('app.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
