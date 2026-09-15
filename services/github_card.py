"""GitHub README graphic — CV copy from ztrunk.space, not GitHub chrome."""

from xml.sax.saxutils import escape


THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#171717",
        "muted": "#737373",
        "border": "#e5e5e5",
        "rule": "#171717",
        "blob": "#8a93a0",
    },
    "dark": {
        "bg": "#1a1a1a",
        "fg": "#e8e8e8",
        "muted": "#9a9a9a",
        "border": "#333333",
        "rule": "#e8e8e8",
        "blob": "#c5c8ce",
    },
}

FONT = "Georgia, 'Times New Roman', Times, serif"
WIDTH = 880
PAD = 48


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
    "From founding engineer to CTO — Valerdat, Inditex, IBM",
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


def render_github_card(theme="light"):
    theme = THEMES.get(theme, THEMES["light"])
    y = 0
    parts = []

    def text(x, yy, content, size=16, fill=None, weight="400", italic=False):
        fill = fill or theme["fg"]
        style = ' font-style="italic"' if italic else ""
        parts.append(
            f'<text x="{x}" y="{yy}" fill="{fill}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}"{style}>{_t(content)}</text>'
        )

    def paragraph(content, size, fill, chars, line_h):
        nonlocal y
        for line in _wrap(content, chars):
            text(PAD, y, line, size, fill)
            y += line_h

    parts.append(
        f'<rect x="0" y="0" width="{WIDTH}" height="HEIGHT_PLACE" fill="{theme["bg"]}"/>'
    )
    parts.append(
        "<defs>"
        f'<radialGradient id="blob-a" cx="10%" cy="0%" r="46%">'
        f'<stop offset="0%" stop-color="{theme["blob"]}" stop-opacity="0.2"/>'
        f'<stop offset="100%" stop-color="{theme["blob"]}" stop-opacity="0"/>'
        "</radialGradient>"
        f'<radialGradient id="blob-b" cx="100%" cy="80%" r="40%">'
        f'<stop offset="0%" stop-color="{theme["blob"]}" stop-opacity="0.12"/>'
        f'<stop offset="100%" stop-color="{theme["blob"]}" stop-opacity="0"/>'
        "</radialGradient>"
        "</defs>"
    )
    parts.append(f'<ellipse cx="60" cy="0" rx="280" ry="200" fill="url(#blob-a)"/>')
    parts.append(f'<ellipse cx="860" cy="620" rx="240" ry="180" fill="url(#blob-b)"/>')

    y = 44
    text(PAD, y, "ztrunk.space", 13, theme["muted"])
    y += 40
    text(PAD, y, "Vasile Ovidiu Ichim", 34, weight="500")
    y += 14
    parts.append(
        f'<rect x="{PAD}" y="{y}" width="44" height="1" fill="{theme["rule"]}" opacity="0.28"/>'
    )
    y += 28
    text(PAD, y, "Co-founder & CTO · Valerdat", 16, theme["muted"])
    y += 36
    paragraph(INTRO, 16, theme["fg"], 78, 24)
    y += 16
    paragraph(STORY, 16, theme["fg"], 78, 24)
    y += 28
    text(PAD, y, "Some of my work", 13, theme["muted"])
    y += 26
    for item in WORK:
        parts.append(
            f'<circle cx="{PAD + 4}" cy="{y - 5}" r="2.2" fill="{theme["fg"]}"/>'
        )
        text(PAD + 18, y, item, 15)
        y += 26
    y += 18
    paragraph(CLOSING, 15, theme["muted"], 78, 22)
    y += 20
    text(PAD, y, "ztrunk.space  ·  valerdat.com  ·  linkedin.com/in/zabbix-byte", 13, theme["muted"])
    height = y + 40

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" '
        f'aria-label="Vasile Ovidiu Ichim — Co-founder &amp; CTO, Valerdat">'
        + "".join(parts).replace("HEIGHT_PLACE", str(height))
        + "</svg>"
    )
