"""
PDF generation service for CV
Creates professional Harvard-style CV in PDF format
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from django.http import HttpResponse


class CVPDFGenerator:
    """Professional Harvard-style CV PDF generator"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom styles for Harvard CV format"""

        # Harvard-style header - name in large, elegant font
        self.styles.add(
            ParagraphStyle(
                name="HarvardName",
                parent=self.styles["Title"],
                fontSize=28,
                textColor=black,
                spaceAfter=3,
                alignment=TA_CENTER,
                fontName="Times-Bold",
            )
        )

        # Contact info style - smaller, centered
        self.styles.add(
            ParagraphStyle(
                name="HarvardContact",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=black,
                spaceAfter=18,
                alignment=TA_CENTER,
                fontName="Times-Roman",
            )
        )

        # Harvard section headers - all caps, bold, with line underneath
        self.styles.add(
            ParagraphStyle(
                name="HarvardSectionHeader",
                parent=self.styles["Heading1"],
                fontSize=12,
                textColor=black,
                spaceAfter=6,
                spaceBefore=18,
                fontName="Times-Bold",
                alignment=TA_LEFT,
                borderWidth=0,
                leftIndent=0,
                bulletIndent=0,
            )
        )

        # Institution/Company style - italics for Harvard look
        self.styles.add(
            ParagraphStyle(
                name="HarvardInstitution",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=black,
                spaceAfter=2,
                fontName="Times-Italic",
                alignment=TA_LEFT,
            )
        )

        # Position/Degree title - bold
        self.styles.add(
            ParagraphStyle(
                name="HarvardPosition",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=black,
                spaceAfter=2,
                fontName="Times-Bold",
                alignment=TA_LEFT,
            )
        )

        # Date range - right aligned, smaller
        self.styles.add(
            ParagraphStyle(
                name="HarvardDate",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=black,
                spaceAfter=2,
                fontName="Times-Roman",
                alignment=TA_RIGHT,
            )
        )

        # Description text - justified, indented
        self.styles.add(
            ParagraphStyle(
                name="HarvardDescription",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=black,
                spaceAfter=8,
                fontName="Times-Roman",
                alignment=TA_JUSTIFY,
                leftIndent=12,
                rightIndent=12,
            )
        )

        # Professional summary style
        self.styles.add(
            ParagraphStyle(
                name="HarvardSummary",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=black,
                spaceAfter=12,
                fontName="Times-Roman",
                alignment=TA_JUSTIFY,
                leftIndent=0,
                rightIndent=0,
            )
        )

    def generate_cv_pdf(self, context_data):
        """Generate the complete CV PDF"""

        # Create PDF buffer
        buffer = io.BytesIO()

        # Create document with Harvard-style margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        # Build document elements
        elements = []

        # Header section
        elements.extend(self._build_header_section(context_data))

        # Professional summary
        elements.extend(self._build_summary_section())

        # Experience section
        elements.extend(self._build_experience_section(context_data))

        # Skills section
        elements.extend(self._build_skills_section(context_data))

        # Education section
        elements.extend(self._build_education_section())

        # Projects section
        elements.extend(self._build_projects_section(context_data))

        # Build PDF
        doc.build(elements)

        # Return buffer
        pdf_value = buffer.getvalue()
        buffer.close()

        return io.BytesIO(pdf_value)

    def _build_header_section(self, context_data):
        """Build CV header with name and contact info"""
        elements = []

        # Name
        name = Paragraph("VASILE OVIDIU ICHIM", self.styles["HarvardName"])
        elements.append(name)

        # Contact information in Harvard style
        contact_info = """

        Barcelona, Spain | zabbix@ztrunk.space | github.com/zabbix-byte
        """
        contact = Paragraph(contact_info, self.styles["HarvardContact"])
        elements.append(contact)

        # Add horizontal rule below header
        elements.append(
            HRFlowable(width="100%", thickness=1, lineCap="round", color=black)
        )
        elements.append(Spacer(1, 12))

        return elements

    def _build_summary_section(self):
        """Build professional summary section"""
        elements = []

        # Section header
        header = Paragraph("PROFESSIONAL SUMMARY", self.styles["HarvardSectionHeader"])
        elements.append(header)

        # Add underline for section
        elements.append(
            HRFlowable(width="100%", thickness=0.5, lineCap="round", color=black)
        )
        elements.append(Spacer(1, 6))

        # Professional summary - concise and authentic
        summary = """
        Technical Lead and Co-Founder with 7+ years of software engineering experience, specializing in full-stack development, cloud infrastructure, and system architecture. Experience includes enterprise infrastructure management at IBM and developing solutions for Inditex through Knowmad Mood.

Core expertise in Python, Django, JavaScript, AWS, and DevOps automation. Currently leading technical strategy and development teams at Valerdat, building data-driven SaaS solutions for procurement and supply chain optimization.

Passionate about building scalable, maintainable software and mentoring engineering teams. Continuously learning through part-time Computer Science degree while staying current with emerging technologies.
        """

        summary_p = Paragraph(summary, self.styles["HarvardSummary"])
        elements.append(summary_p)

        elements.append(Spacer(1, 12))

        return elements

    def _build_experience_section(self, context_data):
        """Build professional experience section"""
        elements = []

        # Section header
        header = Paragraph(
            "PROFESSIONAL EXPERIENCE", self.styles["HarvardSectionHeader"]
        )
        elements.append(header)

        # Add underline for section
        elements.append(
            HRFlowable(width="100%", thickness=0.5, lineCap="round", color=black)
        )
        elements.append(Spacer(1, 8))

        # Valerdat experience
        company1 = Paragraph("<i>Valerdat</i>", self.styles["HarvardInstitution"])
        elements.append(company1)

        position_data1 = [
            [
                Paragraph("Co-founder & Tech Lead", self.styles["HarvardPosition"]),
                Paragraph("March 2022 - Present", self.styles["HarvardDate"]),
            ]
        ]
        position_table1 = Table(position_data1, colWidths=[4 * inch, 2 * inch])
        position_table1.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        elements.append(position_table1)

        valerdat_desc = """• Co-founded and lead technical development of AI-powered intelligent purchasing assistant for supply chain optimization
• Architected Next-Gen MRP platform using machine learning for demand prediction and automated purchase order generation
• Led development team of 5 engineers building scalable data pipelines using Databricks processing 120K+ product references
• Designed RESTful APIs and backend systems connecting real-time data from demand, stock, suppliers, and external variables
• Implemented probabilistic forecasting models to predict sales and optimize inventory policies dynamically
• Established engineering best practices including code reviews, automated testing (pytest, unittest), and documentation
• Managed AWS cloud infrastructure and data processing workflows supporting enterprise procurement operations
• Technologies: Python, Django, PostgreSQL, Redis, Celery, Docker, Databricks, Machine Learning, React, AWS, Terraform"""
        desc1 = Paragraph(valerdat_desc, self.styles["HarvardDescription"])
        elements.append(desc1)

        # Knowmad Mood experience (Inditex client)
        company2 = Paragraph(
            "<i>Knowmad Mood (Client: Inditex)</i>", self.styles["HarvardInstitution"]
        )
        elements.append(company2)

        position_data2 = [
            [
                Paragraph("Senior Software Engineer", self.styles["HarvardPosition"]),
                Paragraph("March 2022 - March 2024", self.styles["HarvardDate"]),
            ]
        ]
        position_table2 = Table(position_data2, colWidths=[4 * inch, 2 * inch])
        position_table2.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        elements.append(position_table2)

        knowmad_desc = """• Developed strategic planning platform for Inditex's Security Department managing supply chain operations
• Built enterprise web applications using Django, React, and Node.js serving internal Inditex teams
• Implemented microservices architecture improving system scalability and performance
• Designed RESTful APIs for web and mobile platforms used by security and operations staff
• Optimized PostgreSQL database queries for complex reporting and analytics
• Collaborated with international teams using agile methodologies and JIRA
• Deployed applications using Docker containers and implemented CI/CD pipelines
• Technologies: Python, Django REST Framework, React.js, PostgreSQL, MongoDB, Redis, AWS"""
        desc2 = Paragraph(knowmad_desc, self.styles["HarvardDescription"])
        elements.append(desc2)

        # IBM experience
        company3 = Paragraph("<i>IBM</i>", self.styles["HarvardInstitution"])
        elements.append(company3)

        position_data3 = [
            [
                Paragraph("System Administrator", self.styles["HarvardPosition"]),
                Paragraph("February 2021 - March 2022", self.styles["HarvardDate"]),
            ]
        ]
        position_table3 = Table(position_data3, colWidths=[4 * inch, 2 * inch])
        position_table3.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        elements.append(position_table3)

        ibm_desc = """• Managed 200+ Linux servers (RHEL, Ubuntu) ensuring 99.95% availability for mission-critical applications
• Automated system administration tasks using Python and Bash reducing manual effort by 60%
• Implemented monitoring solutions (Nagios, Prometheus, Grafana) improving incident response time by 40%
• Optimized system performance identifying bottlenecks and implementing security patches (SELinux, firewall rules)
• Collaborated with global DevOps teams managing infrastructure for Fortune 500 enterprise clients
• Developed Python automation scripts for log analysis, backup management, and resource provisioning
• Participated in on-call rotation providing 24/7 support for production infrastructure
• Technologies: Linux (RHEL/Ubuntu), Python, Bash, Ansible, Docker, Jenkins, Git, VMware"""
        desc3 = Paragraph(ibm_desc, self.styles["HarvardDescription"])
        elements.append(desc3)

        # DATAXIP experience
        company4 = Paragraph("<i>DATAXIP SL</i>", self.styles["HarvardInstitution"])
        elements.append(company4)

        position_data4 = [
            [
                Paragraph(
                    "Developer and System Administrator", self.styles["HarvardPosition"]
                ),
                Paragraph("February 2018 - February 2021", self.styles["HarvardDate"]),
            ]
        ]
        position_table4 = Table(position_data4, colWidths=[4 * inch, 2 * inch])
        position_table4.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        elements.append(position_table4)

        dataxip_desc = """• Developed full-stack web applications using Django, Vue.js, and modern JavaScript frameworks
• Implemented AWS cloud services (EC2, S3, RDS, CloudFront) reducing infrastructure costs by 25%
• Designed and optimized MySQL/PostgreSQL databases supporting 100K+ records with efficient indexing
• Built RESTful APIs and integrated third-party services (Stripe payments, SendGrid, Google Analytics)
• Established DevOps practices including automated deployments, version control (Git), and staging environments
• Managed client relationships delivering projects on-time with 95%+ satisfaction rate
• Implemented responsive UI/UX designs ensuring mobile-first approach and accessibility standards
• Technologies: Python, Django, Vue.js, MySQL, AWS, Docker, Nginx, Git, Bootstrap"""
        desc4 = Paragraph(dataxip_desc, self.styles["HarvardDescription"])
        elements.append(desc4)

        elements.append(Spacer(1, 12))

        return elements

    def _build_skills_section(self, context_data):
        """Build skills section"""
        elements = []

        # Section header
        header = Paragraph(
            "TECHNICAL SKILLS & EXPERTISE", self.styles["HarvardSectionHeader"]
        )
        elements.append(header)

        # Add underline for section
        elements.append(
            HRFlowable(width="100%", thickness=0.5, lineCap="round", color=black)
        )
        elements.append(Spacer(1, 6))

        # Programming & Development
        leadership_header = Paragraph(
            "Programming Languages & Frameworks:", self.styles["HarvardPosition"]
        )
        elements.append(leadership_header)

        leadership_skills = """
        Python (Expert) • Django • Flask • FastAPI • JavaScript/TypeScript • Node.js • React.js • Vue.js • 
        C/C++ • Bash Scripting • SQL • GraphQL • HTML5/CSS3 • Tailwind CSS
        """
        leadership_p = Paragraph(leadership_skills, self.styles["HarvardDescription"])
        elements.append(leadership_p)

        # Databases & Cloud
        tech_header = Paragraph(
            "Databases, Cloud & DevOps:", self.styles["HarvardPosition"]
        )
        elements.append(tech_header)

        tech_skills = """
        PostgreSQL • MySQL • MongoDB • Redis • AWS (EC2, S3, RDS, Lambda) • Docker • Kubernetes • 
        CI/CD (Jenkins, GitLab CI) • Terraform • Nginx • Linux (RHEL, Ubuntu) • Ansible
        """
        tech_p = Paragraph(tech_skills, self.styles["HarvardDescription"])
        elements.append(tech_p)

        # Architecture & Leadership
        infra_header = Paragraph(
            "Software Engineering & Leadership:", self.styles["HarvardPosition"]
        )
        elements.append(infra_header)

        infra_skills = """
        Microservices Architecture • RESTful API Design • System Design • TDD/BDD • Unit Testing • 
        Technical Leadership • Team Management • Agile/Scrum • Code Review • Mentoring
        """
        infra_p = Paragraph(infra_skills, self.styles["HarvardDescription"])
        elements.append(infra_p)

        elements.append(Spacer(1, 12))

        return elements

    def _build_education_section(self):
        """Build education section"""
        elements = []

        # Section header
        header = Paragraph("EDUCATION", self.styles["HarvardSectionHeader"])
        elements.append(header)

        # Add underline for section
        elements.append(
            HRFlowable(width="100%", thickness=0.5, lineCap="round", color=black)
        )
        elements.append(Spacer(1, 6))

        # CS Degree
        degree = Paragraph(
            "Bachelor's Degree, Computer Science (In Progress)",
            self.styles["HarvardPosition"],
        )
        elements.append(degree)

        university = Paragraph("The Open University", self.styles["HarvardInstitution"])
        elements.append(university)

        edu_date = Paragraph(
            "September 2023 - September 2027", self.styles["HarvardDate"]
        )
        elements.append(edu_date)

        edu_desc = """
        Currently pursuing Bachelor's degree in Computer Science through The Open University 
        while maintaining full-time professional responsibilities. Focus on advanced computer 
        science fundamentals, software engineering principles, and emerging technologies.
        """
        edu_desc_p = Paragraph(edu_desc, self.styles["HarvardDescription"])
        elements.append(edu_desc_p)

        elements.append(Spacer(1, 12))

        return elements

    def _build_projects_section(self, context_data):
        """Build featured projects section"""
        elements = []

        # Section header
        header = Paragraph("FEATURED PROJECTS", self.styles["HarvardSectionHeader"])
        elements.append(header)

        # Add underline for section
        elements.append(
            HRFlowable(width="100%", thickness=0.5, lineCap="round", color=black)
        )
        elements.append(Spacer(1, 6))

        # Get GitHub repositories from context
        github_repos = context_data.get("github_repositories", [])

        # Featured projects with priority order
        featured_projects = [
            "NFT-Generator",
            "ztdriver",
            "ztui",
            "zt_cs_cheat",
            "PyPulse",
            "DiscordEasyCloner",
        ]

        # Sort repos to prioritize featured projects
        priority_repos = []
        other_repos = []

        for repo in github_repos:
            if repo.get("name") in featured_projects:
                priority_repos.append(repo)
            else:
                other_repos.append(repo)

        # Sort priority repos by featured order
        priority_repos.sort(
            key=lambda x: (
                featured_projects.index(x.get("name"))
                if x.get("name") in featured_projects
                else 999
            )
        )

        # Combine lists (priority first, then others sorted by stars)
        other_repos.sort(key=lambda x: x.get("stargazers_count", 0), reverse=True)
        display_repos = priority_repos + other_repos

        if display_repos:
            for i, repo in enumerate(display_repos[:6]):  # Show top 6 projects
                project_name = Paragraph(
                    f"{repo.get('name', 'N/A')}", self.styles["HarvardPosition"]
                )
                elements.append(project_name)

                project_desc = repo.get("description", "No description available")
                if project_desc:
                    # Clean and format description
                    clean_desc = (
                        project_desc.replace("💀", "").replace("🔥", "").strip()
                    )
                    if len(clean_desc) > 100:
                        clean_desc = clean_desc[:97] + "..."
                    desc_p = Paragraph(
                        f"• {clean_desc}", self.styles["HarvardDescription"]
                    )
                    elements.append(desc_p)

                # Technical details with enhanced formatting
                language = repo.get("language", "N/A")
                stars = repo.get("stargazers_count", 0)
                forks = repo.get("forks_count", 0)

                tech_details = []
                if language != "N/A":
                    tech_details.append(f"Language: {language}")
                if stars > 0:
                    tech_details.append(f"⭐ {stars} stars")
                if forks > 0:
                    tech_details.append(f"🍴 {forks} forks")

                if tech_details:
                    tech_info = f"<i>{' | '.join(tech_details)}</i>"
                    tech_p = Paragraph(tech_info, self.styles["HarvardDate"])
                    elements.append(tech_p)

                # Add URL for featured projects
                if repo.get("name") in featured_projects[:3]:  # Top 3 projects get URLs
                    url_p = Paragraph(
                        f"<i>github.com/zabbix-byte/{repo.get('name')}</i>",
                        self.styles["HarvardDate"],
                    )
                    elements.append(url_p)

                if i < 5:  # Add spacing between projects
                    elements.append(Spacer(1, 8))
        else:
            # Enhanced fallback with specific project highlights
            fallback_desc = """• <b>NFT-Generator</b>: Advanced Python-based NFT generation system with customizable base art and metadata processing
• <b>ztdriver & ztui</b>: Sophisticated kernel driver with C++ implementation and integrated user interface for system-level operations
• <b>zt_cs_cheat</b>: Comprehensive game modification toolkit featuring ESP, AIM, BHOP, and RAGE capabilities with DLL loading
• <b>PyPulse & DiscordEasyCloner</b>: Desktop application frameworks demonstrating Python GUI development and automation expertise
• Specialized focus on system-level programming, reverse engineering, and performance-critical applications
• Technologies: Python, C++, Kernel Development, GUI Frameworks, Game Engine Integration"""
            fallback_p = Paragraph(fallback_desc, self.styles["HarvardDescription"])
            elements.append(fallback_p)

        return elements


def generate_cv_pdf_response(context_data):
    """Generate PDF response for CV download"""

    generator = CVPDFGenerator()
    pdf_buffer = generator.generate_cv_pdf(context_data)

    # Create HTTP response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        'attachment; filename="Vasile_Ovidiu_Ichim_CV.pdf"'
    )
    response.write(pdf_buffer.getvalue())

    return response
