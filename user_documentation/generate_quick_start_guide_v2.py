#!/usr/bin/env python3
"""
BlackRock Liquidity and Financing - Citizen Developer Posting Board Quick Start Guide
Generates a concise 3-page PDF quick start guide with screenshots
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import os
from datetime import datetime

# Color scheme
PRIMARY_COLOR = HexColor('#4a90e2')
SECONDARY_COLOR = HexColor('#1a1d23')
ACCENT_COLOR = HexColor('#28a745')
WARNING_COLOR = HexColor('#f0ad4e')
LIGHT_GRAY = HexColor('#f8f9fa')

class NumberedCanvas(canvas.Canvas):
    """Canvas that adds page numbers"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page numbers to each page."""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self):
        self.setFont("Helvetica", 8)
        self.setFillColor(HexColor('#666666'))
        self.drawRightString(letter[0] - 0.5*inch, 0.4*inch, 
                            f"Page {self._pageNumber} of 3")

def create_quick_start_guide():
    """Generate the quick start guide PDF"""
    
    # Create PDF document
    filename = "BlackRock_Citizen_Developer_Quick_Start_Guide.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.6*inch,
        leftMargin=0.6*inch,
        topMargin=0.8*inch,
        bottomMargin=0.6*inch
    )
    
    # Container for the 'Flowable' objects
    story = []
    
    # Define custom styles with smaller fonts
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=SECONDARY_COLOR,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=PRIMARY_COLOR,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # Heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=PRIMARY_COLOR,
        spaceAfter=6,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    # Subheading style
    subheading_style = ParagraphStyle(
        'Subheading',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=SECONDARY_COLOR,
        spaceAfter=4,
        spaceBefore=6,
        fontName='Helvetica-Bold'
    )
    
    # Body style - smaller
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=9,
        textColor=black,
        spaceAfter=4,
        alignment=TA_JUSTIFY,
        leading=11
    )
    
    # Bullet style - smaller
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=body_style,
        leftIndent=15,
        bulletIndent=8,
        fontSize=9
    )
    
    # Small caption style
    caption_style = ParagraphStyle(
        'Caption',
        parent=body_style,
        fontSize=8,
        alignment=TA_CENTER,
        textColor=HexColor('#666666')
    )
    
    # PAGE 1: Quick Start / TLDR
    story.append(Paragraph("BlackRock Liquidity and Financing", subtitle_style))
    story.append(Paragraph("Citizen Developer Posting Board", title_style))
    story.append(Paragraph("Quick Start Guide", subtitle_style))
    story.append(Spacer(1, 0.3*inch))
    
    # TLDR Section
    story.append(Paragraph("Quick Start (TL;DR)", heading_style))
    
    # Quick tips table
    quick_tips_data = [
        [Paragraph("<b>For Everyone</b>", body_style), Paragraph("<b>For Developers</b>", body_style), Paragraph("<b>For Managers</b>", body_style)],
        [
            Paragraph("1. Login → Verify email<br/>2. Complete profile<br/>3. Browse ideas with filters<br/>4. Submit new ideas<br/>5. Check notifications (bell icon)", bullet_style),
            Paragraph("1. Must have Developer role<br/>2. Find ideas matching skills<br/>3. Click 'Claim This Idea'<br/>4. Wait for dual approval<br/>5. Track in My Ideas", bullet_style),
            Paragraph("1. Access My Team page<br/>2. Approve claim requests<br/>3. Monitor team metrics<br/>4. Track spending/budget<br/>5. Identify skill gaps", bullet_style)
        ]
    ]
    
    quick_tips_table = Table(quick_tips_data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
    quick_tips_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_GRAY),
        ('TEXTCOLOR', (0, 0), (-1, 0), SECONDARY_COLOR),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e9ecef')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(quick_tips_table)
    story.append(Spacer(1, 0.2*inch))
    
    # What is it?
    story.append(Paragraph("What is the Posting Board?", heading_style))
    story.append(Paragraph(
        "A platform connecting BlackRock L&F business needs with technical talent. Teams post automation/development "
        "needs while skilled employees from any department can discover and implement solutions.",
        body_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Browse Ideas Screenshot
    story.append(Paragraph("Browse & Filter Ideas", subheading_style))
    if os.path.exists('documentation_screenshots/home_page.png'):
        img = Image('documentation_screenshots/home_page.png', width=6.5*inch, height=2.5*inch)
        story.append(img)
        story.append(Paragraph("Filter by skill, priority, status • View bounties • Click for details", caption_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Key Features Grid
    features_data = [
        [Paragraph("<b>Email Authentication</b><br/>No passwords - verify with 6-digit code sent to your BlackRock email", body_style),
         Paragraph("<b>Role-Based Access</b><br/>Developer, Citizen Developer, Idea Submitter, or Manager roles", body_style)],
        [Paragraph("<b>Dual Approval</b><br/>Claims require approval from idea owner AND claimer's manager", body_style),
         Paragraph("<b>Monetary Bounties</b><br/>Track spending; amounts >$50 require manager approval", body_style)]
    ]
    
    features_table = Table(features_data, colWidths=[3.4*inch, 3.4*inch])
    features_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e9ecef')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(features_table)
    
    # PAGE 2: User Functions
    story.append(PageBreak())
    story.append(Paragraph("For All Users", heading_style))
    
    # Two column layout for submit process
    submit_content = []
    submit_content.append(Paragraph("Submitting Ideas", subheading_style))
    submit_content.append(Paragraph("Click 'Submit Idea' to post development needs:", body_style))
    submit_content.append(Paragraph("• <b>Title:</b> Brief, descriptive name", bullet_style))
    submit_content.append(Paragraph("• <b>Description:</b> Detailed requirements", bullet_style))
    submit_content.append(Paragraph("• <b>Priority:</b> Low/Medium/High", bullet_style))
    submit_content.append(Paragraph("• <b>Size:</b> S/M/L/XL effort estimate", bullet_style))
    submit_content.append(Paragraph("• <b>Skills:</b> Required technical skills", bullet_style))
    submit_content.append(Paragraph("• <b>Bounty:</b> Recognition/rewards", bullet_style))
    
    # Submit screenshot
    submit_screenshot = []
    if os.path.exists('documentation_screenshots/submit_idea_page.png'):
        img = Image('documentation_screenshots/submit_idea_page.png', width=3.2*inch, height=2.8*inch)
        submit_screenshot.append(img)
    
    submit_table = Table([[submit_content, submit_screenshot]], colWidths=[3.5*inch, 3.3*inch])
    submit_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('RIGHTPADDING', (1, 0), (1, 0), 0),
    ]))
    story.append(submit_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Claiming Ideas section
    story.append(Paragraph("For Developers: Claiming Ideas", heading_style))
    
    claim_data = [
        ["1. Browse ideas matching your skills", "2. Click 'View Details' → 'Claim This Idea'"],
        ["3. Wait for dual approval (owner + manager)", "4. Track progress in My Ideas dashboard"]
    ]
    
    claim_table = Table(claim_data, colWidths=[3.4*inch, 3.4*inch])
    claim_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e9ecef')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(claim_table)
    story.append(Spacer(1, 0.15*inch))
    
    # My Ideas Dashboard
    story.append(Paragraph("My Ideas Dashboard", subheading_style))
    
    my_ideas_content = []
    if os.path.exists('documentation_screenshots/my_ideas_page.png'):
        img = Image('documentation_screenshots/my_ideas_page.png', width=4*inch, height=1.8*inch)
        my_ideas_content.append(img)
    
    my_ideas_features = []
    my_ideas_features.append(Paragraph("Track your activity:", body_style))
    my_ideas_features.append(Paragraph("• Statistics overview", bullet_style))
    my_ideas_features.append(Paragraph("• Submitted ideas status", bullet_style))
    my_ideas_features.append(Paragraph("• Claimed ideas progress", bullet_style))
    my_ideas_features.append(Paragraph("• Pending approvals", bullet_style))
    my_ideas_features.append(Paragraph("• Notification bell", bullet_style))
    
    my_ideas_table = Table([[my_ideas_content, my_ideas_features]], colWidths=[4.1*inch, 2.7*inch])
    my_ideas_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
    ]))
    story.append(my_ideas_table)
    
    # PAGE 3: Manager Functions
    story.append(PageBreak())
    story.append(Paragraph("For Managers", heading_style))
    
    # Manager capabilities in a compact format
    story.append(Paragraph("Manager Dashboard - My Team", subheading_style))
    
    # My Team screenshot with features
    team_content = []
    if os.path.exists('documentation_screenshots/my_team_page.png'):
        img = Image('documentation_screenshots/my_team_page.png', width=4.2*inch, height=2*inch)
        team_content.append(img)
    
    team_features = []
    team_features.append(Paragraph("<b>Key Capabilities:</b>", body_style))
    team_features.append(Paragraph("• Approve team claims", bullet_style))
    team_features.append(Paragraph("• View team analytics", bullet_style))
    team_features.append(Paragraph("• Assign ideas to members", bullet_style))
    team_features.append(Paragraph("• Edit member profiles", bullet_style))
    team_features.append(Paragraph("• Monitor spending", bullet_style))
    team_features.append(Paragraph("• Identify skill gaps", bullet_style))
    
    team_table = Table([[team_content, team_features]], colWidths=[4.3*inch, 2.5*inch])
    team_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
    ]))
    story.append(team_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Analytics Overview
    story.append(Paragraph("Team Analytics Overview", subheading_style))
    
    analytics_data = [
        [
            Paragraph("<b>Team Overview</b><br/>• Member count & activity<br/>• Submission vs claim rates<br/>• Completion metrics<br/>• Pending approvals", body_style),
            Paragraph("<b>Visual Charts</b><br/>• Priority distribution<br/>• Size breakdown<br/>• Skills gap analysis<br/>• Spending trends", body_style),
            Paragraph("<b>Member Table</b><br/>• Individual metrics<br/>• Edit profiles/skills<br/>• Submitted/claimed<br/>• Activity tracking", body_style)
        ]
    ]
    
    analytics_table = Table(analytics_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
    analytics_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e9ecef')),
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(analytics_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Best Practices
    story.append(Paragraph("Best Practices & Tips", heading_style))
    
    tips_data = [
        [
            Paragraph("<b>For Everyone</b><br/>• Keep profile updated<br/>• Check notifications daily<br/>• Use filters effectively<br/>• Write clear descriptions", body_style),
            Paragraph("<b>For Developers</b><br/>• Match skills to ideas<br/>• Consider workload<br/>• Update progress regularly<br/>• Communicate blockers", body_style),
            Paragraph("<b>For Managers</b><br/>• Review claims promptly<br/>• Monitor skill gaps<br/>• Track team spending<br/>• Encourage participation", body_style)
        ]
    ]
    
    tips_table = Table(tips_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
    tips_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e9ecef')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tips_table)
    
    # Important Notes
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("Important Notes", subheading_style))
    story.append(Paragraph("• Monetary bounties >$50 require manager/admin approval", bullet_style))
    story.append(Paragraph("• Email verification codes expire in 3 minutes", bullet_style))
    story.append(Paragraph("• Claims require dual approval (idea owner + claimer's manager)", bullet_style))
    story.append(Paragraph("• Only Developers and Citizen Developers can claim ideas", bullet_style))
    
    # Footer
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        f"BlackRock Liquidity and Financing • Generated: {datetime.now().strftime('%B %d, %Y')}",
        ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=HexColor('#666666'), alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    
    return filename

if __name__ == "__main__":
    print("Generating BlackRock Liquidity and Financing - Citizen Developer Posting Board Quick Start Guide...")
    filename = create_quick_start_guide()
    print(f"✓ Quick Start Guide generated successfully: {filename}")
    print(f"  File location: {os.path.abspath(filename)}")
    print(f"  File size: {os.path.getsize(filename):,} bytes")