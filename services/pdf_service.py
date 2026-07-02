"""
PDF generation service for CV.

Produces a modern, recruiter-optimized one/two-page CV: scannable layout,
impact-driven bullets, curated projects and ATS-friendly keywords.
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
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
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from django.http import HttpResponse


# ---- Brand palette -------------------------------------------------------
INK = HexColor("#1d1d1f")
DARK = HexColor("#1c1c1e")
ACCENT = HexColor("#0071e3")
MUTED = HexColor("#6b7280")
LIGHT = HexColor("#f5f5f7")
LINE = HexColor("#e5e7eb")
WHITE_SOFT = HexColor("#f0f0f2")


class CVPDFGenerator:
    """Modern, recruiter-focused CV PDF generator."""

    PAGE_SIZE = A4
    MARGIN = 12 * mm

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.content_width = self.PAGE_SIZE[0] - 2 * self.MARGIN

    # ---- Styles ----------------------------------------------------------
    def _setup_custom_styles(self):
        add = self.styles.add

        add(ParagraphStyle(
            name="Name", fontName="Helvetica-Bold", fontSize=22,
            textColor=white, leading=25, spaceAfter=2,
        ))
        add(ParagraphStyle(
            name="JobTitle", fontName="Helvetica", fontSize=11.5,
            textColor=HexColor("#9aa0a6"), leading=15, spaceAfter=8,
        ))
        add(ParagraphStyle(
            name="Contact", fontName="Helvetica", fontSize=8.8,
            textColor=HexColor("#c7c9cc"), leading=13,
        ))
        add(ParagraphStyle(
            name="StatNum", fontName="Helvetica-Bold", fontSize=12.5,
            textColor=ACCENT, leading=14, alignment=TA_CENTER,
        ))
        add(ParagraphStyle(
            name="StatLabel", fontName="Helvetica", fontSize=7.2,
            textColor=MUTED, leading=9, alignment=TA_CENTER,
        ))
        add(ParagraphStyle(
            name="Section", fontName="Helvetica-Bold", fontSize=10.5,
            textColor=ACCENT, leading=12, spaceBefore=0, spaceAfter=2,
        ))
        add(ParagraphStyle(
            name="Summary", fontName="Helvetica", fontSize=9.4,
            textColor=INK, leading=13, alignment=TA_LEFT,
        ))
        add(ParagraphStyle(
            name="Role", fontName="Helvetica-Bold", fontSize=10,
            textColor=INK, leading=12,
        ))
        add(ParagraphStyle(
            name="Company", fontName="Helvetica", fontSize=9.2,
            textColor=ACCENT, leading=12,
        ))
        add(ParagraphStyle(
            name="Date", fontName="Helvetica", fontSize=8.4,
            textColor=MUTED, leading=12, alignment=TA_RIGHT,
        ))
        add(ParagraphStyle(
            name="ExpBullet", fontName="Helvetica", fontSize=8.9,
            textColor=HexColor("#33373d"), leading=11.3,
            leftIndent=10, bulletIndent=0, spaceAfter=0.5,
        ))
        add(ParagraphStyle(
            name="SkillCat", fontName="Helvetica-Bold", fontSize=8.8,
            textColor=INK, leading=12,
        ))
        add(ParagraphStyle(
            name="SkillVal", fontName="Helvetica", fontSize=8.8,
            textColor=HexColor("#33373d"), leading=12,
        ))
        add(ParagraphStyle(
            name="Project", fontName="Helvetica-Bold", fontSize=9,
            textColor=INK, leading=12.5,
        ))
        add(ParagraphStyle(
            name="ProjectDesc", fontName="Helvetica", fontSize=8.8,
            textColor=HexColor("#33373d"), leading=12.5,
        ))
        add(ParagraphStyle(
            name="Tech", fontName="Helvetica-Oblique", fontSize=7.8,
            textColor=MUTED, leading=11,
        ))
        add(ParagraphStyle(
            name="EduTitle", fontName="Helvetica-Bold", fontSize=9.2,
            textColor=INK, leading=12.5,
        ))
        add(ParagraphStyle(
            name="EduMeta", fontName="Helvetica", fontSize=8.6,
            textColor=MUTED, leading=10.5,
        ))

    # ---- Document --------------------------------------------------------
    def generate_cv_pdf(self, context_data):
        buffer = io.BytesIO()

        doc = BaseDocTemplate(
            buffer,
            pagesize=self.PAGE_SIZE,
            leftMargin=self.MARGIN,
            rightMargin=self.MARGIN,
            topMargin=self.MARGIN,
            bottomMargin=10 * mm,
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
        elements.append(Spacer(1, 5))
        elements += self._highlights()
        elements.append(Spacer(1, 5))
        elements += self._summary()
        elements += self._experience()
        elements += self._bottom()

        doc.build(elements)
        pdf_value = buffer.getvalue()
        buffer.close()
        return io.BytesIO(pdf_value)

    # ---- Footer ----------------------------------------------------------
    def _draw_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            self.MARGIN, 7 * mm,
            "Vasile Ovidiu Ichim · Staff Engineer & Technical Lead",
        )
        canvas.drawRightString(
            self.PAGE_SIZE[0] - self.MARGIN, 7 * mm,
            "github.com/zabbix-byte",
        )
        canvas.restoreState()

    # ---- Sections --------------------------------------------------------
    def _header(self, ctx):
        name = ctx.get("name", "Vasile Ovidiu Ichim")
        title = ctx.get("title", "Staff Engineer &amp; Technical Lead · Software Architect")
        location = ctx.get("location", "Barcelona, Spain")
        email = ctx.get("email", "zabbix@ztrunk.space")

        def link(url, label):
            return f'<a href="{url}" color="#7db8ff">{label}</a>'

        linkedin = (
            link("https://www.linkedin.com/in/zabbix-byte/", "linkedin.com/in/zabbix-byte")
            + ' <font color="#9aa0a6">(preferred)</font>'
        )
        contact = "&nbsp;&nbsp;·&nbsp;&nbsp;".join([
            location,
            linkedin,
            link(f"mailto:{email}", email),
            link("https://github.com/zabbix-byte", "github.com/zabbix-byte"),
        ])

        inner = [
            Paragraph(name, self.styles["Name"]),
            Paragraph(title, self.styles["JobTitle"]),
            Paragraph(contact, self.styles["Contact"]),
        ]
        header = Table([[inner]], colWidths=[self.content_width])
        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), DARK),
            ("LEFTPADDING", (0, 0), (-1, -1), 16),
            ("RIGHTPADDING", (0, 0), (-1, -1), 16),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("ROUNDEDCORNERS", [8, 8, 8, 8]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        return [header]

    def _highlights(self):
        stats = [
            ("7+ yrs", "Engineering"),
            ("IBM · Inditex", "Enterprise track record"),
            ("10TB+ / day", "Data processed (Spark)"),
            ("0 → 1", "Platform built hands-on"),
        ]
        # Each stat becomes its own mini-table to stack number over label
        col = self.content_width / 4.0
        row = []
        for num, label in stats:
            mini = Table(
                [[Paragraph(num, self.styles["StatNum"])],
                 [Paragraph(label, self.styles["StatLabel"])]],
                colWidths=[col - 6],
            )
            mini.setStyle(TableStyle([
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 0),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]))
            row.append(mini)

        strip = Table([row], colWidths=[col] * 4)
        strip.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LINEAFTER", (0, 0), (-2, -1), 0.5, LINE),
        ]))
        return [strip]

    def _section_header(self, text):
        return [
            Paragraph(text.upper(), self.styles["Section"]),
            HRFlowable(width="100%", thickness=1.2, color=ACCENT,
                       spaceBefore=0, spaceAfter=3, lineCap="round"),
        ]

    def _summary(self):
        text = (
            "Staff-level engineer and software architect with 7+ years building data-intensive "
            "platforms — distributed pipelines, ML forecasting, multi-tenant SaaS and LLM-powered "
            "products. Co-founder and CTO of an AI procurement startup, where I re-architected the "
            "platform for 10TB+/day; enterprise background across <b>IBM</b> and <b>Inditex</b>. "
            "Hands-on with Python, Django, AWS, Databricks and Kubernetes."
        )
        press = (
            'Featured in <a href="https://www.viaempresa.cat/es/empresa/'
            'como-inteligencia-artificial-redefine-cadena-suministro-caso-valerdat_2202088_102.html" '
            'color="#0071e3"><b>VIA Empresa</b></a>'
            ' · Customer case studies: <a href="https://valerdat.com/casosdeexito" '
            'color="#0071e3">valerdat.com/casosdeexito</a>'
        )
        return self._section_header("Profile") + [
            Paragraph(text, self.styles["Summary"]),
            Spacer(1, 2),
            Paragraph(press, self.styles["Tech"]),
            Spacer(1, 1),
        ]

    def _exp_entry(self, role, company, dates, bullets):
        head = Table(
            [[Paragraph(f"{role} · <font color='#0071e3'>{company}</font>", self.styles["Role"]),
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
        flow.append(Spacer(1, 2))
        return KeepTogether(flow)

    def _experience(self):
        entries = [
            self._exp_entry(
                "Co-founder &amp; CTO", "Valerdat", "2021 – Present",
                [
                    "Re-architected the platform end to end to process 10TB+/day with Spark and serve near-instant responses; demand forecasting at &lt;5% MAPE.",
                    "Owned the full stack: distributed ETL (Databricks/Spark), a multi-tenant Django backend, and AWS infra, observability &amp; security.",
                    "Delivered multi-ERP connectors — Sage 200, Microsoft Dynamics 365 Business Central — via API/SFTP, listed on the Sage Marketplace.",
                    "Founding engineer turned CTO by team decision — sole engineer transversal across the stack, still hands-on and setting direction.",
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
                    "First role and best school — hands-on with everything: physical servers, networking &amp; security (MikroTik), Linux services (Apache/Nginx) and Python web apps.",
                    "Developed Sage 50 ERP extensions and custom reports — the early roots of the ERP integration work I lead today.",
                ],
            ),
        ]
        return self._section_header("Experience") + entries

    def _skills_block(self):
        rows = [
            ("Languages", "Python (expert), C/C++, JavaScript/TypeScript, SQL, Bash"),
            ("Backend &amp; Data", "Django, FastAPI, REST, Celery, Redis, PostgreSQL, Databricks, Spark, ETL"),
            ("Cloud &amp; DevOps", "AWS, Docker, Kubernetes, Terraform, CI/CD, Linux"),
            ("AI, ML &amp; Architecture", "Forecasting (Prophet, ARIMA, XGBoost, NHITS, TFT), LLM integration, distributed systems, multi-tenant SaaS, ERP integrations"),
            ("Technical Leadership", "Architecture &amp; design reviews, technical direction, mentoring"),
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
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))
        return self._section_header("Skills") + [t]

    def _project_cell(self, name, desc, tech):
        mini = Table(
            [[Paragraph(name, self.styles["Project"])],
             [Paragraph(desc, self.styles["ProjectDesc"])],
             [Paragraph(tech, self.styles["Tech"])]],
            colWidths=[self.content_width / 2 - 5 * mm],
        )
        mini.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        return mini

    def _projects_block(self):
        p = [
            self._project_cell(
                "AI Procurement Platform",
                "AI-powered MRP: demand forecasting (Prophet, XGBoost, TFT) at &lt;5% MAPE, optimization and LLMs.",
                "Forecasting · Optimization · LLM · Python"),
            self._project_cell(
                "Distributed ETL Engine",
                "Databricks/Spark pipelines processing 10TB+ of data daily.",
                "Databricks · Spark · ETL"),
            self._project_cell(
                "Multi-ERP Connector Layer",
                "Integrations with Sage 200, Dynamics 365 Business Central and others (API/SFTP).",
                "Sage Marketplace · API · SFTP"),
            self._project_cell(
                "Multi-Tenant SaaS Core",
                "Isolated data, RBAC and per-tenant scaling for enterprise.",
                "Django · PostgreSQL"),
        ]
        gutter = 10 * mm
        col_w = (self.content_width - gutter) / 2.0
        grid = Table(
            [[p[0], p[1]], [p[2], p[3]]],
            colWidths=[col_w, col_w],
        )
        grid.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (0, -1), 0),
            ("RIGHTPADDING", (0, 0), (0, -1), gutter),
            ("LEFTPADDING", (1, 0), (1, -1), gutter),
            ("RIGHTPADDING", (1, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, 0), 0),
            ("TOPPADDING", (0, 1), (-1, 1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return self._section_header("Featured Projects") + [grid]

    def _edu_block(self):
        edu = Table(
            [[Paragraph("B.Sc. Computer Science — <font color='#6b7280'>The Open University</font>",
                        self.styles["EduTitle"]),
              Paragraph("2023 – 2027 (in progress)", self.styles["Date"])]],
            colWidths=[self.content_width * 0.74, self.content_width * 0.26],
        )
        edu.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        flow = self._section_header("Education &amp; Certifications")
        flow.append(edu)
        flow.append(Spacer(1, 2))
        flow.append(Paragraph(
            "<b>Certifications:</b> AWS Cloud (Practical) · FastAPI — Backend APIs",
            self.styles["EduMeta"]))
        flow.append(Paragraph(
            "<b>Languages:</b> Romanian (native) · Spanish (fluent, C2) · English (professional, C1)",
            self.styles["EduMeta"]))
        return flow

    def _bottom(self):
        flow = [Spacer(1, 1)]
        flow += self._skills_block()
        flow.append(Spacer(1, 3))
        flow += self._projects_block()
        flow.append(Spacer(1, 2))
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
