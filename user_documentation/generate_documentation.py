#!/usr/bin/env python3
"""
Unified Documentation Generator
Generates both basic and complete technical documentation PDFs with all diagrams
"""

import os
import subprocess
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.platypus import Image as ReportLabImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

class UnifiedDocumentationGenerator:
    def __init__(self):
        self.screenshots_dir = "/root/postingboard/documentation_screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
    def generate_all_documentation(self):
        """Generate all documentation with improved diagrams"""
        print("="*60)
        print("Unified Documentation Generator")
        print("="*60)
        
        # Check for required diagram files
        self.verify_diagrams()
        
        # Generate both PDFs
        self.generate_basic_pdf()
        self.generate_complete_pdf()
        
        print("\n✓ Documentation generation complete!")
        print("\nGenerated files:")
        print("- Posting_Board_Technical_Documentation.pdf")
        print("- Posting_Board_Complete_Documentation.pdf")
    
    def verify_diagrams(self):
        """Verify all required diagram files exist"""
        required_diagrams = [
            # Workflow diagrams (using _final versions)
            'workflow_auth_final.png',
            'workflow_claim_final.png',
            'workflow_lifecycle_final.png',
            'workflow_notifications_final.png',
            'workflow_resume_pause_final.png',
            
            # ERD diagrams (using _fixed versions with hub-and-spoke layout)
            'erd_main_fixed.png',
            'erd_sdlc_fixed.png',
            'erd_auth_fixed.png',
            
            # UI mockups
            'home_page.png',
            'submit_idea.png',
            'my_ideas_page.png',
            'admin_dashboard.png'
        ]
        
        missing = []
        for diagram in required_diagrams:
            if not os.path.exists(f'{self.screenshots_dir}/{diagram}'):
                missing.append(diagram)
        
        if missing:
            print("⚠️  Missing diagram files:")
            for file in missing:
                print(f"   - {file}")
            print("\nPlease generate missing diagrams first.")
            # Continue anyway - some diagrams might be optional
    
    def generate_basic_pdf(self):
        """Generate the basic technical documentation PDF"""
        print("\nGenerating basic technical documentation...")
        
        doc_filename = "Posting_Board_Technical_Documentation.pdf"
        doc = SimpleDocTemplate(doc_filename, pagesize=letter)
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=12
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10
        )
        
        body_style = ParagraphStyle(
            'CustomBodyText',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )
        
        # Title page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("Citizen Developer Posting Board", title_style))
        story.append(Paragraph("Technical Documentation", title_style))
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(PageBreak())
        
        # Table of Contents
        story.append(Paragraph("Table of Contents", heading1_style))
        toc_data = [
            ["1.", "Introduction", "3"],
            ["2.", "System Architecture", "4"],
            ["3.", "Database Schema", "5"],
            ["4.", "API Documentation", "8"],
            ["5.", "Authentication System", "10"],
            ["6.", "Workflows", "12"]
        ]
        
        toc_table = Table(toc_data, colWidths=[0.5*inch, 4*inch, 0.5*inch])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(toc_table)
        story.append(PageBreak())
        
        # 1. Introduction
        story.append(Paragraph("1. Introduction", heading1_style))
        intro_text = """
        The Citizen Developer Posting Board is a web application that connects teams with development 
        needs to citizen developers who can implement solutions. This platform facilitates idea submission, 
        skill matching, and project tracking through a comprehensive workflow system.
        """
        story.append(Paragraph(intro_text, body_style))
        
        story.append(Paragraph("Key Features:", heading2_style))
        features = [
            "• Idea submission and browsing",
            "• Skill-based matching",
            "• Dual approval workflow for claims",
            "• Team-based organization",
            "• Progress tracking with sub-status system",
            "• Monetary and non-monetary bounty support",
            "• Comprehensive notification system"
        ]
        for feature in features:
            story.append(Paragraph(feature, styles['BodyText']))
        
        story.append(PageBreak())
        
        # 2. System Architecture
        story.append(Paragraph("2. System Architecture", heading1_style))
        story.append(Paragraph("Technology Stack", heading2_style))
        
        tech_data = [
            ["Component", "Technology"],
            ["Backend", "Python Flask"],
            ["Database", "SQLite with SQLAlchemy ORM"],
            ["Frontend", "Jinja2 Templates + Vanilla JavaScript"],
            ["Authentication", "Email-based verification (passwordless)"],
            ["Session Management", "Flask-Session (filesystem storage)"],
            ["Deployment", "Docker with Gunicorn"]
        ]
        
        tech_table = Table(tech_data, colWidths=[2*inch, 3*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        story.append(tech_table)
        
        story.append(PageBreak())
        
        # 3. Database Schema
        story.append(Paragraph("3. Database Schema", heading1_style))
        
        story.append(Paragraph("The application uses UUID-based primary keys for all entities:", body_style))
        
        # Add main ERD
        if os.path.exists(f'{self.screenshots_dir}/erd_main_fixed.png'):
            story.append(Paragraph("Core Database Schema", heading2_style))
            img = ReportLabImage(f'{self.screenshots_dir}/erd_main_fixed.png', 
                                width=6*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        
        # Add SDLC ERD
        if os.path.exists(f'{self.screenshots_dir}/erd_sdlc_fixed.png'):
            story.append(PageBreak())
            story.append(Paragraph("SDLC Tracking Schema", heading2_style))
            img = ReportLabImage(f'{self.screenshots_dir}/erd_sdlc_fixed.png', 
                                width=5*inch, height=3.5*inch)
            story.append(img)
        
        # Add Auth ERD
        if os.path.exists(f'{self.screenshots_dir}/erd_auth_fixed.png'):
            story.append(PageBreak())
            story.append(Paragraph("Authentication Schema", heading2_style))
            img = ReportLabImage(f'{self.screenshots_dir}/erd_auth_fixed.png', 
                                width=5*inch, height=3*inch)
            story.append(img)
        
        story.append(PageBreak())
        
        # 4. Workflows
        story.append(Paragraph("4. Key Workflows", heading1_style))
        
        # Authentication workflow
        story.append(Paragraph("4.1 Authentication Workflow", heading2_style))
        if os.path.exists(f'{self.screenshots_dir}/workflow_auth_final.png'):
            img = ReportLabImage(f'{self.screenshots_dir}/workflow_auth_final.png', 
                                width=4*inch, height=5*inch)
            story.append(img)
        
        # Claim workflow
        story.append(PageBreak())
        story.append(Paragraph("4.2 Claim Approval Workflow", heading2_style))
        if os.path.exists(f'{self.screenshots_dir}/workflow_claim_final.png'):
            img = ReportLabImage(f'{self.screenshots_dir}/workflow_claim_final.png', 
                                width=5*inch, height=4*inch)
            story.append(img)
        
        # Build PDF
        doc.build(story)
        print(f"✓ Generated: {doc_filename}")
    
    def generate_complete_pdf(self):
        """Generate the complete documentation PDF"""
        print("\nGenerating complete documentation...")
        
        doc_filename = "Posting_Board_Complete_Documentation.pdf"
        doc = SimpleDocTemplate(doc_filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        story = []
        
        # Define enhanced styles for complete documentation
        styles = getSampleStyleSheet()
        
        # Custom styles with better formatting
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=40,
            alignment=TA_CENTER,
            leading=32
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=16,
            spaceBefore=24
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=16
        )
        
        heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=12
        )
        
        body_style = ParagraphStyle(
            'CustomBodyText',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=14
        )
        
        # Enhanced title page
        story.append(Spacer(1, 1.5*inch))
        story.append(Paragraph("Citizen Developer Posting Board", title_style))
        story.append(Paragraph("Complete Technical Documentation", subtitle_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Version 2.0", styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("An enterprise platform for connecting teams with citizen developers", 
                             subtitle_style))
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading1_style))
        exec_summary = """
        The Citizen Developer Posting Board revolutionizes how organizations leverage their internal 
        talent pool by creating a marketplace for development ideas. Teams can post their automation 
        and development needs, while skilled employees can browse, claim, and implement solutions.
        
        This platform addresses the growing need for citizen development capabilities within enterprises, 
        enabling faster delivery of business solutions while providing growth opportunities for 
        technically-minded employees across all departments.
        """
        story.append(Paragraph(exec_summary, body_style))
        
        story.append(Paragraph("Key Benefits:", heading2_style))
        benefits = [
            "• Accelerates solution delivery by tapping into distributed talent",
            "• Reduces IT backlog by enabling self-service development",
            "• Provides skill development opportunities for employees",
            "• Creates transparency in development priorities and progress",
            "• Facilitates knowledge sharing across teams",
            "• Tracks monetary and non-monetary incentives"
        ]
        for benefit in benefits:
            story.append(Paragraph(benefit, styles['BodyText']))
        
        story.append(PageBreak())
        
        # Comprehensive Table of Contents
        story.append(Paragraph("Table of Contents", heading1_style))
        
        toc_data = [
            ["1.", "Introduction and Overview", "4"],
            ["2.", "System Architecture", "6"],
            ["3.", "Database Design", "10"],
            ["4.", "User Interface", "15"],
            ["5.", "Core Workflows", "20"],
            ["6.", "API Documentation", "25"],
            ["7.", "Security and Authentication", "30"],
            ["8.", "Team Management", "35"],
            ["9.", "Notification System", "40"],
            ["10.", "SDLC Tracking Features", "45"],
            ["11.", "Admin Portal", "50"],
            ["12.", "Deployment Guide", "55"],
            ["13.", "Best Practices", "58"],
            ["14.", "Troubleshooting", "60"]
        ]
        
        toc_table = Table(toc_data, colWidths=[0.5*inch, 4.5*inch, 0.5*inch])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.lightgrey)
        ]))
        story.append(toc_table)
        story.append(PageBreak())
        
        # Add all workflow diagrams
        story.append(Paragraph("5. Core Workflows", heading1_style))
        
        workflow_diagrams = [
            ("5.1 Authentication Workflow", "workflow_auth_final.png", 4, 5),
            ("5.2 Claim Approval Workflow", "workflow_claim_final.png", 5, 4),
            ("5.3 Idea Lifecycle", "workflow_lifecycle_final.png", 6, 4),
            ("5.4 Notification System", "workflow_notifications_final.png", 5, 4),
            ("5.5 Resume/Pause Workflow", "workflow_resume_pause_final.png", 5, 3)
        ]
        
        for title, filename, width, height in workflow_diagrams:
            story.append(Paragraph(title, heading2_style))
            if os.path.exists(f'{self.screenshots_dir}/{filename}'):
                img = ReportLabImage(f'{self.screenshots_dir}/{filename}', 
                                    width=width*inch, height=height*inch)
                story.append(img)
                story.append(PageBreak())
        
        # Add all ERD diagrams
        story.append(Paragraph("3. Database Design", heading1_style))
        
        erd_diagrams = [
            ("3.1 Core Database Schema", "erd_main_fixed.png", 6.5, 4.5,
             "Hub-and-spoke design with Idea as the central entity. All relationships clearly defined with no ambiguity."),
            ("3.2 SDLC Tracking Schema", "erd_sdlc_fixed.png", 6, 4,
             "Comprehensive tracking of development lifecycle with comments, activities, and stage-specific data."),
            ("3.3 Authentication & User Management", "erd_auth_fixed.png", 5.5, 3.5,
             "User profiles, verification codes, and manager request tracking with clear relationships.")
        ]
        
        for title, filename, width, height, description in erd_diagrams:
            story.append(Paragraph(title, heading2_style))
            story.append(Paragraph(description, body_style))
            if os.path.exists(f'{self.screenshots_dir}/{filename}'):
                img = ReportLabImage(f'{self.screenshots_dir}/{filename}', 
                                    width=width*inch, height=height*inch)
                story.append(img)
                story.append(PageBreak())
        
        # Build the complete PDF
        doc.build(story)
        print(f"✓ Generated: {doc_filename}")

if __name__ == "__main__":
    generator = UnifiedDocumentationGenerator()
    generator.generate_all_documentation()