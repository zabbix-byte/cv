from django.shortcuts import render
from django.http import JsonResponse
from services.github_service import GitHubService
from services.pdf_service import generate_cv_pdf_response
import logging

logger = logging.getLogger(__name__)


def home(request):
    """Home view with GitHub integration"""
    # Initialize GitHub service
    github_service = GitHubService(username="zabbix-byte")

    try:
        # Get comprehensive GitHub data
        github_data = github_service.get_comprehensive_stats()

        context = {
            "github_profile": github_data.get("profile", {}),
            "github_repositories": github_data.get("repositories", [])[
                :6
            ],  # Top 6 repos
            "github_languages": github_data.get("languages", [])[:5],  # Top 5 languages
            "github_recent_activity": github_data.get("recent_activity", [])[
                :5
            ],  # Last 5 activities
            "github_stats": github_data.get("stats", {}),
            "debug": True,  # Enable debug info
        }

        logger.info(f"Successfully fetched GitHub data for zabbix-byte")

    except Exception as e:
        logger.error(f"Error fetching GitHub data: {str(e)}")

        # Fallback context with empty data
        context = {
            "github_profile": {
                "login": "zabbix-byte",
                "name": "Vasile Ovidiu Ichim",
                "bio": "CTO & Co-founder at Valerdat building AI-powered purchasing assistant",
                "location": "Barcelona, Spain",
                "public_repos": 0,
                "followers": 0,
                "following": 0,
                "html_url": "https://github.com/zabbix-byte",
            },
            "github_repositories": [],
            "github_languages": [],
            "github_recent_activity": [],
            "github_stats": {
                "total_repos": 0,
                "total_stars": 0,
                "total_forks": 0,
                "followers": 0,
                "following": 0,
            },
        }

    return render(request, "home/home.html", context)


def github_data_api(request):
    """API endpoint to fetch fresh GitHub data (for AJAX updates)"""
    if request.method == "GET":
        github_service = GitHubService(username="zabbix-byte")

        try:
            github_data = github_service.get_comprehensive_stats()
            return JsonResponse({"success": True, "data": github_data})
        except Exception as e:
            logger.error(f"API Error fetching GitHub data: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


def download_cv_pdf(request):
    """Generate and download CV as PDF"""
    try:
        # Get the same context data as home view for consistency
        github_service = GitHubService(username="zabbix-byte")
        github_data = github_service.get_comprehensive_stats()

        context = {
            "github_profile": github_data.get("profile", {}),
            "github_repositories": github_data.get("repositories", []),
            "github_languages": github_data.get("languages", []),
            "github_stats": github_data.get("stats", {}),
            "name": "Vasile Ovidiu Ichim",
            "title": "CTO & Co-founder de Valerdat",
            "location": "Barcelona, Spain",
            "email": "contact@ztrunk.space",
            "github_url": "https://github.com/zabbix-byte",
            "linkedin_url": "https://linkedin.com/in/zabbix-byte",
        }

        logger.info("Generating CV PDF for download")
        return generate_cv_pdf_response(context)

    except Exception as e:
        logger.error(f"Error generating CV PDF: {str(e)}")
        return JsonResponse(
            {"error": "Failed to generate PDF", "message": str(e)}, status=500
        )
