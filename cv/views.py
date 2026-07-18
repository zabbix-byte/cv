from django.shortcuts import render
from django.http import JsonResponse
from services.github_service import GitHubService
from services.pdf_service import generate_cv_pdf_response
import logging

logger = logging.getLogger(__name__)


def home(request):
    return render(request, "pages/home.html")


def experience(request):
    return render(request, "pages/experience.html")


def projects(request):
    return render(request, "pages/projects.html")


def research(request):
    return render(request, "pages/research.html")


def skills(request):
    return render(request, "pages/skills.html")


def education(request):
    return render(request, "pages/education.html")


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
        context = {
            "name": "Vasile Ovidiu Ichim",
            "title": "Staff Engineer &amp; Technical Lead · Software Architect",
            "location": "Barcelona, Spain",
            "email": "zabbix@ztrunk.space",
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
