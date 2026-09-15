from collections import Counter
from pathlib import Path
import json
import logging

from django.conf import settings
from django.db.models import Sum, Count
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from cv.models import PageView, VisitSession
from services.geo import lookup_ip
from services.github_card import render_github_card
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


@require_GET
def github_card_svg(request):
    theme = request.GET.get("theme", "light")
    if theme not in ("light", "dark"):
        theme = "light"
    try:
        metrics = GitHubService(username="zabbix-byte").get_card_metrics()
    except Exception as exc:
        logger.error("GitHub card metrics failed: %s", exc)
        metrics = {"years_coding": 13}
    svg = render_github_card(theme, metrics)
    response = HttpResponse(svg, content_type="image/svg+xml; charset=utf-8")
    response["Cache-Control"] = "public, max-age=300"
    return response


def github_widget(request):
    markdown = (
        '<div align="center">\n'
        '<a href="https://ztrunk.space/">\n'
        "  <picture>\n"
        '    <source media="(prefers-color-scheme: dark)" '
        'srcset="https://ztrunk.space/github.svg?theme=dark&v=3">\n'
        '    <img alt="Vasile Ovidiu Ichim — GitHub profile" '
        'src="https://ztrunk.space/github.svg?theme=light&v=3" width="880">\n'
        "  </picture>\n"
        "</a>\n"
        "</div>"
    )
    return render(
        request,
        "pages/github_widget.html",
        {"embed_code": markdown},
    )


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
    "/github",
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


def _clip(value, n):
    if value is None:
        return ""
    return str(value)[:n]


def _parse_ua(ua):
    raw = ua or ""
    low = raw.lower()
    device = "Desktop"
    if "ipad" in low or "tablet" in low:
        device = "Tablet"
    elif "mobi" in low or "iphone" in low or ("android" in low and "mobile" in low):
        device = "Mobile"

    os_name = "Unknown"
    if "windows" in low:
        os_name = "Windows"
    elif "iphone" in low or "ipad" in low:
        os_name = "iOS"
    elif "mac os" in low or "macintosh" in low:
        os_name = "macOS"
    elif "android" in low:
        os_name = "Android"
    elif "linux" in low:
        os_name = "Linux"

    browser = "Unknown"
    if "edg/" in low:
        browser = "Edge"
    elif "opr/" in low or "opera" in low:
        browser = "Opera"
    elif "chrome" in low and "chromium" not in low and "edg/" not in low:
        browser = "Chrome"
    elif "safari" in low and "chrome" not in low:
        browser = "Safari"
    elif "firefox" in low:
        browser = "Firefox"
    return browser, os_name, device


def _num(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _apply_session_fields(session, request, payload, geo, created):
    ua = request.META.get("HTTP_USER_AGENT", "")[:800]
    browser, os_name, device = _parse_ua(ua)
    lang_header = (request.META.get("HTTP_ACCEPT_LANGUAGE") or "").split(",")[0]
    updates = {
        "ip": _client_ip(request) or session.ip,
        "user_agent": ua or session.user_agent,
        "browser": browser if browser != "Unknown" else session.browser,
        "os": os_name if os_name != "Unknown" else session.os,
        "device": device,
        "language": _clip(payload.get("language") or lang_header, 40) or session.language,
        "timezone_client": _clip(payload.get("tz"), 64) or session.timezone_client,
        "screen": _clip(payload.get("screen"), 24) or session.screen,
        "viewport": _clip(payload.get("viewport"), 24) or session.viewport,
        "platform": _clip(payload.get("platform"), 80) or session.platform,
        "color_scheme": _clip(payload.get("color_scheme"), 12) or session.color_scheme,
        "connection_effective": _clip(payload.get("conn"), 20) or session.connection_effective,
        "utm_source": _clip(payload.get("utm_source"), 80) or session.utm_source,
        "utm_medium": _clip(payload.get("utm_medium"), 80) or session.utm_medium,
        "utm_campaign": _clip(payload.get("utm_campaign"), 80) or session.utm_campaign,
    }
    if payload.get("dpr") is not None:
        updates["pixel_ratio"] = _num(payload.get("dpr"))
    if payload.get("cores") is not None:
        try:
            updates["cores"] = min(int(payload.get("cores")), 256)
        except (TypeError, ValueError):
            pass
    if payload.get("memory") is not None:
        updates["memory_gb"] = _num(payload.get("memory"))
    if payload.get("downlink") is not None:
        updates["downlink"] = _num(payload.get("downlink"))
    if "touch" in payload:
        updates["touch"] = bool(payload.get("touch"))
    if created and not session.landing_path:
        updates["landing_path"] = _clip(payload.get("path") or payload.get("landing"), 255)
    if created or not session.referrer:
        updates["referrer"] = _clip(payload.get("referrer"), 500) or session.referrer
    for key, value in geo.items():
        if value in (None, ""):
            continue
        updates[key] = value
    for key, value in updates.items():
        setattr(session, key, value)
    session.save()


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
    geo = lookup_ip(ip)
    session, created = VisitSession.objects.get_or_create(
        sid=sid,
        defaults={
            "ip": ip or "0.0.0.0",
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:800],
            **{k: v for k, v in geo.items() if v not in (None, "")},
        },
    )
    _apply_session_fields(session, request, payload, geo, created)

    if action == "ping":
        view_id = payload.get("id")
        try:
            seconds = min(int(payload.get("seconds") or 0), 60 * 60 * 6)
        except (TypeError, ValueError):
            seconds = 0
        updated = PageView.objects.filter(id=view_id, session=session).update(
            seconds=seconds
        )
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


