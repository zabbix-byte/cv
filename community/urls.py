from django.urls import path

from community.views import github_builder, github_svg, lab_home

urlpatterns = [
    path("", lab_home, name="lab_home"),
    path("github/", github_builder, name="lab_github"),
    path("github.svg", github_svg, name="lab_github_svg"),
]
