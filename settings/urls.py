from django.urls import include, path

urlpatterns = [
    path("lab/", include("community.urls")),
    path("", include("cv.urls")),
]
