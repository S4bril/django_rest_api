from django.urls import include, path

urlpatterns = [
    path("", include("fu_api.urls")),
]
