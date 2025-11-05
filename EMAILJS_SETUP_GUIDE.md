# EmailJS Setup Guide for Contact Form

## Overview
The contact form is now configured to send emails to `srushti_csd@ksit.edu.in` using EmailJS service. You need to complete the EmailJS setup to make it functional.

## Setup Steps

### 1. Create EmailJS Account
1. Go to [https://www.emailjs.com/](https://www.emailjs.com/)
2. Sign up for a free account
3. Verify your email address

### 2. Create Email Service
1. In your EmailJS dashboard, go to "Email Services"
2. Click "Add New Service"
3. Choose your email provider (Gmail, Outlook, etc.)
4. Follow the setup instructions for your provider
5. Note down the **Service ID** (e.g., `service_abc123`)

### 3. Create Email Template
1. Go to "Email Templates" in your dashboard
2. Click "Create New Template"
3. Use this template structure:

```
Subject: New Contact Form Message: {{subject}}

From: {{from_name}}
Email: {{from_email}}
Phone: {{phone}}

Subject: {{subject}}

Message:
{{message}}

---
This message was sent from the contact form.
Reply to: {{reply_to}}
```

4. Save the template and note down the **Template ID** (e.g., `template_xyz789`)

### 4. Get Public Key
1. Go to "Account" settings in your EmailJS dashboard
2. Find your **Public Key** (e.g., `NiFJMwWh5ZpeV0Dxi`)

### 5. Update Configuration
1. Open `frontend/src/config/emailjs-config.ts`
2. Replace the placeholder values:

```typescript
export const EMAILJS_CONFIG = {
  PUBLIC_KEY: 'your_actual_public_key',
  SERVICE_ID: 'your_actual_service_id',
  TEMPLATE_ID: 'your_actual_template_id',
  TO_EMAIL: 'srushti_csd@ksit.edu.in'
};
```

### 6. Test the Contact Form
1. Run your application
2. Go to the Contact page
3. Fill out and submit the form
4. Check your email at `srushti_csd@ksit.edu.in`

## Email Template Variables
The following variables are available in your EmailJS template:
- `{{to_email}}` - Recipient email (srushti_csd@ksit.edu.in)
- `{{from_name}}` - Sender's name
- `{{from_email}}` - Sender's email address
- `{{phone}}` - Sender's phone number
- `{{subject}}` - Message subject
- `{{message}}` - Message content
- `{{reply_to}}` - Reply-to email (sender's email)

## Features Implemented
✅ Form validation
✅ Loading state during email sending
✅ Success/error feedback
✅ Form reset after successful submission
✅ Configuration file for easy updates
✅ Email template with all sender details

## Troubleshooting
- If emails aren't being sent, check the browser console for errors
- Verify that all configuration values are correct
- Make sure your EmailJS service is properly configured
- Check EmailJS dashboard for usage limits and quota

## Free Tier Limits
EmailJS free tier includes:
- 200 emails per month
- Basic email templates
- Standard support

For higher volume, consider upgrading to a paid plan.