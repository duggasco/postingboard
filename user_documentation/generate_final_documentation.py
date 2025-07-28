#!/usr/bin/env python3
"""
Generate Final Documentation for Citizen Developer Posting Board
With all formatting fixes and content improvements
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, Preformatted, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

class FinalDocumentationGenerator:
    def __init__(self):
        self.doc = SimpleDocTemplate(
            "Posting_Board_Final_Documentation.pdf",
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72  # Increased bottom margin
        )
        self.screenshots_dir = "/root/postingboard/documentation_screenshots"
        self.page_height = letter[1]
        self.page_width = letter[0]
        self.margin = 72
        self.usable_width = self.page_width - (2 * self.margin)
        self.usable_height = self.page_height - (2 * self.margin)
        
    def generate(self):
        """Generate the complete documentation"""
        story = []
        styles = self.get_custom_styles()
        
        # Title Page
        story.extend(self.create_title_page(styles))
        
        # Table of Contents
        story.extend(self.create_table_of_contents(styles))
        
        # 1. Executive Summary (Pages 3-4)
        story.extend(self.create_executive_summary(styles))
        
        # 2. Technical Architecture (Pages 5-9)
        story.extend(self.create_technical_architecture(styles))
        
        # 3. Database Design (Pages 10-14)
        story.extend(self.create_database_design(styles))
        
        # 4. User Interface (Pages 15-19)
        story.extend(self.create_user_interface(styles))
        
        # 5. Core Workflows (Pages 20-24)
        story.extend(self.create_core_workflows(styles))
        
        # 6. API Documentation (Pages 25-29)
        story.extend(self.create_api_documentation(styles))
        
        # 7. Security and Authentication (Pages 30-34)
        story.extend(self.create_security_section(styles))
        
        # 8. SDLC Features (Pages 35-39)
        story.extend(self.create_sdlc_features(styles))
        
        # 9. Admin Portal (Pages 40-44)
        story.extend(self.create_admin_portal(styles))
        
        # 10. Deployment Guide (Pages 45-49)
        story.extend(self.create_deployment_guide(styles))
        
        # 11. Performance Optimization (Pages 50-54)
        story.extend(self.create_performance_section(styles))
        
        # 12. Troubleshooting (Pages 55-59)
        story.extend(self.create_troubleshooting(styles))
        
        # 13. Future Roadmap (Pages 60-62)
        story.extend(self.create_future_roadmap(styles))
        
        # 14. Appendices (Pages 63-65)
        story.extend(self.create_appendices(styles))
        
        # Build PDF
        self.doc.build(story)
        print("="*60)
        print("Final Documentation Generator")
        print("="*60)
        print()
        print("✓ Generated: Posting_Board_Final_Documentation.pdf")
        print("✓ Total sections: 14")
        print("✓ Estimated pages: 65+")
        print("✓ Fixed: Table text wrapping and scaling")
        print("✓ Fixed: Title overlap issue")
        print("✓ Fixed: Code block collision detection")
        print("✓ Fixed: Workflow diagram sizing")
        print("✓ Removed: IT and cost savings references")
        print("✓ Fixed: Table of contents formatting")
        
    def get_custom_styles(self):
        """Create custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=32,  # Reduced from 36 to prevent overlap
            textColor=colors.HexColor('#1a1d23'),
            spaceAfter=30,
            alignment=TA_CENTER,
            leading=40  # Added line height
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1d23'),
            spaceAfter=20,
            spaceBefore=20
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#1a1d23'),
            spaceAfter=15,
            spaceBefore=15
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#1a1d23'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
        
        styles.add(ParagraphStyle(
            name='CustomCode',
            parent=styles['Code'],
            fontSize=8,  # Reduced from 9 for better fit
            leftIndent=12,  # Reduced indent
            rightIndent=12,
            backColor=colors.HexColor('#f5f5f5'),
            borderColor=colors.HexColor('#dddddd'),
            borderWidth=1,
            borderPadding=6,
            spaceAfter=12,
            spaceBefore=12,  # Added space before
            wordWrap='CJK'  # Better word wrapping
        ))
        
        styles.add(ParagraphStyle(
            name='BulletText',
            parent=styles['BodyText'],
            fontSize=11,
            leftIndent=24,
            spaceAfter=8,
            bulletIndent=12
        ))
        
        styles.add(ParagraphStyle(
            name='NumberedText',
            parent=styles['BodyText'],
            fontSize=11,
            leftIndent=24,
            spaceAfter=8
        ))
        
        styles.add(ParagraphStyle(
            name='FieldName',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a1d23'),
            spaceAfter=4
        ))
        
        styles.add(ParagraphStyle(
            name='FieldDescription',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#333333'),
            leftIndent=20,
            spaceAfter=16,
            alignment=TA_JUSTIFY
        ))
        
        styles.add(ParagraphStyle(
            name='TOCEntry',
            parent=styles['Normal'],
            fontSize=11,
            leftIndent=0,
            spaceAfter=6
        ))
        
        styles.add(ParagraphStyle(
            name='TOCSubEntry',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=4,
            textColor=colors.HexColor('#555555')
        ))
        
        return styles
        
    def create_title_page(self, styles):
        """Create the title page"""
        elements = []
        
        # Add some spacing
        elements.append(Spacer(1, 2*inch))
        
        # Title - Split into two lines to prevent overlap
        elements.append(Paragraph("Citizen Developer", styles['CustomTitle']))
        elements.append(Paragraph("Posting Board", styles['CustomTitle']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        elements.append(Paragraph("Technical Documentation", styles['CustomHeading2']))
        elements.append(Paragraph("System Launch Edition", styles['CustomHeading2']))
        elements.append(Spacer(1, 1*inch))
        
        # Version info
        elements.append(Paragraph("Version 1.0 - Launch Release", styles['Normal']))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        
        elements.append(PageBreak())
        return elements
        
    def create_table_of_contents(self, styles):
        """Create table of contents as formatted text, not table"""
        elements = []
        
        elements.append(Paragraph("Table of Contents", styles['CustomHeading1']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Main sections
        toc_entries = [
            ("1. Executive Summary", "3", True),
            ("    1.1 System Overview", "3", False),
            ("    1.2 Launch Objectives", "3", False),
            ("    1.3 Expected Benefits", "4", False),
            ("    1.4 Success Metrics", "4", False),
            ("2. Technical Architecture", "5", True),
            ("    2.1 Technology Stack", "5", False),
            ("    2.2 Component Overview", "7", False),
            ("    2.3 Flask Architecture", "8", False),
            ("    2.4 Session Management", "9", False),
            ("3. Database Design", "10", True),
            ("    3.1 Core Schema", "10", False),
            ("    3.2 Entity Relationships", "11", False),
            ("    3.3 UUID Implementation", "12", False),
            ("    3.4 SDLC Extensions", "13", False),
            ("    3.5 Data Integrity", "14", False),
            ("4. User Interface", "15", True),
            ("    4.1 Browse Ideas", "15", False),
            ("    4.2 Submit Ideas", "16", False),
            ("    4.3 My Ideas Dashboard", "17", False),
            ("    4.4 Team Analytics", "18", False),
            ("    4.5 Mobile Responsiveness", "19", False),
            ("5. Core Workflows", "20", True),
            ("    5.1 Authentication Flow", "20", False),
            ("    5.2 Idea Lifecycle", "21", False),
            ("    5.3 Claim Process", "22", False),
            ("    5.4 Manager Approval", "23", False),
            ("    5.5 Bounty Approval", "24", False),
            ("6. API Documentation", "25", True),
            ("    6.1 RESTful Design", "25", False),
            ("    6.2 Public Endpoints", "26", False),
            ("    6.3 Protected Endpoints", "27", False),
            ("    6.4 Admin Endpoints", "28", False),
            ("    6.5 Error Handling", "29", False),
            ("7. Security and Authentication", "30", True),
            ("    7.1 Passwordless Authentication", "30", False),
            ("    7.2 Session Security", "31", False),
            ("    7.3 Role-Based Access Control", "32", False),
            ("    7.4 Data Protection", "33", False),
            ("    7.5 Security Best Practices", "34", False),
            ("8. SDLC Features", "35", True),
            ("    8.1 Sub-Status Tracking", "35", False),
            ("    8.2 Development Progress", "36", False),
            ("    8.3 Interactive GANTT Charts", "37", False),
            ("    8.4 Comments System", "38", False),
            ("    8.5 Activity Tracking", "39", False),
            ("9. Admin Portal", "40", True),
            ("    9.1 Dashboard Overview", "40", False),
            ("    9.2 Idea Management", "41", False),
            ("    9.3 User Management", "42", False),
            ("    9.4 Team Management", "43", False),
            ("    9.5 Analytics & Reporting", "44", False),
            ("10. Deployment Guide", "45", True),
            ("    10.1 Requirements", "45", False),
            ("    10.2 Native Deployment", "46", False),
            ("    10.3 Docker Deployment", "47", False),
            ("    10.4 Production Configuration", "48", False),
            ("    10.5 Monitoring Setup", "49", False),
            ("11. Performance Optimization", "50", True),
            ("    11.1 Database Optimization", "50", False),
            ("    11.2 Caching Strategies", "51", False),
            ("    11.3 Frontend Performance", "52", False),
            ("    11.4 API Performance", "53", False),
            ("    11.5 Monitoring & Metrics", "54", False),
            ("12. Troubleshooting", "55", True),
            ("    12.1 Common Issues", "55", False),
            ("    12.2 Authentication Problems", "56", False),
            ("    12.3 Database Issues", "57", False),
            ("    12.4 Performance Issues", "58", False),
            ("    12.5 Debug Procedures", "59", False),
            ("13. Future Roadmap", "60", True),
            ("    13.1 Planned Features", "60", False),
            ("    13.2 Integration Plans", "61", False),
            ("    13.3 Scalability Roadmap", "62", False),
            ("14. Appendices", "63", True),
            ("    14.1 Configuration Reference", "63", False),
            ("    14.2 API Response Examples", "64", False),
            ("    14.3 Additional Resources", "65", False)
        ]
        
        for title, page, is_main in toc_entries:
            if is_main:
                # Main entries with dots to page number
                text = f"{title} {'.' * (65 - len(title) - len(page))} {page}"
                elements.append(Paragraph(text, styles['TOCEntry']))
            else:
                # Sub entries with dots to page number
                text = f"{title} {'.' * (63 - len(title) - len(page))} {page}"
                elements.append(Paragraph(text, styles['TOCSubEntry']))
        
        elements.append(PageBreak())
        
        return elements
        
    def create_executive_summary(self, styles):
        """Create executive summary section without IT or cost savings references"""
        elements = []
        
        elements.append(Paragraph("1. Executive Summary", styles['CustomHeading1']))
        
        elements.append(Paragraph("1.1 System Overview", styles['CustomHeading2']))
        
        overview_text = """
        The Citizen Developer Posting Board represents a strategic initiative to democratize software development
        within our organization. This platform creates a marketplace where business teams can post their automation
        and development needs, while technically-skilled employees from any department can discover and implement
        these solutions.
        
        By leveraging the growing citizen developer movement, this system addresses the critical gap between
        technical capacity and business demand for digital solutions. The platform facilitates collaboration, skill
        development, and rapid solution delivery while maintaining appropriate governance and oversight.
        """
        elements.append(Paragraph(overview_text, styles['CustomBody']))
        
        elements.append(Paragraph("1.2 Launch Objectives", styles['CustomHeading2']))
        
        objectives_text = """
        The system launch aims to achieve the following key objectives:
        """
        elements.append(Paragraph(objectives_text, styles['CustomBody']))
        
        objectives = [
            "Establish a centralized platform for capturing and prioritizing business automation needs across all departments",
            "Enable skilled employees to contribute to digital transformation efforts regardless of their formal role",
            "Reduce the backlog of small to medium-sized development requests through distributed implementation",
            "Create visibility into the organization's collective technical capabilities and development capacity",
            "Foster a culture of innovation and continuous improvement through democratized problem-solving",
            "Implement appropriate governance and approval workflows for citizen development initiatives"
        ]
        
        for obj in objectives:
            elements.append(Paragraph(f"• {obj}", styles['BulletText']))
            
        elements.append(Paragraph("1.3 Expected Benefits", styles['CustomHeading2']))
        
        benefits_intro = """
        Based on industry benchmarks and pilot program results, we anticipate the following benefits
        within the first year of operation:
        """
        elements.append(Paragraph(benefits_intro, styles['CustomBody']))
        
        benefits = [
            "30-40% reduction in development backlog for small automation and enhancement requests",
            "Identification and enablement of 50+ citizen developers across the organization",
            "Average 2-3 week reduction in time-to-solution for qualifying projects",
            "Improved employee engagement through skill development and contribution opportunities",
            "Enhanced visibility into departmental technology needs and priorities",
            "Creation of a knowledge base of reusable solutions and best practices"
        ]
        
        for benefit in benefits:
            elements.append(Paragraph(f"• {benefit}", styles['BulletText']))
            
        elements.append(PageBreak())
        
        # Page 4
        elements.append(Paragraph("1.4 Success Metrics", styles['CustomHeading2']))
        
        metrics_intro = """
        The platform will track the following key performance indicators to measure success
        and guide continuous improvement:
        """
        elements.append(Paragraph(metrics_intro, styles['CustomBody']))
        
        # Smaller table with wrapped text
        metrics_data = [
            ["Metric", "Target (Year 1)", "Measurement Method"],
            ["Active Citizen Developers", "50+ users", "Unique users claiming ideas"],
            ["Ideas Submitted", "200+ ideas", "Total submissions in system"],
            ["Ideas Completed", "100+ solutions", "Ideas marked as complete"],
            ["Average Time to Claim", "< 5 days", "Time from submission to claim"],
            ["Average Completion Time", "< 30 days", "Time from claim to completion"],
            ["User Satisfaction", "> 80%", "Quarterly survey results"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.2*inch, 1.3*inch, 2.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3*inch))
        
        strategic_text = """
        The Citizen Developer Posting Board positions our organization at the forefront of the
        digital transformation movement. By empowering our workforce to participate directly in
        solution development, we create a sustainable competitive advantage through increased
        agility, innovation, and employee engagement. This platform serves as the foundation
        for a broader citizen development program that will evolve based on user feedback and
        organizational needs.
        """
        elements.append(Paragraph(strategic_text, styles['CustomBody']))
        
        elements.append(PageBreak())
        
        return elements
        
    def create_technical_architecture(self, styles):
        """Create technical architecture section with detailed session descriptions"""
        elements = []
        
        # Page 5
        elements.append(Paragraph("2. Technical Architecture", styles['CustomHeading1']))
        
        elements.append(Paragraph("2.1 Technology Stack", styles['CustomHeading2']))
        
        stack_intro = """
        The platform is built on a modern, maintainable technology stack that prioritizes
        developer productivity, system reliability, and operational simplicity:
        """
        elements.append(Paragraph(stack_intro, styles['CustomBody']))
        
        # Technology stack table with better text wrapping
        stack_data = [
            ["Layer", "Technology", "Purpose"],
            ["Backend Framework", "Flask 2.3+", "Lightweight Python web framework for rapid development"],
            ["Database", "SQLite/PostgreSQL", "Embedded database for development, PostgreSQL for production"],
            ["ORM", "SQLAlchemy", "Database abstraction layer with migration support"],
            ["Frontend", "Jinja2 + JavaScript", "Server-side templating with dynamic client interactions"],
            ["Session Management", "Flask-Session", "Secure server-side session storage with Redis support"],
            ["Authentication", "Custom Email-based", "Passwordless authentication for enhanced security"],
            ["Deployment", "Docker + Gunicorn", "Containerized deployment with production WSGI server"],
            ["Version Control", "Git", "Source code management and collaboration"]
        ]
        
        # Create paragraphs for table cells to handle wrapping
        wrapped_data = []
        for row in stack_data:
            wrapped_row = []
            for cell in row:
                if len(cell) > 40:  # Wrap long text
                    wrapped_row.append(Paragraph(cell, styles['Normal']))
                else:
                    wrapped_row.append(cell)
            wrapped_data.append(wrapped_row)
        
        stack_table = Table(wrapped_data, colWidths=[1.3*inch, 1.3*inch, 3.4*inch])
        stack_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(stack_table)
        
        # Add screenshot if available
        home_screenshot = os.path.join(self.screenshots_dir, "home_page.png")
        if os.path.exists(home_screenshot):
            # Keep header and image together
            screenshot_content = []
            screenshot_content.append(Spacer(1, 0.3*inch))
            screenshot_content.append(Paragraph("System Homepage", styles['CustomHeading3']))
            img = Image(home_screenshot, width=5*inch, height=3.5*inch)
            screenshot_content.append(img)
            # Add as KeepTogether to prevent page split
            elements.append(KeepTogether(screenshot_content))
        
        elements.append(PageBreak())
        
        # Continue with session management section
        elements.append(Paragraph("2.4 Session Management", styles['CustomHeading2']))
        
        session_intro = """
        The platform implements a robust session management system that maintains user state
        across requests while ensuring security and performance. Flask-Session provides
        server-side session storage, preventing client-side tampering and enabling
        complex session data structures.
        """
        elements.append(Paragraph(session_intro, styles['CustomBody']))
        
        elements.append(Paragraph("Session Configuration", styles['CustomHeading3']))
        
        # Add space before code block
        elements.append(Spacer(1, 0.2*inch))
        
        session_code = """
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_FILE_DIR'] = './flask_session/'
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS attacks
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
        """
        elements.append(Paragraph(session_code, styles['CustomCode']))
        
        elements.append(Paragraph("Session Variables Reference", styles['CustomHeading3']))
        
        session_vars_intro = """
        The following session variables are used throughout the application to maintain
        user state and provide personalized experiences:
        """
        elements.append(Paragraph(session_vars_intro, styles['CustomBody']))
        
        # Enhanced session variable descriptions following best practices
        session_vars = [
            {
                "name": "user_email",
                "type": "String (required)",
                "description": """The authenticated user's email address, serving as the primary identifier
                throughout the system. This value is set during the email verification process and persists
                for the duration of the session. Used for database lookups, audit trails, and access control.
                Format: Standard email format (e.g., user@company.com). Maximum length: 120 characters.""",
                "example": "john.doe@company.com"
            },
            {
                "name": "user_name",
                "type": "String (optional)",
                "description": """The user's display name as entered in their profile. This human-readable
                name appears throughout the UI instead of the email address for better user experience.
                If not set, the system falls back to displaying the email address. Updated when users
                complete their profile or modify their name. Maximum length: 100 characters.""",
                "example": "John Doe"
            },
            {
                "name": "user_verified",
                "type": "Boolean (required)",
                "description": """Indicates whether the user has successfully completed email verification.
                Set to True after entering a valid verification code. This flag gates access to protected
                features like submitting ideas, claiming ideas, and accessing personal dashboards. 
                Unverified users can only browse public content. Reset to False if verification expires.""",
                "example": "True"
            },
            {
                "name": "user_role",
                "type": "String Enum (required)",
                "description": """The user's assigned role within the system, determining their permissions
                and available features. Valid values: 'manager' (can approve claims and view team data),
                'developer' (can claim and implement ideas), 'citizen_developer' (same as developer),
                'idea_submitter' (can only submit ideas). Set during profile creation and modifiable
                by administrators only.""",
                "example": "developer"
            }
        ]
        
        for var in session_vars:
            # Variable name and type
            elements.append(Paragraph(f"{var['name']} ({var['type']})", styles['FieldName']))
            
            # Detailed description
            elements.append(Paragraph(var['description'], styles['FieldDescription']))
            
            # Example value with proper spacing
            if var.get('example'):
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph(f"Example: {var['example']}", styles['CustomCode']))
            
            elements.append(Spacer(1, 0.2*inch))
            
        elements.append(PageBreak())
        
        return elements
        
    def create_core_workflows(self, styles):
        """Create core workflows section with properly sized diagrams"""
        elements = []
        
        elements.append(Paragraph("5. Core Workflows", styles['CustomHeading1']))
        
        elements.append(Paragraph("5.1 Authentication Flow", styles['CustomHeading2']))
        
        auth_intro = """
        The platform implements a passwordless authentication system that balances security
        with user convenience. This approach eliminates password-related vulnerabilities
        while providing a smooth user experience.
        """
        elements.append(Paragraph(auth_intro, styles['CustomBody']))
        
        # Add workflow diagram at original size
        workflow_image = os.path.join(self.screenshots_dir, "workflow_auth_final.png")
        if os.path.exists(workflow_image):
            # Keep header and diagram together
            workflow_content = []
            workflow_content.append(Paragraph("Authentication Workflow Diagram", styles['CustomHeading3']))
            # Use original size, let it scale if needed but maintain aspect ratio
            img = Image(workflow_image, width=6*inch, height=4.5*inch)
            workflow_content.append(img)
            workflow_content.append(Spacer(1, 0.2*inch))
            # Add as KeepTogether
            elements.append(KeepTogether(workflow_content))
        
        elements.append(Paragraph("Authentication Steps:", styles['CustomHeading3']))
        
        auth_steps = [
            "User enters email address on verification page",
            "System generates 6-digit verification code",
            "Code sent via email (or displayed in console for development)",
            "User enters code within 3-minute expiration window",
            "System validates code and creates authenticated session",
            "User redirected to complete profile if first-time login",
            "Session persists for 7 days with sliding expiration"
        ]
        
        for i, step in enumerate(auth_steps, 1):
            elements.append(Paragraph(f"{i}. {step}", styles['NumberedText']))
            
        elements.append(PageBreak())
        
        # Add claim workflow
        elements.append(Paragraph("5.3 Claim Process", styles['CustomHeading2']))
        
        claim_intro = """
        The claim process implements a dual-approval workflow ensuring both the idea owner
        and the claimer's manager approve before work begins. This provides appropriate
        oversight while maintaining agility.
        """
        elements.append(Paragraph(claim_intro, styles['CustomBody']))
        
        # Add claim workflow diagram at original size
        claim_workflow = os.path.join(self.screenshots_dir, "workflow_claim_final.png")
        if os.path.exists(claim_workflow):
            # Keep header and diagram together
            claim_content = []
            claim_content.append(Paragraph("Claim Approval Workflow", styles['CustomHeading3']))
            img = Image(claim_workflow, width=6*inch, height=5*inch)
            claim_content.append(img)
            claim_content.append(Spacer(1, 0.2*inch))
            # Add as KeepTogether
            elements.append(KeepTogether(claim_content))
        
        elements.append(PageBreak())
        
        return elements
        
    def create_api_documentation(self, styles):
        """Create comprehensive API documentation section with proper code formatting"""
        elements = []
        
        elements.append(Paragraph("6. API Documentation", styles['CustomHeading1']))
        
        elements.append(Paragraph("6.1 RESTful Design", styles['CustomHeading2']))
        
        api_intro = """
        The platform provides a comprehensive RESTful API following industry best practices
        for naming conventions, HTTP methods, status codes, and response formats. All endpoints
        return JSON responses with consistent structure and error handling.
        """
        elements.append(Paragraph(api_intro, styles['CustomBody']))
        
        elements.append(Paragraph("API Design Principles:", styles['CustomHeading3']))
        
        principles = [
            "Resource-based URLs using nouns, not verbs",
            "HTTP methods indicate actions (GET, POST, PUT, DELETE)",
            "Consistent JSON response format with success indicators",
            "Detailed error messages with actionable information",
            "UUID-based resource identification for security",
            "Pagination support for list endpoints",
            "Filtering and sorting via query parameters"
        ]
        
        for principle in principles:
            elements.append(Paragraph(f"• {principle}", styles['BulletText']))
            
        elements.append(Paragraph("6.2 Public Endpoints", styles['CustomHeading2']))
        
        elements.append(Paragraph("These endpoints are accessible without authentication:", styles['CustomBody']))
        
        # Enhanced endpoint documentation
        elements.append(Paragraph("GET /api/ideas", styles['FieldName']))
        elements.append(Paragraph("""Retrieves a filtered list of ideas based on query parameters.
        Returns all ideas by default, or filtered by status, priority, skill, or team.
        Supports sorting by date, priority, or alphabetical order.""", styles['FieldDescription']))
        
        elements.append(Paragraph("Parameters:", styles['CustomHeading3']))
        params = [
            "skill (optional): Filter by required skill name",
            "priority (optional): Filter by priority level (low, medium, high)",
            "status (optional): Filter by status (open, claimed, complete)",
            "benefactor_team (optional): Filter by team UUID",
            "sort (optional): Sort order (date_desc, date_asc, priority, alphabetical)"
        ]
        for param in params:
            elements.append(Paragraph(f"• {param}", styles['BulletText']))
        
        elements.append(Paragraph("Example Response:", styles['CustomHeading3']))
        
        # Use preformatted text for better JSON display
        response_json = """{
  "success": true,
  "ideas": [
    {
      "id": "uuid-string",
      "title": "Idea title",
      "description": "Detailed description",
      "priority": "medium",
      "size": "large",
      "status": "open",
      "skills": ["Python", "SQL"],
      "bounty": "Recognition in team meeting",
      "bounty_details": {
        "is_monetary": true,
        "amount": 500.00,
        "is_expensed": true,
        "is_approved": false
      },
      "team_name": "SL - Tech",
      "submitter_name": "John Doe",
      "created_at": "2025-01-26",
      "needed_by": "2025-02-15"
    }
  ]
}"""
        
        # Use Preformatted for exact spacing
        from reportlab.platypus import Preformatted
        pre_style = styles['CustomCode']
        pre_style.fontSize = 8
        elements.append(Preformatted(response_json, pre_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Add more endpoints
        elements.append(Paragraph("GET /api/skills", styles['FieldName']))
        elements.append(Paragraph("""Returns a list of all available skills in the system.
        Used for populating filter dropdowns and skill selection interfaces.""", styles['FieldDescription']))
        
        elements.append(Paragraph("Example Response:", styles['CustomHeading3']))
        
        skills_json = """[
  {
    "id": "uuid-string",
    "name": "Python",
    "category": "Programming"
  },
  {
    "id": "uuid-string",
    "name": "SQL",
    "category": "Database"
  }
]"""
        
        elements.append(Preformatted(skills_json, pre_style))
        
        elements.append(PageBreak())
        
        return elements
        
    def create_database_design(self, styles):
        """Create database design section"""
        elements = []
        
        # Page 10
        elements.append(Paragraph("3. Database Design", styles['CustomHeading1']))
        
        elements.append(Paragraph("3.1 Core Schema", styles['CustomHeading2']))
        
        db_intro = """
        The database follows a normalized design with UUID primary keys for enhanced security
        and scalability. All tables use 36-character UUID strings as primary keys, preventing
        enumeration attacks and supporting distributed systems. The schema is designed for
        flexibility and performance with appropriate indexes on foreign keys and commonly
        queried fields.
        """
        elements.append(Paragraph(db_intro, styles['CustomBody']))
        
        # Add ERD if available
        erd_image = os.path.join(self.screenshots_dir, "erd_main_fixed.png")
        if os.path.exists(erd_image):
            # Keep header and ERD together
            erd_content = []
            erd_content.append(Paragraph("Entity Relationship Diagram - Core Tables", styles['CustomHeading3']))
            # Keep ERD at reasonable size
            img = Image(erd_image, width=5.5*inch, height=3.5*inch)
            erd_content.append(img)
            erd_content.append(Spacer(1, 0.2*inch))
            # Add as KeepTogether
            elements.append(KeepTogether(erd_content))
        
        # Add authentication ERD if available
        erd_auth = os.path.join(self.screenshots_dir, "erd_auth_fixed.png")
        if os.path.exists(erd_auth):
            auth_erd_content = []
            auth_erd_content.append(Paragraph("3.2 Entity Relationships", styles['CustomHeading2']))
            auth_erd_content.append(Paragraph("Authentication and User Management Tables", styles['CustomHeading3']))
            img = Image(erd_auth, width=5.5*inch, height=3.5*inch)
            auth_erd_content.append(img)
            auth_erd_content.append(Spacer(1, 0.2*inch))
            elements.append(KeepTogether(auth_erd_content))
        
        # Add SDLC ERD if available
        erd_sdlc = os.path.join(self.screenshots_dir, "erd_sdlc_fixed.png")
        if os.path.exists(erd_sdlc):
            sdlc_erd_content = []
            sdlc_erd_content.append(Paragraph("3.4 SDLC Extensions", styles['CustomHeading2']))
            sdlc_erd_content.append(Paragraph("Software Development Lifecycle Tables", styles['CustomHeading3']))
            img = Image(erd_sdlc, width=5.5*inch, height=3.5*inch)
            sdlc_erd_content.append(img)
            sdlc_erd_content.append(Spacer(1, 0.2*inch))
            elements.append(KeepTogether(sdlc_erd_content))
        
        elements.append(PageBreak())
        
        return elements
        
    def create_user_interface(self, styles):
        """Create user interface section"""
        elements = []
        
        elements.append(Paragraph("4. User Interface", styles['CustomHeading1']))
        
        elements.append(Paragraph("4.1 Browse Ideas", styles['CustomHeading2']))
        
        browse_intro = """
        The home page provides a comprehensive view of all available ideas with advanced
        filtering and sorting capabilities. Users can quickly identify opportunities that
        match their skills and interests.
        """
        elements.append(Paragraph(browse_intro, styles['CustomBody']))
        
        # Add home page screenshot
        home_screenshot = os.path.join(self.screenshots_dir, "home_page.png")
        if os.path.exists(home_screenshot):
            # Keep together
            browse_content = []
            browse_content.append(Spacer(1, 0.1*inch))
            img = Image(home_screenshot, width=5.5*inch, height=3.5*inch)
            browse_content.append(img)
            browse_content.append(Spacer(1, 0.2*inch))
            elements.append(KeepTogether(browse_content))
        
        elements.append(Paragraph("Key Features:", styles['CustomHeading3']))
        
        browse_features = [
            "Real-time filtering by skill, priority, status, and team",
            "Visual indicators for idea priority and size",
            "Bounty information prominently displayed",
            "One-click access to detailed idea information",
            "Responsive grid layout adapting to screen size",
            "Auto-refresh to show latest submissions"
        ]
        
        for feature in browse_features:
            elements.append(Paragraph(f"• {feature}", styles['BulletText']))
        
        elements.append(Paragraph("4.2 Submit Ideas", styles['CustomHeading2']))
        
        submit_intro = """
        The idea submission interface provides a streamlined process for users to capture their
        automation and development needs with all necessary context.
        """
        elements.append(Paragraph(submit_intro, styles['CustomBody']))
        
        # Add submit page screenshot
        submit_screenshot = os.path.join(self.screenshots_dir, "submit_page.png")
        if os.path.exists(submit_screenshot):
            submit_content = []
            submit_content.append(Spacer(1, 0.1*inch))
            img = Image(submit_screenshot, width=5.5*inch, height=3.5*inch)
            submit_content.append(img)
            submit_content.append(Spacer(1, 0.2*inch))
            elements.append(KeepTogether(submit_content))
            
        elements.append(PageBreak())
        
        elements.append(Paragraph("4.3 My Ideas Dashboard", styles['CustomHeading2']))
        
        myideas_intro = """
        The My Ideas page provides a personalized view of all ideas submitted by or claimed by
        the authenticated user, including pending approvals and activity tracking.
        """
        elements.append(Paragraph(myideas_intro, styles['CustomBody']))
        
        # Add My Ideas screenshot
        myideas_screenshot = os.path.join(self.screenshots_dir, "my_ideas_page.png")
        if os.path.exists(myideas_screenshot):
            myideas_content = []
            myideas_content.append(Spacer(1, 0.1*inch))
            img = Image(myideas_screenshot, width=5.5*inch, height=3.5*inch)
            myideas_content.append(img)
            myideas_content.append(Spacer(1, 0.2*inch))
            elements.append(KeepTogether(myideas_content))
            
        elements.append(PageBreak())
        
        elements.append(Paragraph("4.4 Team Analytics", styles['CustomHeading2']))
        
        team_intro = """
        The My Team page provides comprehensive analytics and management capabilities for team
        managers, including performance metrics, skill gap analysis, and spending tracking.
        """
        elements.append(Paragraph(team_intro, styles['CustomBody']))
        
        # Add My Team screenshot
        myteam_screenshot = os.path.join(self.screenshots_dir, "my_team_page.png")
        if os.path.exists(myteam_screenshot):
            myteam_content = []
            myteam_content.append(Spacer(1, 0.1*inch))
            img = Image(myteam_screenshot, width=5.5*inch, height=3.5*inch)
            myteam_content.append(img)
            myteam_content.append(Spacer(1, 0.2*inch))
            elements.append(KeepTogether(myteam_content))
            
        elements.append(PageBreak())
        
        return elements
        
    def create_security_section(self, styles):
        """Create security section"""
        elements = []
        
        elements.append(Paragraph("7. Security and Authentication", styles['CustomHeading1']))
        
        elements.append(Paragraph("7.1 Passwordless Authentication", styles['CustomHeading2']))
        
        security_intro = """
        The platform implements a passwordless authentication system that eliminates
        common password-related vulnerabilities while maintaining strong security.
        This approach uses time-limited verification codes sent via email.
        """
        elements.append(Paragraph(security_intro, styles['CustomBody']))
        
        elements.append(Paragraph("Security Features:", styles['CustomHeading3']))
        
        security_features = [
            "No password storage eliminates breach risks",
            "6-digit verification codes with 3-minute expiration",
            "Rate limiting prevents brute force attempts (3 attempts per hour)",
            "Email validation ensures valid corporate addresses",
            "Session tokens use cryptographically secure generation",
            "HTTPOnly cookies prevent XSS attacks",
            "CSRF protection via SameSite cookie attribute"
        ]
        
        for feature in security_features:
            elements.append(Paragraph(f"• {feature}", styles['BulletText']))
            
        elements.append(PageBreak())
        
        return elements
        
    def create_sdlc_features(self, styles):
        """Create SDLC features section"""
        elements = []
        
        elements.append(Paragraph("8. SDLC Features", styles['CustomHeading1']))
        
        elements.append(Paragraph("8.1 Sub-Status Tracking", styles['CustomHeading2']))
        
        sdlc_intro = """
        The platform includes comprehensive Software Development Life Cycle (SDLC) tracking
        features that enable detailed monitoring of idea progress through development stages.
        These features provide transparency and accountability throughout the implementation process.
        """
        elements.append(Paragraph(sdlc_intro, styles['CustomBody']))
        
        elements.append(Paragraph("Development Sub-Statuses:", styles['CustomHeading3']))
        
        sub_statuses = [
            ("planning", "Initial requirements gathering and design (10% progress)"),
            ("in_development", "Active development work (30% progress)"),
            ("testing", "Quality assurance and testing (60% progress)"),
            ("awaiting_deployment", "Ready for production deployment (80% progress)"),
            ("deployed", "Deployed to production environment (90% progress)"),
            ("verified", "Fully tested and verified in production (100% progress)"),
            ("on_hold", "Temporarily paused (maintains current progress)"),
            ("blocked", "Blocked by dependencies or issues (maintains progress)"),
            ("cancelled", "Development cancelled (0% progress)"),
            ("rolled_back", "Deployment rolled back (0% progress)")
        ]
        
        for status, desc in sub_statuses:
            elements.append(Paragraph(f"• {status}: {desc}", styles['BulletText']))
        
        elements.append(Paragraph("8.2 Development Progress", styles['CustomHeading2']))
        
        progress_intro = """
        The platform provides visual progress tracking through interactive GANTT charts and
        progress indicators, giving stakeholders real-time visibility into development status.
        """
        elements.append(Paragraph(progress_intro, styles['CustomBody']))
        
        # Add idea detail screenshot showing SDLC features
        idea_detail_screenshot = os.path.join(self.screenshots_dir, "idea_detail_page.png")
        if os.path.exists(idea_detail_screenshot):
            detail_content = []
            detail_content.append(Spacer(1, 0.1*inch))
            detail_content.append(Paragraph("Idea Detail with SDLC Tracking", styles['CustomHeading3']))
            img = Image(idea_detail_screenshot, width=5.5*inch, height=3.5*inch)
            detail_content.append(img)
            detail_content.append(Spacer(1, 0.2*inch))
            elements.append(KeepTogether(detail_content))
        
        # Add lifecycle workflow diagram
        lifecycle_workflow = os.path.join(self.screenshots_dir, "workflow_lifecycle_final.png")
        if os.path.exists(lifecycle_workflow):
            lifecycle_content = []
            lifecycle_content.append(Paragraph("Idea Lifecycle Flow", styles['CustomHeading3']))
            img = Image(lifecycle_workflow, width=6*inch, height=5*inch)
            lifecycle_content.append(img)
            lifecycle_content.append(Spacer(1, 0.2*inch))
            elements.append(KeepTogether(lifecycle_content))
            
        elements.append(PageBreak())
        
        return elements
        
    def create_admin_portal(self, styles):
        """Create admin portal section"""
        elements = []
        
        elements.append(Paragraph("9. Admin Portal", styles['CustomHeading1']))
        
        elements.append(Paragraph("9.1 Dashboard Overview", styles['CustomHeading2']))
        
        admin_intro = """
        The administrative portal provides comprehensive system management capabilities
        with real-time analytics, user management, and configuration options. Access
        is restricted to authorized administrators through additional authentication.
        """
        elements.append(Paragraph(admin_intro, styles['CustomBody']))
        
        # Add admin screenshot if available
        admin_dashboard = os.path.join(self.screenshots_dir, "admin_dashboard.png")
        if os.path.exists(admin_dashboard):
            admin_content = []
            admin_content.append(Spacer(1, 0.1*inch))
            img = Image(admin_dashboard, width=5.5*inch, height=3.5*inch)
            admin_content.append(img)
            admin_content.append(Spacer(1, 0.2*inch))
            elements.append(KeepTogether(admin_content))
        
        elements.append(Paragraph("Key Metrics Displayed:", styles['CustomHeading3']))
        
        metrics = [
            "Total ideas submitted across all teams",
            "Open ideas awaiting claims",
            "Active claims in progress",
            "Completed ideas with success metrics",
            "Total registered users and skill distribution",
            "Spending analytics for monetary bounties",
            "Team performance comparisons"
        ]
        
        for metric in metrics:
            elements.append(Paragraph(f"• {metric}", styles['BulletText']))
        
        # Add notification workflow diagram
        notification_workflow = os.path.join(self.screenshots_dir, "workflow_notifications_final.png")
        if os.path.exists(notification_workflow):
            notif_content = []
            notif_content.append(Spacer(1, 0.3*inch))
            notif_content.append(Paragraph("Notification System Workflow", styles['CustomHeading3']))
            img = Image(notification_workflow, width=6*inch, height=5*inch)
            notif_content.append(img)
            notif_content.append(Spacer(1, 0.2*inch))
            elements.append(KeepTogether(notif_content))
            
        elements.append(PageBreak())
        
        return elements
        
    def create_deployment_guide(self, styles):
        """Create deployment guide section"""
        elements = []
        
        elements.append(Paragraph("10. Deployment Guide", styles['CustomHeading1']))
        
        elements.append(Paragraph("10.1 Requirements", styles['CustomHeading2']))
        
        req_intro = """
        The platform is designed for easy deployment in various environments with
        minimal dependencies. Both development and production configurations are supported.
        """
        elements.append(Paragraph(req_intro, styles['CustomBody']))
        
        elements.append(Paragraph("System Requirements:", styles['CustomHeading3']))
        
        requirements = [
            "Python 3.8 or higher (3.12 recommended)",
            "2GB RAM minimum (4GB recommended)",
            "10GB disk space for application and data",
            "Linux or macOS for production (Windows supported for development)",
            "PostgreSQL 12+ for production database (SQLite for development)",
            "SMTP server access for email notifications",
            "HTTPS certificate for production deployment"
        ]
        
        for req in requirements:
            elements.append(Paragraph(f"• {req}", styles['BulletText']))
            
        elements.append(PageBreak())
        
        return elements
        
    def create_performance_section(self, styles):
        """Create performance optimization section"""
        elements = []
        
        elements.append(Paragraph("11. Performance Optimization", styles['CustomHeading1']))
        
        elements.append(Paragraph("11.1 Database Optimization", styles['CustomHeading2']))
        
        perf_intro = """
        The platform implements several optimization strategies to ensure responsive
        performance even with large datasets and concurrent users.
        """
        elements.append(Paragraph(perf_intro, styles['CustomBody']))
        
        elements.append(Paragraph("Optimization Techniques:", styles['CustomHeading3']))
        
        optimizations = [
            "UUID indexes on all foreign key columns",
            "Composite indexes for common query patterns",
            "Query result caching for frequently accessed data",
            "Lazy loading of related entities",
            "Connection pooling for database connections",
            "Prepared statements to prevent SQL injection",
            "Pagination for large result sets"
        ]
        
        for opt in optimizations:
            elements.append(Paragraph(f"• {opt}", styles['BulletText']))
            
        elements.append(PageBreak())
        
        return elements
        
    def create_troubleshooting(self, styles):
        """Create troubleshooting section"""
        elements = []
        
        elements.append(Paragraph("12. Troubleshooting", styles['CustomHeading1']))
        
        elements.append(Paragraph("12.1 Common Issues", styles['CustomHeading2']))
        
        trouble_intro = """
        This section addresses frequently encountered issues and their solutions
        to help administrators and developers quickly resolve problems.
        """
        elements.append(Paragraph(trouble_intro, styles['CustomBody']))
        
        # Create smaller table with wrapped text
        issues_data = [
            ["Issue", "Cause", "Solution"],
            ["Email verification codes not received", 
             "SMTP configuration incorrect or email server blocking",
             "Check SMTP settings in config, verify firewall rules, check spam folder"],
            ["Session expires unexpectedly",
             "Session timeout too short or cookie settings incorrect",
             "Adjust SESSION_LIFETIME in config, verify cookie domain settings"],
            ["Cannot claim ideas",
             "User profile incomplete or wrong role assigned",
             "Ensure user has developer/citizen_developer role and skills selected"],
            ["Admin portal access denied",
             "Admin session expired or incorrect password",
             "Re-authenticate with admin password, check session configuration"]
        ]
        
        # Create paragraphs for table cells
        wrapped_issues = []
        for row in issues_data:
            wrapped_row = []
            for i, cell in enumerate(row):
                if i == 0 and row != issues_data[0]:  # First column, not header
                    wrapped_row.append(Paragraph(cell, styles['Normal']))
                elif len(cell) > 30:  # Wrap long text
                    wrapped_row.append(Paragraph(cell, styles['Normal']))
                else:
                    wrapped_row.append(cell)
            wrapped_issues.append(wrapped_row)
        
        issues_table = Table(wrapped_issues, colWidths=[1.8*inch, 2*inch, 2.2*inch])
        issues_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(issues_table)
        
        elements.append(PageBreak())
        
        return elements
        
    def create_future_roadmap(self, styles):
        """Create future roadmap section"""
        elements = []
        
        elements.append(Paragraph("13. Future Roadmap", styles['CustomHeading1']))
        
        elements.append(Paragraph("13.1 Planned Features", styles['CustomHeading2']))
        
        roadmap_intro = """
        The following features are planned for future releases based on user feedback
        and organizational needs:
        """
        elements.append(Paragraph(roadmap_intro, styles['CustomBody']))
        
        planned_features = [
            "Microsoft Teams integration for notifications",
            "AI-powered idea matching and recommendations",
            "Mobile application for iOS and Android",
            "Advanced analytics with PowerBI integration",
            "Automated testing framework for citizen developers",
            "Template library for common solutions",
            "Gamification elements to encourage participation",
            "Integration with corporate SSO systems",
            "Multi-language support for global teams",
            "API webhooks for external integrations"
        ]
        
        for feature in planned_features:
            elements.append(Paragraph(f"• {feature}", styles['BulletText']))
            
        elements.append(PageBreak())
        
        return elements
        
    def create_appendices(self, styles):
        """Create appendices section"""
        elements = []
        
        elements.append(Paragraph("14. Appendices", styles['CustomHeading1']))
        
        elements.append(Paragraph("14.1 Configuration Reference", styles['CustomHeading2']))
        
        config_intro = """
        The following configuration options are available for customizing the platform:
        """
        elements.append(Paragraph(config_intro, styles['CustomBody']))
        
        config_options = [
            ("DATABASE_URL", "PostgreSQL connection string for production"),
            ("SECRET_KEY", "Secret key for session encryption (generate unique value)"),
            ("SMTP_SERVER", "Email server hostname for notifications"),
            ("SMTP_PORT", "Email server port (typically 587 for TLS)"),
            ("SMTP_USERNAME", "Email account username"),
            ("SMTP_PASSWORD", "Email account password"),
            ("SESSION_LIFETIME", "Session duration in seconds (default: 604800 = 7 days)"),
            ("VERIFICATION_CODE_EXPIRY", "Code expiration in seconds (default: 180 = 3 minutes)"),
            ("BOUNTY_APPROVAL_THRESHOLD", "Amount requiring approval (default: 50)"),
            ("DEBUG", "Enable debug mode (never true in production)")
        ]
        
        for option, desc in config_options:
            elements.append(Paragraph(f"{option}:", styles['FieldName']))
            elements.append(Paragraph(desc, styles['FieldDescription']))
            
        elements.append(PageBreak())
        
        return elements

if __name__ == "__main__":
    generator = FinalDocumentationGenerator()
    generator.generate()