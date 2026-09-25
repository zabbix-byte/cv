import logging
import re

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from services.github_card import render_error_card, render_user_github_card
from services.github_service import GitHubService

logger = logging.getLogger(__name__)

USER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


def parse_username(value):
    raw = (value or "").strip()
    if not raw:
        return ""
    raw = raw.lstrip("@")
    if "github.com/" in raw.lower():
        raw = raw.split("github.com/", 1)[-1]
    raw = raw.strip("/").split("/")[0].split("?")[0]
    if not USER_RE.match(raw):
        return None
    return raw


def _theme(request):
    theme = request.GET.get("theme", "light")
    if theme not in ("light", "dark"):
        theme = "light"
    return theme


def _embed(username):
    user = username or "YOUR_USERNAME"
    return (
        '<div align="center">\n'
        f'<a href="https://ztrunk.space/lab/github/?user={user}">\n'
        "  <picture>\n"
        '    <source media="(prefers-color-scheme: dark)" '
        f'srcset="https://ztrunk.space/lab/github.svg?user={user}&theme=dark&v=1">\n'
        f'    <img alt="{user} — GitHub profile" '
        f'src="https://ztrunk.space/lab/github.svg?user={user}&theme=light&v=1" width="880">\n'
        "  </picture>\n"
        "</a>\n"
        "</div>"
    )


def lab_home(request):
    return render(request, "community/hub.html")


@require_GET
def github_builder(request):
    raw = request.GET.get("user", "")
    username = parse_username(raw)
    invalid = raw.strip() and username is None
    missing = False
    if username:
        profile = GitHubService(username=username).get_user_profile(fallback=False)
        if not profile:
            missing = True
    return render(
        request,
        "community/github.html",
        {
            "query": raw.strip(),
            "username": username or "",
            "invalid": invalid,
            "missing": missing,
            "embed_code": _embed(username if username and not missing else ""),
        },
    )


@require_GET
def github_svg(request):
    theme = _theme(request)
    username = parse_username(request.GET.get("user", ""))
    if not username:
        svg = render_error_card(theme, "Add ?user=your-github-login")
        return HttpResponse(svg, content_type="image/svg+xml; charset=utf-8", status=400)
    try:
        service = GitHubService(username=username)
        if not service.get_user_profile(fallback=False):
            svg = render_error_card(theme, "GitHub user not found")
            return HttpResponse(
                svg, content_type="image/svg+xml; charset=utf-8", status=404
            )
        metrics = service.get_card_metrics()
        svg = render_user_github_card(theme, metrics)
    except Exception as exc:
        logger.error("Community GitHub card failed for %s: %s", username, exc)
        svg = render_error_card(theme, "Could not load GitHub data")
        return HttpResponse(svg, content_type="image/svg+xml; charset=utf-8", status=503)
    response = HttpResponse(svg, content_type="image/svg+xml; charset=utf-8")
    response["Cache-Control"] = "public, max-age=300"
    return response
