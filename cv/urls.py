from django.urls import path
from .views import home, github_data_api, download_cv_pdf

urlpatterns = [
    path('', home, name='home'),
    path('api/github-data/', github_data_api, name='github_data_api'),
    path('download-cv/', download_cv_pdf, name='download_cv_pdf'),
]
