# Email Configuration for VeilForge Contact Form
# Replace these values with your actual email credentials

EMAIL_CONFIG = {
    # SMTP Server Configuration
    'SMTP_SERVER': 'smtp.gmail.com',  # Gmail SMTP server
    'SMTP_PORT': 587,                 # Gmail SMTP port
    
    # Email Credentials - ADD YOUR REAL GMAIL CREDENTIALS HERE
    'EMAIL_USER': 'your_actual_email@gmail.com',        # Replace with your Gmail
    'EMAIL_PASSWORD': 'your_16_char_app_password',      # Replace with Gmail App Password
    
    # Recipient Configuration
    'RECIPIENT_EMAIL': 'srushti_csd@ksit.edu.in',
    'SENDER_NAME': 'VeilForge Contact System',
    
    # Email Templates
    'SUBJECT_TEMPLATE': 'VeilForge Contact: {subject}',
    
    # Enable/Disable email sending for testing
    'ENABLE_EMAIL': True  # Changed to True - will work when you add real credentials
}

# Instructions for Gmail App Password:
"""
To use Gmail SMTP, you need to:
1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Generate an "App Password" for this application
4. Use that App Password (not your regular Gmail password)
5. Set ENABLE_EMAIL to True
"""

# Alternative Email Services:
"""
For other email providers:
- Outlook/Hotmail: smtp-mail.outlook.com:587
- Yahoo: smtp.mail.yahoo.com:587
- Custom SMTP: Use your provider's SMTP settings
"""