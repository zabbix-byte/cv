"""GitHub README graphic — ztrunk.space clouds + stats GitHub's profile hides."""

import math
from xml.sax.saxutils import escape


THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#171717",
        "muted": "#737373",
        "rule": "#171717",
        "core": "#faf9f6",
        "mid": "#a8b0ba",
        "rim": "#7a8490",
        "edge": "#58606c",
        "stroke": "#3e444e",
        "spec": "#ffffff",
    },
    "dark": {
        "bg": "transparent",
        "fg": "#f0f6fc",
        "muted": "#f0f6fc",
        "rule": "#f0f6fc",
        "core": "#161b22",
        "mid": "#21262d",
        "rim": "#30363d",
        "edge": "#484f58",
        "stroke": "#f0f6fc",
        "spec": "#f0f6fc",
    },
}

FONT = "Georgia, 'Times New Roman', Times, serif"
WIDTH = 880
PAD = 48
TEXT_CHARS = 54
YEARS_CODING = 13

INTRO = (
    "I'm a software engineer and technical lead specializing in designing and "
    "scaling data-intensive systems — from distributed pipelines to multi-tenant "
    "AI platforms. I've been coding for over 13 years — seven of them professionally."
)

STORY = (
    "As a founding engineer at Valerdat, I led and designed the software hands-on, "
    "developed it together with the team, and grew into the CTO role. Previously, "
    "I worked at Inditex and IBM. Today my work sits at the intersection of "
    "technology and product, remaining hands-on in daily software development."
)

WORK = (
    "Founding engineer to CTO at Valerdat — previously Inditex and IBM",
    "Planning & procurement platform — ERP data to purchase proposals",
    "Kernel drivers, injection, and game-security internals",
    "Press coverage and customer case studies",
)

CLOSING = (
    "We're hiring ML Engineers and Full Stack Developers. "
    "I'm always open to talking about architecture, performance, and data at scale."
)


def _t(value, limit=None):
    text = "" if value is None else str(value)
    if limit and len(text) > limit:
        text = text[: limit - 1] + "…"
    return escape(text)


def _wrap(text, width):
    words = (text or "").split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if len(trial) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def _fmt_n(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    if number >= 10000:
        return f"{number / 1000:.0f}k"
    if number >= 1000:
        return f"{number / 1000:.1f}".rstrip("0").rstrip(".") + "k"
    return str(number)


def _blob_d(cx, cy, scale, phase, unit=152, steps=72):
    parts = []
    for i in range(steps + 1):
        theta = (i / steps) * math.tau
        morph = (
            0.13 * math.sin(2 * theta + phase * 0.62)
            + 0.09 * math.sin(3 * theta - phase * 0.41)
            + 0.055 * math.sin(4 * theta + phase * 0.88)
            + 0.04 * math.sin(5 * theta + phase * 0.27)
            + 0.03 * math.cos(7 * theta - phase * 0.53)
        )
        radius = unit * scale * (1 + morph)
        x = round(cx + math.cos(theta) * radius, 1)
        y = round(cy + math.sin(theta) * radius, 1)
        parts.append(f"{'M' if i == 0 else 'L'}{x} {y}")
    return " ".join(parts) + " Z"


def _text(x, y, content, size, fill, weight="400", anchor="start"):
    extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}"{extra}>{_t(content)}</text>'
    )


