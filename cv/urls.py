from django.urls import path
from .views import home, github_data_api

urlpatterns = [
    path('', home, name='home'),
    path('api/github-data/', github_data_api, name='github_data_api'),
]
