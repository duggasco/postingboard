import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from database import get_session
from models import EmailSettings

def send_claim_notification(idea, claim):
    """Send email notification when an idea is claimed."""
    db = get_session()
    try:
        # Get email settings from database
        settings = db.query(EmailSettings).filter_by(is_active=True).first()
        
        if not settings or not settings.smtp_server:
            print(f"Email notification (not sent - no mail server configured):")
            print(f"To: {idea.email}")
            print(f"Subject: Your idea '{idea.title}' has been claimed!")
            print(f"Claimer: {claim.claimer_name} from {claim.claimer_team}")
            return
        
        msg = MIMEMultipart()
        msg['From'] = f"{settings.from_name} <{settings.from_email}>"
        msg['To'] = idea.email
        msg['Subject'] = f'Your idea "{idea.title}" has been claimed!'
        
        body = f"""
        <html>
        <body>
            <h2>Good news! Your idea has been claimed</h2>
            <p>Your idea "<strong>{idea.title}</strong>" has been claimed by:</p>
            <ul>
                <li><strong>Name:</strong> {claim.claimer_name}</li>
                <li><strong>Team:</strong> {claim.claimer_team or 'Not specified'}</li>
                <li><strong>Skills:</strong> {claim.claimer_skills or 'Not specified'}</li>
            </ul>
            <p>They will be in touch with you soon to discuss the implementation.</p>
            <br>
            <p>Best regards,<br>The Posting Board Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
            print(f"Email sent to {idea.email}")
            
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
    finally:
        db.close()

def send_verification_code(email, code):
    """Send email verification code."""
    db = get_session()
    try:
        # Get email settings from database
        settings = db.query(EmailSettings).filter_by(is_active=True).first()
        
        if not settings or not settings.smtp_server:
            print(f"Verification code (not sent - no mail server configured):")
            print(f"To: {email}")
            print(f"Code: {code}")
            print(f"Valid for: 3 minutes")
            return True
        
        msg = MIMEMultipart()
        msg['From'] = f"{settings.from_name} <{settings.from_email}>"
        msg['To'] = email
        msg['Subject'] = 'Your Posting Board Verification Code'
        
        body = f"""
        <html>
        <body>
            <h2>Email Verification</h2>
            <p>Your verification code is:</p>
            <h1 style="text-align: center; color: #4CAF50; font-size: 48px; letter-spacing: 10px;">{code}</h1>
            <p>This code will expire in <strong>3 minutes</strong>.</p>
            <p>If you didn't request this code, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The Posting Board Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
            print(f"Verification email sent to {email}")
            return True
            
    except Exception as e:
        print(f"Failed to send verification email: {str(e)}")
        return False
    finally:
        db.close()