def _cloud(theme, idx, cx, cy, scale, phase, dur):
    fill_id = f"blob-fill-{idx}"
    d0 = _blob_d(cx, cy, scale, phase)
    d1 = _blob_d(cx, cy, scale, phase + 1.15)
    gx = round(cx - 152 * scale * 0.18, 1)
    gy = round(cy - 152 * scale * 0.22, 1)
    gradient = (
        f'<radialGradient id="{fill_id}" cx="{gx}" cy="{gy}" r="{round(152 * scale * 1.08, 1)}" '
        f'gradientUnits="userSpaceOnUse">'
        f'<stop offset="0%" stop-color="{theme["core"]}" stop-opacity="0.22"/>'
        f'<stop offset="38%" stop-color="{theme["mid"]}" stop-opacity="0.18"/>'
        f'<stop offset="78%" stop-color="{theme["rim"]}" stop-opacity="0.28"/>'
        f'<stop offset="100%" stop-color="{theme["edge"]}" stop-opacity="0.34"/>'
        "</radialGradient>"
    )
    animate = (
        f'<animate attributeName="d" values="{d0};{d1};{d0}" dur="{dur}s" '
        'repeatCount="indefinite"/>'
    )
    body = (
        f'<path fill="url(#{fill_id})" d="{d0}">{animate}</path>'
        f'<path fill="none" stroke="{theme["stroke"]}" stroke-opacity="0.38" '
        f'stroke-width="1.15" stroke-linejoin="round" d="{d0}">{animate}</path>'
    )
    return gradient, body


def render_github_card(theme="light", metrics=None):
    theme = THEMES.get(theme, THEMES["light"])
    metrics = metrics or {}
    stars = _fmt_n(metrics.get("stars"))
    forks = _fmt_n(metrics.get("forks"))
    langs = [name for name in (metrics.get("langs") or []) if name][:4]
    github_year = metrics.get("github_year")
    years_coding = metrics.get("years_coding") or YEARS_CODING

    y = 46
    content = [_text(PAD, y, "ztrunk.space", 13, theme["muted"])]
    y += 40
    content.append(_text(PAD, y, "Vasile Ovidiu Ichim", 34, theme["fg"], "500"))
    y += 14
    content.append(
        f'<rect x="{PAD}" y="{y}" width="44" height="1" fill="{theme["rule"]}" opacity="0.28"/>'
    )
    y += 28
    content.append(_text(PAD, y, "Co-founder & CTO · Valerdat", 16, theme["muted"]))
    y += 40
    figures = [
        (stars, "stars across public work"),
        (forks, "forks of my repos"),
        (str(years_coding), "years coding"),
        (str(github_year) if github_year else None, "on GitHub"),
    ]
    figures = [(value, label) for value, label in figures if value]
    if figures:
        col = 188
        for i, (value, label) in enumerate(figures):
            x = PAD + i * col
            content.append(_text(x, y, value, 26, theme["fg"], "500"))
            content.append(_text(x, y + 18, label, 11, theme["muted"]))
        y += 48
    y += 12
    for line in _wrap(INTRO, TEXT_CHARS):
        content.append(_text(PAD, y, line, 16, theme["fg"]))
        y += 24
    y += 14
    for line in _wrap(STORY, TEXT_CHARS):
        content.append(_text(PAD, y, line, 16, theme["fg"]))
        y += 24
    y += 26
    content.append(_text(PAD, y, "Some of my work", 13, theme["muted"]))
    y += 26
    for item in WORK:
        lines = _wrap(item, TEXT_CHARS - 2)
        content.append(
            f'<circle cx="{PAD + 4}" cy="{y - 5}" r="2.2" fill="{theme["fg"]}"/>'
        )
        for i, line in enumerate(lines):
            content.append(_text(PAD + 18, y, line, 15, theme["fg"]))
            y += 22 if i < len(lines) - 1 else 26
    if langs:
        y += 10
        content.append(
            _text(PAD, y, "Public work in " + ", ".join(langs), 13, theme["muted"])
        )
        y += 8
    y += 18
    for line in _wrap(CLOSING, TEXT_CHARS):
        content.append(_text(PAD, y, line, 15, theme["muted"]))
        y += 22
    y += 18
    content.append(
        _text(
            PAD,
            y,
            "ztrunk.space  ·  valerdat.com  ·  linkedin.com/in/zabbix-byte",
            13,
            theme["muted"],
        )
    )
    height = y + 64
    return _assemble_svg(
        theme,
        height,
        content,
        "Vasile Ovidiu Ichim — Co-founder & CTO, Valerdat",
    )


