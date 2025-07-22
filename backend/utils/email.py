import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_claim_notification(idea_owner_email, idea_title, claimer_name, claimer_skills, claimer_team):
    """
    Send email notification when an idea is claimed
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_DEFAULT_SENDER
        msg['To'] = idea_owner_email
        msg['Subject'] = f'Your idea "{idea_title}" has been claimed!'
        
        body = f"""
        <html>
        <body>
            <h2>Good news! Your idea has been claimed</h2>
            <p>Your idea "<strong>{idea_title}</strong>" has been claimed by:</p>
            <ul>
                <li><strong>Name:</strong> {claimer_name}</li>
                <li><strong>Team:</strong> {claimer_team or 'Not specified'}</li>
                <li><strong>Skills:</strong> {claimer_skills or 'Not specified'}</li>
            </ul>
            <p>They will be in touch with you soon to discuss the implementation.</p>
            <br>
            <p>Best regards,<br>The Posting Board Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        if Config.MAIL_SERVER != 'localhost':
            with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
                if Config.MAIL_USE_TLS:
                    server.starttls()
                if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
                    server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
                server.send_message(msg)
                print(f"Email sent to {idea_owner_email}")
        else:
            print(f"Email notification (not sent - no mail server configured):")
            print(f"To: {idea_owner_email}")
            print(f"Subject: {msg['Subject']}")
            print(f"Body: {body}")
            
    except Exception as e:
        print(f"Failed to send email: {str(e)}")