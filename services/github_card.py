"""SVG profile card for GitHub README (iframes are stripped there)."""

from xml.sax.saxutils import escape


THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#171717",
        "muted": "#737373",
        "border": "#e5e5e5",
        "surface": "#fafafa",
        "heat": ("#ececec", "#c8c8c8", "#9a9a9a", "#5c5c5c", "#171717"),
    },
    "dark": {
        "bg": "#1a1a1a",
        "fg": "#e8e8e8",
        "muted": "#9a9a9a",
        "border": "#333333",
        "surface": "#242424",
        "heat": ("#2a2a2a", "#4a4a4a", "#7a7a7a", "#b5b5b5", "#e8e8e8"),
    },
}

FONT = "Georgia, 'Times New Roman', Times, serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
WIDTH = 840


def _t(value, limit=None):
    text = "" if value is None else str(value)
    if limit and len(text) > limit:
        text = text[: limit - 1] + "…"
    return escape(text)


def _heat_fill(theme, level):
    colors = theme["heat"]
    try:
        return colors[max(0, min(int(level), 4))]
    except (TypeError, ValueError):
        return colors[0]


def render_github_card(payload, theme="light"):
    theme = THEMES.get(theme, THEMES["light"])
    profile = payload.get("profile") or {}
    stats = payload.get("stats") or {}
    pinned = (payload.get("pinned") or [])[:6]
    weeks = payload.get("weeks") or []
    avatar = payload.get("avatar_data") or ""
    contrib = payload.get("contrib_total") or 0
    name = profile.get("name") or "Vasile Ovidiu Ichim"
    login = profile.get("login") or "zabbix-byte"
    bio = profile.get("bio") or "Supply software by day, cracking games by night"
    place = " · ".join(
        p for p in (profile.get("company"), profile.get("location")) if p
    )

    repos = stats.get("total_repos") or profile.get("public_repos") or 0
    stars = stats.get("total_stars") or 0
    followers = stats.get("followers") or profile.get("followers") or 0

    y = 28
    parts = []

    def text(x, yy, content, size=15, fill=None, weight="400", family=FONT, anchor="start", limit=None):
        fill = fill or theme["fg"]
        parts.append(
            f'<text x="{x}" y="{yy}" fill="{fill}" font-family="{family}" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">'
            f"{_t(content, limit)}</text>"
        )

    parts.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="HEIGHT_PLACE" rx="18" '
        f'fill="{theme["bg"]}" stroke="{theme["border"]}"/>'
    )

    text(28, y + 14, "ztrunk.space", 12, theme["muted"])
    text(WIDTH - 28, y + 14, "GitHub", 12, theme["muted"], anchor="end")
    y += 36

    if avatar:
        parts.append('<defs><clipPath id="av"><circle cx="60" cy="CY" r="32"/></clipPath></defs>')
        cy = y + 32
        parts[-1] = parts[-1].replace("CY", str(cy))
        parts.append(
            f'<image href="{avatar}" x="28" y="{y}" width="64" height="64" '
            f'clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>'
        )
        parts.append(
            f'<circle cx="60" cy="{cy}" r="32.5" fill="none" stroke="{theme["border"]}"/>'
        )
        text_x = 108
    else:
        text_x = 28

    text(text_x, y + 22, name, 22, weight="500", limit=42)
    text(text_x, y + 44, f"@{login}", 14, theme["muted"], limit=34)
    text(text_x, y + 66, bio, 13, theme["fg"], limit=72)
    if place:
        text(text_x, y + 86, place, 12, theme["muted"], limit=60)
    y += 108

    metrics = (
        (str(repos), "repos"),
        (str(stars), "stars"),
        (str(followers), "followers"),
        (str(contrib), "contrib"),
    )
    for i, (value, label) in enumerate(metrics):
        x = 28 + i * 200
        text(x, y, value, 20, weight="500")
        text(x, y + 18, label, 12, theme["muted"])
    y += 44

    if weeks:
        text(28, y, f"{contrib} contributions in the last year", 12, theme["muted"])
        y += 10
        cell, gap = 10, 3
        heat_w = len(weeks) * (cell + gap) - gap
        x0 = max(28, WIDTH - 28 - heat_w)
        for wi, week in enumerate(weeks):
            for di, day in enumerate(week):
                x = x0 + wi * (cell + gap)
                yy = y + di * (cell + gap)
                fill = _heat_fill(theme, day.get("level") or 0)
                title = _t(f"{day.get('date', '')} · {day.get('count', 0)}")
                parts.append(
                    f'<rect x="{x}" y="{yy}" width="{cell}" height="{cell}" rx="2" '
                    f'fill="{fill}"><title>{title}</title></rect>'
                )
        y += 7 * (cell + gap) + 18

    if pinned:
        text(28, y, "Pinned", 12, theme["muted"])
        y += 12
        col_w = 252
        row_h = 78
        for i, repo in enumerate(pinned):
            col = i % 3
            row = i // 3
            x = 28 + col * (col_w + 14)
            yy = y + row * (row_h + 10)
            parts.append(
                f'<rect x="{x}" y="{yy}" width="{col_w}" height="{row_h}" rx="12" '
                f'fill="{theme["surface"]}" stroke="{theme["border"]}"/>'
            )
            text(x + 14, yy + 24, repo.get("name"), 14, weight="500", limit=26)
            text(x + 14, yy + 44, repo.get("description") or "", 12, theme["muted"], limit=34)
            lang = repo.get("language") or ""
            stars_n = repo.get("stargazers_count") or 0
            meta = " · ".join(p for p in (lang, f"★ {stars_n}") if p)
            text(x + 14, yy + 64, meta, 11, theme["muted"], limit=32)
        rows = (len(pinned) + 2) // 3
        y += rows * (row_h + 10) + 8

    text(28, y + 8, "Co-founder & CTO · Valerdat", 12, theme["muted"])
    height = y + 28
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" '
        f'aria-label="{_t(name)} on GitHub">'
        + "".join(parts).replace("HEIGHT_PLACE", str(height - 1))
        + "</svg>"
    )
    return svg
