import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_claim_notification(idea, claim):
    """Send email notification when an idea is claimed."""
    try:
        if not Config.SMTP_USERNAME:
            print(f"Email notification (not sent - no mail server configured):")
            print(f"To: {idea.email}")
            print(f"Subject: Your idea '{idea.title}' has been claimed!")
            print(f"Claimer: {claim.claimer_name} from {claim.claimer_team}")
            return
        
        msg = MIMEMultipart()
        msg['From'] = Config.SMTP_USERNAME
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
        
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
            server.send_message(msg)
            print(f"Email sent to {idea.email}")
            
    except Exception as e:
        print(f"Failed to send email: {str(e)}")