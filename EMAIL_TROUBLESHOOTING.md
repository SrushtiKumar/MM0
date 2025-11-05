# EmailJS Troubleshooting Guide

## Current Configuration
- Service ID: service_llf0hhj
- Template ID: template_86cmll6  
- Public Key: gxZ_jnSYM6BBWevvd
- Recipient: srushti_csd@ksit.edu.in

## Common Issues & Solutions

### 1. **Template Variables Mismatch**
Make sure your EmailJS template includes these variables:
```
Subject: New Contact Form Message: {{subject}}

From: {{from_name}}
Email: {{from_email}}
Phone: {{phone}}

Message:
{{message}}

---
Reply to: {{reply_to}}
```

### 2. **Service Configuration**
Verify in your EmailJS dashboard:
- ✅ Email service is connected (Gmail/Outlook)
- ✅ Service is active and not suspended
- ✅ Template is published (not in draft)
- ✅ Public key is copied correctly

### 3. **Testing Steps**
1. Open browser developer tools (F12)
2. Go to Console tab
3. Fill out and submit the contact form
4. Check console for detailed error messages

### 4. **Common Error Codes**
- **400**: Bad Request - Check template variables
- **422**: Unprocessable Entity - Service/template configuration issue
- **403**: Forbidden - Public key or service access issue
- **Network Error**: CORS or connectivity issue

### 5. **Quick Test**
Try this in browser console to test EmailJS directly:
```javascript
emailjs.send('service_llf0hhj', 'template_86cmll6', {
  from_name: 'Test User',
  from_email: 'test@example.com',
  subject: 'Test Subject',
  message: 'Test message',
  to_email: 'srushti_csd@ksit.edu.in'
}, 'gxZ_jnSYM6BBWevvd')
.then(result => console.log('Success:', result))
.catch(error => console.log('Error:', error));
```

### 6. **EmailJS Dashboard Checklist**
- [ ] Account is verified
- [ ] Service is connected to your email provider
- [ ] Template exists and matches variable names
- [ ] Monthly quota not exceeded
- [ ] No domain restrictions set

### 7. **Template Setup**
Your template should use these exact variable names:
- {{from_name}}
- {{from_email}}  
- {{phone}}
- {{subject}}
- {{message}}
- {{to_email}}
- {{reply_to}}

## Next Steps
1. Check browser console for specific error
2. Verify template variable names match exactly
3. Test with the console command above
4. Check EmailJS dashboard for any warnings