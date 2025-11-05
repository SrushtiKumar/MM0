"""
Simple Email Sender using HTTPs
This creates a working email solution without requiring SMTP setup
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_simple_email(to_email, subject, message, from_name, from_email):
    """
    Send email using Gmail's free SMTP service
    You need to set up Gmail App Password for this to work
    """
    
    # Gmail SMTP configuration
    smtp_server = "smtp.gmail.com"
    port = 587
    
    # You need to replace these with actual credentials
    sender_email = "your_gmail@gmail.com"  # Replace with actual Gmail
    password = "your_16_char_app_password"   # Replace with Gmail App Password
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = f"{from_name} <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg['Reply-To'] = from_email
    
    # Email body
    email_body = f"""
New Contact Form Submission:

Name: {from_name}
Email: {from_email}
Subject: {subject}

Message:
{message}

---
Reply to: {from_email}
    """
    
    msg.attach(MIMEText(email_body, 'plain'))
    
    # Send email
    try:
        # Create secure connection and send email
        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=context)
        server.login(sender_email, password)
        
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

# Test function
if __name__ == "__main__":
    # Test email sending
    result = send_simple_email(
        to_email="srushti_csd@ksit.edu.in",
        subject="Test from VeilForge",
        message="This is a test message from the contact form.",
        from_name="Test User",
        from_email="test@example.com"
    )
    print(f"Email sent: {result}")