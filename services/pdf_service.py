"""
PDF generation service for CV.

Editorial, monocrome layout — same spirit as the site (serif, quiet hierarchy).
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
from django.conf import settings
from pathlib import Path


# ---- Palette (leerob-aligned) -------------------------------------------
INK = HexColor("#171717")
MUTED = HexColor("#737373")
LINE = HexColor("#e5e5e5")

# Prefer Times (built-in serif). Optional STIX if present under static/fonts.
_FONT = "Times-Roman"
_FONT_BOLD = "Times-Bold"
_FONT_ITALIC = "Times-Italic"


def _register_fonts():
    global _FONT, _FONT_BOLD, _FONT_ITALIC
    fonts_dir = Path(settings.BASE_DIR) / "static" / "fonts"
    regular = fonts_dir / "STIXTwoText-Regular.ttf"
    bold = fonts_dir / "STIXTwoText-Medium.ttf"
    if regular.exists() and bold.exists():
        try:
            pdfmetrics.registerFont(TTFont("STIXTwo", str(regular)))
            pdfmetrics.registerFont(TTFont("STIXTwo-Bold", str(bold)))
            _FONT = "STIXTwo"
            _FONT_BOLD = "STIXTwo-Bold"
            _FONT_ITALIC = "STIXTwo"
        except Exception:
            pass


class CVPDFGenerator:
    """Quiet, recruiter-focused editorial CV."""

    PAGE_SIZE = A4
    MARGIN = 16 * mm

    def __init__(self):
        _register_fonts()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.content_width = self.PAGE_SIZE[0] - 2 * self.MARGIN

    def _setup_custom_styles(self):
        add = self.styles.add

        add(ParagraphStyle(
            name="Name", fontName=_FONT_BOLD, fontSize=18,
            textColor=INK, leading=20, spaceAfter=2,
        ))
        add(ParagraphStyle(
            name="JobTitle", fontName=_FONT, fontSize=10.5,
            textColor=MUTED, leading=14, spaceAfter=4,
        ))
        add(ParagraphStyle(
            name="Contact", fontName=_FONT, fontSize=9,
            textColor=MUTED, leading=12, spaceAfter=10,
        ))
        add(ParagraphStyle(
            name="Section", fontName=_FONT_BOLD, fontSize=10,
            textColor=INK, leading=12, spaceBefore=8, spaceAfter=2,
        ))
        add(ParagraphStyle(
            name="Summary", fontName=_FONT, fontSize=9.4,
            textColor=INK, leading=13, alignment=TA_LEFT,
        ))
        add(ParagraphStyle(
            name="Role", fontName=_FONT_BOLD, fontSize=10,
            textColor=INK, leading=12,
        ))
        add(ParagraphStyle(
            name="Date", fontName=_FONT, fontSize=9,
            textColor=MUTED, leading=12, alignment=TA_RIGHT,
        ))
        add(ParagraphStyle(
            name="ExpBullet", fontName=_FONT, fontSize=9,
            textColor=INK, leading=11.8,
            leftIndent=10, bulletIndent=0, spaceAfter=1,
        ))
        add(ParagraphStyle(
            name="SkillCat", fontName=_FONT_BOLD, fontSize=9,
            textColor=INK, leading=12,
        ))
        add(ParagraphStyle(
            name="SkillVal", fontName=_FONT, fontSize=9,
            textColor=INK, leading=12,
        ))
        add(ParagraphStyle(
            name="Project", fontName=_FONT_BOLD, fontSize=9.2,
            textColor=INK, leading=12,
        ))
        add(ParagraphStyle(
            name="ProjectDesc", fontName=_FONT, fontSize=9,
            textColor=INK, leading=12,
        ))
        add(ParagraphStyle(
            name="Tech", fontName=_FONT_ITALIC, fontSize=8.2,
            textColor=MUTED, leading=11,
        ))
        add(ParagraphStyle(
            name="EduTitle", fontName=_FONT_BOLD, fontSize=9.2,
            textColor=INK, leading=12,
        ))
        add(ParagraphStyle(
            name="EduMeta", fontName=_FONT, fontSize=8.8,
            textColor=MUTED, leading=11,
        ))

    def generate_cv_pdf(self, context_data):
        buffer = io.BytesIO()

        doc = BaseDocTemplate(
            buffer,
            pagesize=self.PAGE_SIZE,
            leftMargin=self.MARGIN,
            rightMargin=self.MARGIN,
            topMargin=self.MARGIN,
            bottomMargin=12 * mm,
            title="Vasile Ovidiu Ichim — CV",
            author="Vasile Ovidiu Ichim",
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
            id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        )
        doc.addPageTemplates([
            PageTemplate(id="cv", frames=[frame], onPage=self._draw_footer)
        ])

        elements = []
        elements += self._header(context_data)
        elements += self._summary()
        elements += self._experience()
        elements += self._bottom()

        doc.build(elements)
        pdf_value = buffer.getvalue()
        buffer.close()
        return io.BytesIO(pdf_value)

    def _draw_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        y = 8 * mm
        canvas.line(self.MARGIN, y + 4 * mm, self.PAGE_SIZE[0] - self.MARGIN, y + 4 * mm)
        canvas.setFont(_FONT, 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            self.MARGIN, y,
            "Vasile Ovidiu Ichim · Staff Engineer & Technical Lead",
        )
        canvas.drawRightString(
            self.PAGE_SIZE[0] - self.MARGIN, y,
            "github.com/zabbix-byte",
        )
        canvas.restoreState()

    def _header(self, ctx):
        name = ctx.get("name", "Vasile Ovidiu Ichim")
        title = ctx.get("title", "Staff Engineer &amp; Technical Lead · Software Architect")
        location = ctx.get("location", "Barcelona, Spain")
        email = ctx.get("email", "zabbix@ztrunk.space")

        def link(url, label):
            return f'<a href="{url}" color="#171717"><u>{label}</u></a>'

        contact = "&nbsp;&nbsp;·&nbsp;&nbsp;".join([
            location,
            link("https://www.linkedin.com/in/zabbix-byte/", "linkedin.com/in/zabbix-byte"),
            link(f"mailto:{email}", email),
            link("https://github.com/zabbix-byte", "github.com/zabbix-byte"),
        ])

        return [
            Paragraph(name, self.styles["Name"]),
            Paragraph(title, self.styles["JobTitle"]),
            Paragraph(contact, self.styles["Contact"]),
            HRFlowable(width="100%", thickness=0.6, color=LINE,
                       spaceBefore=0, spaceAfter=8, lineCap="round"),
        ]

    def _section_header(self, text):
        return [
            Paragraph(text, self.styles["Section"]),
            HRFlowable(width="100%", thickness=0.5, color=LINE,
                       spaceBefore=0, spaceAfter=5, lineCap="round"),
        ]

    def _summary(self):
        text = (
            "Software engineer and technical lead specializing in designing and scaling "
            "data-intensive systems — from distributed pipelines to multi-tenant AI platforms. "
            "Coding for over 13 years — seven of them professionally."
        )
        text2 = (
            "Founding engineer at <b>Valerdat</b>, led and designed the software hands-on and developed it "
            "together with the team before becoming CTO — operating across <b>500k+ SKUs</b> and <b>10TB+</b> of "
            "supply-chain data, with demand forecasting at &lt;7% MAPE. Hands-on daily. "
            "Previously at <b>Inditex</b> and <b>IBM</b>."
        )
        press = (
            'Featured in <a href="https://www.viaempresa.cat/es/empresa/'
            'como-inteligencia-artificial-redefine-cadena-suministro-caso-valerdat_2202088_102.html" '
            'color="#737373"><u>VIA Empresa</u></a>'
            ' · <a href="https://valerdat.com/casosdeexito" '
            'color="#737373"><u>valerdat.com/casosdeexito</u></a>'
        )
        return self._section_header("Profile") + [
            Paragraph(text, self.styles["Summary"]),
            Spacer(1, 2),
            Paragraph(text2, self.styles["Summary"]),
            Spacer(1, 3),
            Paragraph(press, self.styles["Tech"]),
            Spacer(1, 2),
        ]

    def _exp_entry(self, role, company, dates, bullets):
        head = Table(
            [[Paragraph(f"{role} · {company}", self.styles["Role"]),
              Paragraph(dates, self.styles["Date"])]],
            colWidths=[self.content_width * 0.74, self.content_width * 0.26],
        )
        head.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        flow = [head]
        for b in bullets:
            flow.append(Paragraph(b, self.styles["ExpBullet"], bulletText="•"))
        flow.append(Spacer(1, 4))
        return KeepTogether(flow)

    def _experience(self):
        entries = [
            self._exp_entry(
                "Co-founder &amp; CTO", "Valerdat", "2021 – Present",
                [
                    "Joined as founding engineer, grew into tech lead, then CTO — led and designed the software hands-on; developed it with the team.",
                    "As CTO: architecture, data and application platform, cloud and security posture, and technical hiring — while staying in the code on the hard paths.",
                    "Day to day: design reviews, platform ownership, and close work with product so forecasting and procurement stay tied to real supply-chain workflows.",
                ],
            ),
            self._exp_entry(
                "Python Software Engineer (concurrent)", "Knowmad Mood (Inditex)", "Oct 2023 – Sep 2024",
                [
                    "Built the strategic planning platform for Inditex's Security Department (Django, React, AWS).",
                    "Designed REST APIs and microservices, improving scalability of internal supply-chain operations.",
                    "Optimized PostgreSQL analytics queries and shipped via Docker and CI/CD pipelines.",
                ],
            ),
            self._exp_entry(
                "Middleware &amp; Application Operations", "IBM", "Feb 2021 – Mar 2022",
                [
                    "Coordinated and executed application deployments and updates for CTTI (Generalitat de Catalunya) public services — tax, agriculture and others.",
                    "Administered application and web servers: IBM WebSphere, Oracle WebLogic, Apache Tomcat, Apache HTTP Server and Nginx.",
                    "Operated across RedHat Linux and Windows Server environments, ensuring reliable release rollouts.",
                ],
            ),
            self._exp_entry(
                "Software &amp; Systems Engineer", "Dataxip SL", "Feb 2018 – Feb 2021",
                [
                    "Built and operated physical servers, networking &amp; security (MikroTik), Linux services (Apache/Nginx) and Python web apps.",
                    "Developed Sage 50 ERP extensions and custom reports — early foundation for the ERP integration work I lead today.",
                ],
            ),
        ]
        return self._section_header("Experience") + entries

    def _skills_block(self):
        rows = [
            ("Languages", "Python, C/C++, JavaScript/TypeScript, SQL, Bash"),
            ("Backend &amp; Data", "Django, FastAPI, REST, Celery, Redis, PostgreSQL, Databricks, Spark, ETL"),
            ("Cloud &amp; DevOps", "AWS, Docker, Kubernetes, Terraform, CI/CD, Linux"),
            ("AI, ML &amp; Architecture", "Forecasting (Prophet, XGBoost, TFT, and 13 other models), LLM integration, distributed systems, multi-tenant SaaS, ERP integrations"),
            ("Leadership", "Architecture &amp; design reviews, technical direction, mentoring"),
        ]
        data = []
        for cat, val in rows:
            data.append([
                Paragraph(cat, self.styles["SkillCat"]),
                Paragraph(val, self.styles["SkillVal"]),
            ])
        t = Table(data, colWidths=[36 * mm, self.content_width - 36 * mm])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
        ]))
        return self._section_header("Skills") + [t]

    def _project_cell(self, name, desc):
        mini = Table(
            [[Paragraph(name, self.styles["Project"])],
             [Paragraph(desc, self.styles["ProjectDesc"])]],
            colWidths=[self.content_width / 2 - 5 * mm],
        )
        mini.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        return mini

    def _projects_block(self):
        p = [
            self._project_cell(
                "AI Planning &amp; Procurement Platform · Valerdat",
                "Planning and procurement platform end to end (demand planning, purchasing, replenishment): 500k+ SKUs / 10TB+ data; model analysis as base for planning (&lt;7% MAPE, best of 13+ models), purchase optimizer, platform as the base system clients build on; multi-tenant Django + Databricks/Spark, ERP connectors (Sage/BC/SAP — Sage Marketplace), agents that converse and automate — all wrapped in each client’s business logic. Path: ingest → forecast → purchase optimizer → platform."),
            self._project_cell(
                "Strategic Planning · Inditex",
                "Planning platform for Inditex’s Security Department — Django, React, and AWS."),
        ]
        gutter = 8 * mm
        col_w = (self.content_width - gutter) / 2.0
        grid = Table(
            [[p[0], p[1]]],
            colWidths=[col_w, col_w],
        )
        grid.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (0, -1), 0),
            ("RIGHTPADDING", (0, 0), (0, -1), gutter),
            ("LEFTPADDING", (1, 0), (1, -1), gutter),
            ("RIGHTPADDING", (1, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return self._section_header("Featured Projects") + [grid]

    def _research_block(self):
        intro = (
            "Security &amp; systems internals (personal). Windows kernel and user-mode work — "
            "how I started programming 12–13 years ago and still a hobby that sharpens how I reason "
            "about boundaries, failure modes, and performance in production."
        )
        items = [
            ('<b><a href="https://github.com/zabbix-byte/ztdriver" color="#171717"><u>Windows Kernel Drivers</u></a></b> — '
             "kernel-mode driver experiments in C++ exploring user/kernel communication and IOCTL paths."),
            ('<b><a href="https://github.com/zabbix-byte/ztui" color="#171717"><u>Overlay cheat base</u></a></b> — '
             "end-to-end overlay cheat base: kernel driver + user-mode client for memory access, DLL loading, and real-time DX11 overlays."),
            ('<b><a href="https://github.com/zabbix-byte/zt_cs_cheat" color="#171717"><u>End-to-end game cheat</u></a></b> (archived) — '
             "a separate full cheat: process attachment, DLL injection, and memory layout — the same surfaces anti-cheat systems watch."),
        ]
        flow = self._section_header("Research") + [
            Paragraph(intro, self.styles["Summary"]),
            Spacer(1, 2),
        ]
        for it in items:
            flow.append(Paragraph(it, self.styles["ExpBullet"], bulletText="•"))
        flow.append(Spacer(1, 2))
        flow.append(Paragraph(
            "Open-source &amp; side projects: "
            '<a href="https://github.com/zabbix-byte/PyPulse" color="#171717"><u>PyPulse</u></a> (Chromium desktop apps in Python), '
            '<a href="https://github.com/zabbix-byte/cefpythonX" color="#171717"><u>cefpythonX</u></a> (CEF bindings for Python 3.10–3.13), '
            '<a href="https://github.com/zabbix-byte/real-tars" color="#171717"><u>real-tars</u></a> (Interstellar TARS robot — embedded AI agent), and more on '
            '<a href="https://github.com/zabbix-byte" color="#171717"><u>GitHub</u></a>.',
            self.styles["EduMeta"]))
        return flow

    def _edu_block(self):
        edu = Table(
            [[Paragraph("B.Sc. Computer Science — The Open University",
                        self.styles["EduTitle"]),
              Paragraph("2023 – 2027", self.styles["Date"])]],
            colWidths=[self.content_width * 0.74, self.content_width * 0.26],
        )
        edu.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        flow = self._section_header("Education")
        flow.append(edu)
        flow.append(Paragraph("In progress.", self.styles["EduMeta"]))
        flow.append(Spacer(1, 3))
        flow.append(Paragraph(
            "Languages: Romanian (native) · Spanish (fluent, C2) · English (professional, C1)",
            self.styles["EduMeta"]))
        flow.append(Paragraph(
            "Coursework: Platzi (platzi.com/p/zabbix) — Python, C++, AWS, FastAPI, Git, and more.",
            self.styles["EduMeta"]))
        return flow

    def _bottom(self):
        flow = [Spacer(1, 2)]
        flow += self._skills_block()
        flow.append(Spacer(1, 4))
        flow += self._projects_block()
        flow.append(Spacer(1, 4))
        flow += self._research_block()
        flow.append(Spacer(1, 4))
        flow.append(KeepTogether(self._edu_block()))
        return flow


def generate_cv_pdf_response(context_data):
    """Generate PDF response for CV download."""
    generator = CVPDFGenerator()
    pdf_buffer = generator.generate_cv_pdf(context_data)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        'attachment; filename="Vasile_Ovidiu_Ichim_CV.pdf"'
    )
    response.write(pdf_buffer.getvalue())
    return response