def _dash(value):
    if value is None or value == "":
        return "—"
    return value


def _session_info(session):
    browser, os_name, device = _parse_ua(session.user_agent)
    return {
        "browser": session.browser or (browser if browser != "Unknown" else ""),
        "os": session.os or (os_name if os_name != "Unknown" else ""),
        "device": session.device or device,
        "isp": session.isp or session.org,
        "tz": session.timezone_client or session.timezone_ip,
        "net": session.connection_effective or session.connection_type,
        "memory": f"{session.memory_gb:g} GB" if session.memory_gb else "",
        "dpr": f"{session.pixel_ratio:g}x" if session.pixel_ratio else "",
        "touch": "Yes" if session.touch else ("No" if session.touch is False else ""),
        "utm": " / ".join(
            p for p in (session.utm_source, session.utm_medium, session.utm_campaign) if p
        ),
    }


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


def _top(qs, field, limit=8):
    return list(
        qs.exclude(**{field: ""})
        .values(field)
        .annotate(n=Count("id"))
        .order_by("-n")[:limit]
    )


def _stats_context():
    sessions = VisitSession.objects.annotate(
        view_count=Count("views"),
        dwell=Sum("views__seconds"),
    )
    views = PageView.objects.select_related("session")
    total_seconds = views.aggregate(s=Sum("seconds"))["s"] or 0
    total_sessions = sessions.count() or 1
    bounced = sessions.filter(view_count=1).count()
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
    recent = []
    for view in views[:50]:
        s = view.session
        info = _session_info(s)
        place = ", ".join(p for p in (s.city, s.region, s.country) if p) or "Unknown"
        recent.append(
            {
                "when": timezone.localtime(view.started_at).strftime("%d %b %H:%M"),
                "path": view.path or "/",
                "time": _fmt_duration(view.seconds),
                "ip": s.ip,
                "place": place,
                "postal": _dash(s.postal),
                "isp": _dash(info["isp"]),
                "browser": _dash(info["browser"]),
                "os": _dash(info["os"]),
                "device": _dash(info["device"]),
                "lang": _dash(s.language),
                "screen": _dash(s.screen),
                "viewport": _dash(s.viewport),
                "tz": _dash(info["tz"]),
                "net": _dash(info["net"]),
                "platform": _dash(s.platform),
                "referrer": _dash(view.referrer or s.referrer),
                "ua": s.user_agent,
            }
        )
    visitors = []
    for s in sessions[:40]:
        info = _session_info(s)
        place = ", ".join(p for p in (s.city, s.region, s.country) if p) or "Unknown"
        visitors.append(
            {
                "when": timezone.localtime(s.last_seen).strftime("%d %b %H:%M"),
                "ip": s.ip,
                "place": place,
                "postal": _dash(s.postal),
                "continent": _dash(s.continent),
                "isp": _dash(info["isp"]),
                "org": _dash(s.org),
                "tz": _dash(info["tz"]),
                "browser": _dash(info["browser"]),
                "os": _dash(info["os"]),
                "device": _dash(info["device"]),
                "lang": _dash(s.language),
                "screen": _dash(s.screen),
                "viewport": _dash(s.viewport),
                "dpr": _dash(info["dpr"]),
                "net": _dash(info["net"]),
                "cores": _dash(s.cores),
                "memory": _dash(info["memory"]),
                "touch": _dash(info["touch"]),
                "theme": _dash(s.color_scheme),
                "platform": _dash(s.platform),
                "landing": _dash(s.landing_path),
                "referrer": _dash(s.referrer),
                "utm": _dash(info["utm"]),
                "pages": s.view_count,
                "time": _fmt_duration(s.dwell),
                "ua": s.user_agent,
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
    browsers_c, systems_c, devices_c = Counter(), Counter(), Counter()
    mobile = 0
    for session in sessions:
        info = _session_info(session)
        if info["browser"]:
            browsers_c[info["browser"]] += 1
        if info["os"]:
            systems_c[info["os"]] += 1
        if info["device"]:
            devices_c[info["device"]] += 1
        if info["device"] == "Mobile":
            mobile += 1
    return {
        "total_sessions": sessions.count(),
        "total_views": views.count(),
        "total_time": _fmt_duration(total_seconds),
        "avg_time": _fmt_duration(total_seconds / max(sessions.count(), 1)),
        "bounce": f"{round(100 * bounced / total_sessions)}%",
        "mobile": mobile,
        "pages": pages,
        "countries": _top(sessions, "country"),
        "browsers": [{"browser": name, "n": n} for name, n in browsers_c.most_common(8)],
        "systems": [{"os": name, "n": n} for name, n in systems_c.most_common(8)],
        "devices": [{"device": name, "n": n} for name, n in devices_c.most_common(8)],
        "isps": _top(sessions, "isp"),
        "languages": _top(sessions, "language"),
        "referrers": _top(sessions, "referrer", 6),
        "recent": recent,
        "visitors": visitors,
        "map_points": map_points,
    }
