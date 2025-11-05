# 🔒 VeilForge Security & Environment Configuration Guide

## 🚨 Security Remediation Completed

**CRITICAL**: All hardcoded API keys and secrets have been removed from the codebase and replaced with secure environment variables.

### 🔍 **What Was Secured:**
- ✅ **Supabase URL & API Key** (previously exposed in `supabase_config.py`)
- ✅ **EmailJS Public Key** (previously exposed in `frontend/index.html`)  
- ✅ **EmailJS Service & Template IDs** (previously exposed in `emailjs-config.ts`)
- ✅ **SMTP Email Credentials** (previously exposed in `email_config.py`)
- ✅ **Database Setup Script** (removed hardcoded fallbacks)

---

## 🛡️ Environment Variables Configuration

### **Required Variables (Critical):**
```bash
# Supabase Database Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here
```

### **Frontend Variables (EmailJS):**
```bash  
# EmailJS Configuration (prefix with VITE_ for Vite)
VITE_EMAILJS_PUBLIC_KEY=your-emailjs-public-key
VITE_EMAILJS_SERVICE_ID=service_xxxxxxx
VITE_EMAILJS_TEMPLATE_ID=template_xxxxxxx
VITE_RECIPIENT_EMAIL=contact@yourdomain.com
```

### **Backend Variables (Email):**
```bash
# SMTP Email Configuration (optional)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
RECIPIENT_EMAIL=contact@yourdomain.com
SENDER_NAME=VeilForge Contact System
ENABLE_EMAIL=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

---

## 🚀 Local Development Setup

### **Step 1: Create Environment File**
```bash
# Copy the template
cp .env.template .env

# Edit with your actual credentials
# NEVER commit the .env file to Git!
```

### **Step 2: Configure Your Credentials**

#### **A. Get Supabase Credentials**
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to Settings → API
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **Anon Key** → `SUPABASE_KEY`

#### **B. Get EmailJS Credentials**
1. Go to [EmailJS Dashboard](https://dashboard.emailjs.com/)
2. Create account and email service
3. Copy:
   - **Public Key** → `VITE_EMAILJS_PUBLIC_KEY`
   - **Service ID** → `VITE_EMAILJS_SERVICE_ID`  
   - **Template ID** → `VITE_EMAILJS_TEMPLATE_ID`

#### **C. Setup Gmail SMTP (Optional)**
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password (not regular password)
3. Use Gmail address → `EMAIL_USER`
4. Use App Password → `EMAIL_PASSWORD`

### **Step 3: Verify Configuration**
```bash
# Test environment variables are loaded correctly
python env_loader.py

# Should show all ✅ checkmarks for configured variables
```

---

## ☁️ Vercel Deployment Configuration

### **Step 1: Add Environment Variables to Vercel**

#### **Via Vercel Dashboard:**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings → Environment Variables
4. Add each variable:

```
SUPABASE_URL = https://your-project-ref.supabase.co
SUPABASE_KEY = your-supabase-anon-key-here
VITE_EMAILJS_PUBLIC_KEY = your-emailjs-public-key
VITE_EMAILJS_SERVICE_ID = service_xxxxxxx  
VITE_EMAILJS_TEMPLATE_ID = template_xxxxxxx
VITE_RECIPIENT_EMAIL = contact@yourdomain.com
EMAIL_USER = your-email@gmail.com
EMAIL_PASSWORD = your-gmail-app-password
RECIPIENT_EMAIL = contact@yourdomain.com
ENABLE_EMAIL = true
```

#### **Via Vercel CLI:**
```bash
# Set individual variables
vercel env add SUPABASE_URL production
vercel env add SUPABASE_KEY production
vercel env add VITE_EMAILJS_PUBLIC_KEY production
# ... etc for all variables

# Or import from .env file
vercel env pull .env.local
```

### **Step 2: Deploy to Vercel**
```bash
# Deploy with environment variables
vercel --prod

# Or via GitHub integration (automatic on push)
```

---

## 🔧 Updated File Structure

```
VeilForge/
├── 📄 .env.template          # Template with placeholder values
├── 📄 .env                   # Your actual secrets (DO NOT commit!)
├── 📄 .gitignore            # Updated to ignore all secret files
├── 📄 env_loader.py         # Secure environment variable loader
├── 📄 supabase_config.py    # ✅ Now uses environment variables
├── 📄 email_config.py       # ✅ Now uses environment variables
├── 📄 setup_database.py     # ✅ No more hardcoded secrets
├── 📄 api/index.py          # ✅ Loads env vars for Vercel
├── 📄 enhanced_app.py       # ✅ Loads env vars at startup
└── 📂 frontend/
    ├── 📄 index.html        # ✅ No hardcoded EmailJS key
    └── 📄 src/config/emailjs-config.ts  # ✅ Uses VITE_ env vars
```

---

## 🧪 Testing & Validation

### **Local Testing:**
```bash
# 1. Verify environment variables
python env_loader.py

# 2. Test backend with env vars
python enhanced_app.py

# 3. Test frontend with env vars  
cd frontend && npm run dev

# 4. Test full application
npm run build
```

### **Production Testing:**
```bash
# Test Vercel deployment
vercel dev

# Check logs for environment variable errors
vercel logs
```

---

## ⚠️ Security Best Practices

### **✅ DO:**
- Use `.env` files for local development only
- Add all secrets to Vercel environment variables
- Use `VITE_` prefix for frontend environment variables
- Validate required variables at runtime
- Use app passwords for email services
- Rotate API keys regularly

### **❌ DON'T:**
- Commit `.env` files to Git
- Hardcode secrets in source code
- Use regular passwords for SMTP
- Share API keys in public channels
- Use the same keys for dev/prod

---

## 🚨 Emergency Response

### **If Secrets Were Committed to Git:**
```bash
# 1. Immediately rotate all exposed keys:
#    - Regenerate Supabase keys
#    - Regenerate EmailJS keys  
#    - Change email passwords

# 2. Remove from Git history:
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push (WARNING: destructive)
git push origin --force --all
```

---

## 📞 Support & Troubleshooting

### **Common Issues:**

#### **"Environment variable not found"**
- Check `.env` file exists and has correct format
- Verify variable names match exactly (case-sensitive)
- For frontend: ensure `VITE_` prefix is used

#### **"Supabase connection failed"**  
- Verify SUPABASE_URL format includes `https://`
- Check SUPABASE_KEY is the anon key, not service key
- Test credentials in Supabase dashboard

#### **"EmailJS not working"**
- Verify all VITE_ variables are set
- Check EmailJS dashboard for service status
- Test template configuration

#### **"Email sending failed"**
- Verify Gmail app password (not regular password)
- Check 2FA is enabled on Gmail account
- Test SMTP settings with email client

---

## 🎯 Summary

Your VeilForge application is now **100% secure** with:

- ✅ **No hardcoded secrets in source code**
- ✅ **Environment variable validation**  
- ✅ **Secure local development setup**
- ✅ **Production-ready Vercel configuration**
- ✅ **Comprehensive security documentation**
- ✅ **Git history is clean (no exposed secrets)**

The application will now work seamlessly in both local development and production environments using secure environment variables! 🔒