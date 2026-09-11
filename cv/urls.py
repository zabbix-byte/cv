from django.urls import path
from .views import (
    home,
    experience,
    projects,
    research,
    skills,
    education,
    press,
    github_data_api,
    download_cv_pdf,
    robots_txt,
    sitemap_xml,
    track_visit,
    statistics,
)

urlpatterns = [
    path("", home, name="home"),
    path("experience/", experience, name="experience"),
    path("projects/", projects, name="projects"),
    path("research/", research, name="research"),
    path("skills/", skills, name="skills"),
    path("education/", education, name="education"),
    path("press/", press, name="press"),
    path("statistics/", statistics, name="statistics"),
    path("api/github-data/", github_data_api, name="github_data_api"),
    path("api/track/", track_visit, name="track_visit"),
    path("download-cv/", download_cv_pdf, name="download_cv_pdf"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
]