def render_user_github_card(theme="light", metrics=None):
    theme = THEMES.get(theme, THEMES["light"])
    metrics = metrics or {}
    login = metrics.get("login") or "github"
    name = metrics.get("name") or login
    bio = metrics.get("bio") or ""
    company = (metrics.get("company") or "").lstrip("@")
    location = metrics.get("location") or ""
    stars = _fmt_n(metrics.get("stars"))
    forks = _fmt_n(metrics.get("forks"))
    langs = [item for item in (metrics.get("langs") or []) if item][:4]
    github_year = metrics.get("github_year")
    years_on = metrics.get("years_on_github")

    role_bits = [bit for bit in (company, location) if bit]
    role = " · ".join(role_bits) if role_bits else f"@{login}"

    y = 46
    content = [_text(PAD, y, f"github.com/{login}", 13, theme["muted"])]
    y += 40
    content.append(_text(PAD, y, name, 34, theme["fg"], "500"))
    y += 14
    content.append(
        f'<rect x="{PAD}" y="{y}" width="44" height="1" fill="{theme["rule"]}" opacity="0.28"/>'
    )
    y += 28
    content.append(_text(PAD, y, role, 16, theme["muted"]))
    y += 40
    figures = [
        (stars, "stars across public work"),
        (forks, "forks of my repos"),
        (str(years_on) if years_on else None, "years on GitHub"),
        (str(github_year) if github_year else None, "on GitHub"),
    ]
    figures = [(value, label) for value, label in figures if value]
    if figures:
        col = 188
        for i, (value, label) in enumerate(figures):
            x = PAD + i * col
            content.append(_text(x, y, value, 26, theme["fg"], "500"))
            content.append(_text(x, y + 18, label, 11, theme["muted"]))
        y += 48
    y += 12
    if bio:
        for line in _wrap(bio, TEXT_CHARS):
            content.append(_text(PAD, y, line, 16, theme["fg"]))
            y += 24
        y += 14
    if langs:
        content.append(
            _text(PAD, y, "Public work in " + ", ".join(langs), 13, theme["muted"])
        )
        y += 26
    content.append(
        _text(PAD, y, f"github.com/{login}  ·  ztrunk.space/lab", 13, theme["muted"])
    )
    height = y + 64
    return _assemble_svg(theme, height, content, f"{name} on GitHub")


def render_error_card(theme="light", message="GitHub user not found"):
    theme = THEMES.get(theme, THEMES["light"])
    content = [
        _text(PAD, 80, "ztrunk.space/lab", 13, theme["muted"]),
        _text(PAD, 130, message, 22, theme["fg"], "500"),
        _text(PAD, 168, "Check the username and try again.", 16, theme["muted"]),
    ]
    return _assemble_svg(theme, 220, content, message)


def _assemble_svg(theme, height, content, aria):
    clouds = [
        (0, round(WIDTH * 0.92, 1), round(height * 0.1, 1), 1.0, 0.0, 9.5),
        (1, round(WIDTH * 0.08, 1), round(height * 0.9, 1), 0.86, 2.1, 11.0),
        (2, round(WIDTH * 0.93, 1), round(height * 0.88, 1), 0.74, 4.4, 8.2),
    ]
    gradients = []
    cloud_markup = []
    for spec in clouds:
        gradient, markup = _cloud(theme, *spec)
        gradients.append(gradient)
        cloud_markup.append(markup)

    defs = "<defs>" + "".join(gradients) + "</defs>"
    bg = theme["bg"]
    backdrop = (
        ""
        if bg in ("none", "transparent")
        else f'<rect x="0" y="0" width="{WIDTH}" height="{height}" fill="{bg}"/>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" '
        f'style="background:transparent" '
        f'aria-label="{_t(aria)}">'
        + backdrop
        + defs
        + "".join(cloud_markup)
        + "".join(content)
        + "</svg>"
    )
