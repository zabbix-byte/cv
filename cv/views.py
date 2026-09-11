from pathlib import Path
import json
import logging

from django.conf import settings
from django.db.models import Sum, Count
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cv.models import PageView, VisitSession
from services.geo import lookup_ip
from services.github_service import GitHubService
from services.pdf_service import generate_cv_pdf_response

logger = logging.getLogger(__name__)


def _static_file_response(name, content_type):
    path = Path(settings.BASE_DIR) / "static" / name
    if not path.exists():
        raise Http404
    return FileResponse(path.open("rb"), content_type=content_type)


def robots_txt(request):
    return _static_file_response("robots.txt", "text/plain")


def sitemap_xml(request):
    return _static_file_response("sitemap.xml", "application/xml")


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


def press(request):
    return render(request, "pages/press.html")


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
            "title": "Co-founder &amp; CTO · Valerdat",
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


SKIP_TRACK_PREFIXES = (
    "/statistics",
    "/api/track",
    "/download-cv",
    "/robots.txt",
    "/sitemap.xml",
)


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or ""


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


@csrf_exempt
@require_POST
def track_visit(request):
    payload = _json_body(request)
    action = payload.get("action") or "start"
    path = (payload.get("path") or "/")[:255]
    if any(path.startswith(prefix) for prefix in SKIP_TRACK_PREFIXES):
        return JsonResponse({"ok": True, "ignored": True})

    sid = (payload.get("sid") or "")[:64]
    if not sid:
        return JsonResponse({"ok": False}, status=400)

    ip = _client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "")[:500]
    geo = lookup_ip(ip)
    session, created = VisitSession.objects.get_or_create(
        sid=sid,
        defaults={
            "ip": ip or "0.0.0.0",
            "user_agent": ua,
            **geo,
        },
    )
    if not created:
        session.ip = ip or session.ip
        session.user_agent = ua or session.user_agent
        if geo.get("lat") is not None or geo.get("country"):
            session.country = geo["country"] or session.country
            session.city = geo["city"] or session.city
            session.region = geo["region"] or session.region
            session.lat = geo["lat"] if geo.get("lat") is not None else session.lat
            session.lon = geo["lon"] if geo.get("lon") is not None else session.lon
        session.save()

    if action == "ping":
        view_id = payload.get("id")
        try:
            seconds = min(int(payload.get("seconds") or 0), 60 * 60 * 6)
        except (TypeError, ValueError):
            seconds = 0
        updated = PageView.objects.filter(id=view_id, session=session).update(
            seconds=seconds
        )
        session.save(update_fields=["last_seen"])
        return JsonResponse({"ok": True, "updated": bool(updated)})

    view = PageView.objects.create(
        session=session,
        path=path,
        title=(payload.get("title") or "")[:255],
        referrer=(payload.get("referrer") or "")[:500],
    )
    return JsonResponse({"ok": True, "id": view.id})


def _stats_unlocked(request):
    token = getattr(settings, "STATS_TOKEN", "") or ""
    if request.session.get("stats_ok") is True:
        return True
    if token and request.GET.get("k") == token:
        request.session["stats_ok"] = True
        return True
    if settings.DEBUG and not token:
        return True
    return False


def _fmt_duration(seconds):
    seconds = int(seconds or 0)
    if seconds < 60:
        return f"{seconds}s"
    minutes, rem = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {rem}s" if rem else f"{minutes}m"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m"


def statistics(request):
    token = getattr(settings, "STATS_TOKEN", "") or ""
    if request.method == "POST":
        submitted = request.POST.get("token", "")
        if token and submitted == token:
            request.session["stats_ok"] = True
            return render(request, "pages/statistics.html", _stats_context())
        return render(request, "pages/statistics_gate.html", {"error": True})

    if not _stats_unlocked(request):
        return render(request, "pages/statistics_gate.html", {"error": False})

    return render(request, "pages/statistics.html", _stats_context())


def _stats_context():
    sessions = VisitSession.objects.annotate(
        view_count=Count("views"),
        dwell=Sum("views__seconds"),
    )
    views = PageView.objects.select_related("session")
    total_seconds = views.aggregate(s=Sum("seconds"))["s"] or 0
    pages = [
        {
            "path": row["path"],
            "hits": row["hits"],
            "time": _fmt_duration(row["dwell"]),
        }
        for row in views.values("path")
        .annotate(hits=Count("id"), dwell=Sum("seconds"))
        .order_by("-hits")[:12]
    ]
    countries = list(
        sessions.exclude(country="")
        .values("country")
        .annotate(n=Count("id"))
        .order_by("-n")[:8]
    )
    recent = []
    for view in views[:40]:
        place = ", ".join(
            p for p in (view.session.city, view.session.country) if p
        ) or "Unknown"
        recent.append(
            {
                "path": view.path,
                "ip": view.session.ip,
                "place": place,
                "time": _fmt_duration(view.seconds),
                "when": timezone.localtime(view.started_at).strftime("%d %b %H:%M"),
            }
        )
    grouped = {}
    for session in sessions.exclude(lat__isnull=True).exclude(lon__isnull=True):
        key = (round(session.lat, 3), round(session.lon, 3))
        bucket = grouped.setdefault(
            key,
            {
                "lat": session.lat,
                "lon": session.lon,
                "city": session.city,
                "country": session.country,
                "visitors": 0,
                "seconds": 0,
            },
        )
        bucket["visitors"] += 1
        bucket["seconds"] += session.dwell or 0
    map_points = [
        {**point, "time": _fmt_duration(point.pop("seconds"))}
        for point in grouped.values()
    ]
    return {
        "total_sessions": sessions.count(),
        "total_views": views.count(),
        "total_time": _fmt_duration(total_seconds),
        "pages": pages,
        "countries": countries,
        "recent": recent,
        "map_points": map_points,
    }
