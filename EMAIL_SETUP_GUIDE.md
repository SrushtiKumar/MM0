# VeilForge Contact Form Email Setup Guide

## Current Status 
✅ **Backend email functionality implemented**  
✅ **Frontend contact form ready**  
⚠️ **Email credentials need configuration for actual email sending**

## Quick Test (Current Setup)
The contact form will now:
1. Show detailed error logs in console for EmailJS debugging
2. Send to backend API which logs all contact messages
3. Return appropriate success/failure messages
4. Work reliably even without email configuration

## To Enable Actual Email Sending

### Option 1: Configure Gmail SMTP (Recommended)
1. **Edit `email_config.py`:**
   ```python
   EMAIL_CONFIG = {
       'SMTP_SERVER': 'smtp.gmail.com',
       'SMTP_PORT': 587,
       'EMAIL_USER': 'your_gmail@gmail.com',      # Your Gmail address
       'EMAIL_PASSWORD': 'your_app_password',     # Gmail App Password (NOT regular password)
       'RECIPIENT_EMAIL': 'srushti_csd@ksit.edu.in',
       'SENDER_NAME': 'VeilForge Contact System',
       'SUBJECT_TEMPLATE': 'VeilForge Contact: {subject}',
       'ENABLE_EMAIL': True  # Change to True
   }
   ```

2. **Get Gmail App Password:**
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Enable 2-Factor Authentication
   - Go to "Security" → "App passwords"
   - Generate password for "Mail"
   - Use that 16-character password (not your regular Gmail password)

3. **Restart backend server**

### Option 2: Use Alternative Email Service
Replace the SMTP configuration with:
- **Outlook**: `smtp-mail.outlook.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Custom SMTP**: Use your provider's settings

### Option 3: Use EmailJS (Fix Configuration)
1. Go to [EmailJS Dashboard](https://www.emailjs.com/)
2. Create account and get real Service ID, Template ID, Public Key
3. Replace values in `Contact.tsx`

## Testing
1. **Start both servers:**
   ```
   Frontend: npm run dev (http://localhost:8080)
   Backend: python enhanced_app.py (http://localhost:8000)
   ```

2. **Test contact form:**
   - Fill out the contact form
   - Check browser console for detailed logs
   - Check backend terminal for email processing logs

3. **Verify email delivery:**
   - Check `srushti_csd@ksit.edu.in` inbox
   - If no email, check spam folder
   - Review backend logs for error messages

## Current Behavior (Without Email Config)
- ✅ Form submits successfully
- ✅ Messages logged to backend console
- ✅ User sees success message
- ✅ No error messages shown
- ⚠️ No actual emails sent (logged for manual processing)

## With Email Config Enabled
- ✅ All above features
- ✅ Actual emails sent to srushti_csd@ksit.edu.in
- ✅ SMTP error handling and fallback
- ✅ Detailed delivery confirmation

## Troubleshooting
- **"Authentication failed"**: Check Gmail App Password
- **"Connection refused"**: Check SMTP server/port
- **"Rate limited"**: Wait and try again
- **Still no emails**: Check spam folder or try different email service