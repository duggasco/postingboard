#!/usr/bin/env python3
"""
Citizen Developer Posting Board - Quick Start Guide Generator
Generates a 3-page PDF quick start guide for users and managers
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
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
        self.setFont("Helvetica", 9)
        self.setFillColor(HexColor('#666666'))
        self.drawRightString(letter[0] - 0.5*inch, 0.5*inch, 
                            f"Page {self._pageNumber} of 3")

def create_quick_start_guide():
    """Generate the quick start guide PDF"""
    
    # Create PDF document
    filename = "Citizen_Developer_Posting_Board_Quick_Start_Guide.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    # Container for the 'Flowable' objects
    story = []
    
    # Define custom styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=SECONDARY_COLOR,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=PRIMARY_COLOR,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # Heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=PRIMARY_COLOR,
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Subheading style
    subheading_style = ParagraphStyle(
        'Subheading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=SECONDARY_COLOR,
        spaceAfter=6,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=black,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=14
    )
    
    # Bullet style
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=body_style,
        leftIndent=20,
        bulletIndent=10
    )
    
    # PAGE 1: Getting Started
    story.append(Paragraph("Citizen Developer Posting Board", title_style))
    story.append(Paragraph("Quick Start Guide", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    
    # What is it?
    story.append(Paragraph("What is the Posting Board?", heading_style))
    story.append(Paragraph(
        "The Citizen Developer Posting Board is a platform where teams can post their automation "
        "and development needs, while skilled employees from any department can discover and "
        "implement these solutions. It democratizes software development by connecting business "
        "needs with technical talent across the organization.",
        body_style
    ))
    story.append(Spacer(1, 0.25*inch))
    
    # Getting Started
    story.append(Paragraph("Getting Started", heading_style))
    
    # Navigation
    story.append(Paragraph("1. Navigate to the Platform", subheading_style))
    story.append(Paragraph(
        "Access the Posting Board at your organization's URL. The home page displays all available "
        "ideas that need implementation.",
        body_style
    ))
    
    # Authentication
    story.append(Paragraph("2. Verify Your Email", subheading_style))
    story.append(Paragraph(
        "Click 'Login' or any protected feature to start the authentication process:",
        body_style
    ))
    story.append(Paragraph("• Enter your corporate email address", bullet_style))
    story.append(Paragraph("• Check your email for a 6-digit verification code", bullet_style))
    story.append(Paragraph("• Enter the code within 3 minutes to complete verification", bullet_style))
    story.append(Paragraph("• Complete your profile with name, role, team, and skills", bullet_style))
    
    # Main Navigation
    story.append(Paragraph("3. Explore the Platform", subheading_style))
    story.append(Paragraph("The main navigation provides access to:", body_style))
    story.append(Paragraph("• <b>All Ideas</b> - Browse all open opportunities", bullet_style))
    story.append(Paragraph("• <b>My Ideas</b> - View ideas you've submitted or claimed", bullet_style))
    story.append(Paragraph("• <b>My Team</b> - Team analytics (managers only)", bullet_style))
    story.append(Paragraph("• <b>Submit Idea</b> - Post a new development need", bullet_style))
    
    # Browse Ideas
    story.append(Paragraph("Browsing Ideas", heading_style))
    story.append(Paragraph("The home page shows idea cards with:", body_style))
    story.append(Paragraph("• Title and description of the need", bullet_style))
    story.append(Paragraph("• Required skills and priority level", bullet_style))
    story.append(Paragraph("• Size estimate (Small/Medium/Large/Extra Large)", bullet_style))
    story.append(Paragraph("• Bounty or recognition offered", bullet_style))
    story.append(Paragraph("• Team and submission details", bullet_style))
    
    story.append(Paragraph("Use the filters at the top to find ideas matching your skills.", body_style))
    
    # PAGE 2: User Functions
    story.append(PageBreak())
    story.append(Paragraph("For All Users", heading_style))
    
    # Submitting Ideas
    story.append(Paragraph("Submitting an Idea", subheading_style))
    story.append(Paragraph("Click 'Submit Idea' in the navigation to post a new need:", body_style))
    story.append(Paragraph("• <b>Title:</b> Brief, descriptive name for your idea", bullet_style))
    story.append(Paragraph("• <b>Description:</b> Detailed explanation of what you need", bullet_style))
    story.append(Paragraph("• <b>Team:</b> Your team (auto-filled if assigned)", bullet_style))
    story.append(Paragraph("• <b>Priority:</b> Low, Medium, or High urgency", bullet_style))
    story.append(Paragraph("• <b>Size:</b> Estimated effort required", bullet_style))
    story.append(Paragraph("• <b>Skills:</b> Technical skills needed for implementation", bullet_style))
    story.append(Paragraph("• <b>Needed By:</b> Target completion date", bullet_style))
    story.append(Paragraph("• <b>Bounty:</b> Recognition or rewards offered", bullet_style))
    
    # Claiming Ideas
    story.append(Paragraph("Claiming Ideas (Developers Only)", subheading_style))
    story.append(Paragraph(
        "If you have Developer or Citizen Developer role, you can claim ideas to work on:",
        body_style
    ))
    story.append(Paragraph("1. Click 'View Details' on an idea card", bullet_style))
    story.append(Paragraph("2. Review the full requirements and bounty", bullet_style))
    story.append(Paragraph("3. Click 'Claim This Idea' if you have the required skills", bullet_style))
    story.append(Paragraph("4. Wait for dual approval from idea owner and your manager", bullet_style))
    story.append(Paragraph("5. Once approved, the idea moves to 'Claimed' status", bullet_style))
    
    # My Ideas Dashboard
    story.append(Paragraph("My Ideas Dashboard", subheading_style))
    story.append(Paragraph("Track your activity and manage approvals:", body_style))
    story.append(Paragraph("• View statistics: Submitted, Claimed, Open, Complete", bullet_style))
    story.append(Paragraph("• See all ideas you've submitted with current status", bullet_style))
    story.append(Paragraph("• Track ideas you're working on", bullet_style))
    story.append(Paragraph("• Approve/deny claim requests for your ideas", bullet_style))
    story.append(Paragraph("• Monitor pending approvals", bullet_style))
    
    # Notifications
    story.append(Paragraph("Notifications", subheading_style))
    story.append(Paragraph(
        "The bell icon in the navigation shows unread notifications for:",
        body_style
    ))
    story.append(Paragraph("• Claim requests on your ideas", bullet_style))
    story.append(Paragraph("• Approval decisions on your claims", bullet_style))
    story.append(Paragraph("• Status changes on ideas you're involved with", bullet_style))
    story.append(Paragraph("• Team updates and assignments", bullet_style))
    
    # PAGE 3: Manager Functions
    story.append(PageBreak())
    story.append(Paragraph("For Managers", heading_style))
    
    # Manager Role
    story.append(Paragraph("Manager Capabilities", subheading_style))
    story.append(Paragraph(
        "As a manager, you have additional responsibilities and tools:",
        body_style
    ))
    story.append(Paragraph("• Approve team members' claim requests", bullet_style))
    story.append(Paragraph("• View comprehensive team analytics", bullet_style))
    story.append(Paragraph("• Assign ideas to specific team members", bullet_style))
    story.append(Paragraph("• Edit team member profiles and skills", bullet_style))
    story.append(Paragraph("• Monitor team spending on bounties", bullet_style))
    
    # My Team Dashboard
    story.append(Paragraph("My Team Dashboard", subheading_style))
    story.append(Paragraph("Access 'My Team' in navigation to view:", body_style))
    
    story.append(Paragraph("<b>Team Overview:</b>", bullet_style))
    story.append(Paragraph("  - Member count and activity metrics", bullet_style))
    story.append(Paragraph("  - Ideas submitted vs. claimed", bullet_style))
    story.append(Paragraph("  - Completion rate and pending approvals", bullet_style))
    story.append(Paragraph("  - Total spending on bounties", bullet_style))
    
    story.append(Paragraph("<b>Visual Analytics:</b>", bullet_style))
    story.append(Paragraph("  - Priority and size distribution charts", bullet_style))
    story.append(Paragraph("  - Team skills vs. skills needed (gap analysis)", bullet_style))
    story.append(Paragraph("  - Spending trends over time", bullet_style))
    
    story.append(Paragraph("<b>Team Members Table:</b>", bullet_style))
    story.append(Paragraph("  - Individual performance metrics", bullet_style))
    story.append(Paragraph("  - Edit member profiles and skills", bullet_style))
    story.append(Paragraph("  - Track submitted, claimed, and completed ideas", bullet_style))
    
    # Approval Workflow
    story.append(Paragraph("Approval Workflow", subheading_style))
    story.append(Paragraph("When team members request to claim ideas:", body_style))
    story.append(Paragraph("1. You receive a notification for approval", bullet_style))
    story.append(Paragraph("2. Review the claim request in My Ideas or via notification", bullet_style))
    story.append(Paragraph("3. Consider member's skills and current workload", bullet_style))
    story.append(Paragraph("4. Approve or deny with one click", bullet_style))
    story.append(Paragraph("5. Both your approval and idea owner's approval are required", bullet_style))
    
    # Quick Tips
    story.append(Paragraph("Quick Tips", heading_style))
    story.append(Paragraph("• Check notifications regularly for pending approvals", bullet_style))
    story.append(Paragraph("• Use filters to find ideas matching your team's skills", bullet_style))
    story.append(Paragraph("• Encourage team members to keep profiles updated", bullet_style))
    story.append(Paragraph("• Monitor the skills gap chart to identify training needs", bullet_style))
    story.append(Paragraph("• Ideas with monetary bounties over $50 require approval", bullet_style))
    story.append(Paragraph("• Use 'My Team' to track spending and budget impact", bullet_style))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y')}",
        ParagraphStyle('Footer', parent=body_style, fontSize=9, textColor=HexColor('#666666'), alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    
    return filename

if __name__ == "__main__":
    print("Generating Citizen Developer Posting Board Quick Start Guide...")
    filename = create_quick_start_guide()
    print(f"✓ Quick Start Guide generated successfully: {filename}")
    print(f"  File location: {os.path.abspath(filename)}")
    print(f"  File size: {os.path.getsize(filename):,} bytes")