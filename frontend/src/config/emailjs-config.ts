// EmailJS Configuration
// You need to replace these values with your actual EmailJS credentials

export const EMAILJS_CONFIG = {
  // Your EmailJS public key (found in your EmailJS account settings)
  PUBLIC_KEY: 'gxZ_jnSYM6BBWevvd', // Replace with your actual public key
  
  // Your EmailJS service ID (created in your EmailJS services)  
  SERVICE_ID: 'service_llf0hhj', // Your actual service ID
  
  // Your EmailJS template ID (created in your EmailJS email templates)
  TEMPLATE_ID: 'template_nzm50pk', // Replace with your actual template ID
  
  // The recipient email address
  TO_EMAIL: 'srushti_csd@ksit.edu.in'
};

// Template variables that will be sent to your email template:
// {{to_email}} - Recipient email ()
// {{from_name}} - Sender's name
// {{from_email}} - Sender's email
// {{phone}} - Sender's phone number
// {{subject}} - Message subject
// {{message}} - Message content
// {{reply_to}} - Reply-to email (sender's email)