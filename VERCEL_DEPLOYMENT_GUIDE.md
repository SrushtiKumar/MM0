# VeilForge Vercel Deployment Guide

## Project Structure Overview

This project has been configured for deployment on Vercel with the following structure:

```
VeilForge/
├── frontend/                    # React + Vite frontend application
│   ├── src/                    # React source code
│   ├── dist/                   # Build output (generated)
│   ├── package.json           # Frontend dependencies and scripts
│   └── vite.config.ts         # Vite build configuration
├── api/                        # Vercel serverless functions
│   └── index.py               # Main FastAPI entry point for Vercel
├── requirements.txt            # Python dependencies for backend
├── package.json               # Root package.json with build scripts
├── vercel.json                # Vercel deployment configuration
├── enhanced_app.py            # Main FastAPI application (imported by api/index.py)
├── app_backup.py              # Original app.py (renamed, not used)
└── [steganography modules]    # Python modules for steganography functions
```

## Key Configuration Files

### 1. vercel.json
- Configures Vercel deployment settings
- Sets up routing: `/api/*` → Python serverless function, `/*` → React frontend
- Defines build commands and output directories
- Configures serverless function settings (memory, timeout, etc.)

### 2. api/index.py
- Entry point for Vercel's Python serverless functions
- Imports and exports the FastAPI app from enhanced_app.py
- Handles path configuration for module imports
- Sets up environment variables for production

### 3. requirements.txt
- Optimized Python dependencies for serverless deployment
- Removed large/incompatible packages (librosa, uvicorn)
- Uses opencv-python-headless for better serverless compatibility

### 4. package.json (root)
- Defines build commands for Vercel
- Sets up workspace configuration
- Includes engines specification for Node.js version

## Deployment Steps

### Prerequisites
1. Install Vercel CLI: `npm install -g vercel`
2. Create Vercel account at https://vercel.com
3. Push your code to GitHub repository

### Option 1: Deploy via Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect the configuration
5. Click "Deploy"

### Option 2: Deploy via CLI
1. Run `vercel` in the project root
2. Follow the prompts to link your project
3. Run `vercel --prod` for production deployment

## Environment Variables

### **🔒 CRITICAL: Required Environment Variables**

**IMPORTANT**: All API keys have been secured and MUST be configured in Vercel:

#### **Required Variables:**
```bash
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here
```

#### **Frontend Variables (EmailJS):**
```bash
VITE_EMAILJS_PUBLIC_KEY=your-emailjs-public-key
VITE_EMAILJS_SERVICE_ID=service_xxxxxxx
VITE_EMAILJS_TEMPLATE_ID=template_xxxxxxx
VITE_RECIPIENT_EMAIL=contact@yourdomain.com
```

#### **Backend Variables (Email - Optional):**
```bash
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
RECIPIENT_EMAIL=contact@yourdomain.com
ENABLE_EMAIL=true
```

### **Adding Variables to Vercel:**
- Vercel Dashboard → Project Settings → Environment Variables
- Or via CLI: `vercel env add [NAME] [VALUE]`

**⚠️ Without these variables, the application will not function properly!**

See `SECURITY_SETUP_GUIDE.md` for detailed configuration instructions.

## Build Process

### Frontend Build (React + Vite)
1. Vercel runs: `cd frontend && npm install && npm run build`
2. Builds React app to `frontend/dist/`
3. Static files are served directly by Vercel CDN

### Backend Build (FastAPI)
1. Vercel installs Python dependencies from `requirements.txt`
2. Creates serverless function from `api/index.py`
3. Function handles all `/api/*` requests

## API Endpoints

All backend endpoints are prefixed with `/api/`:
- `GET /api/health` - Health check
- `POST /api/embed` - Embed files in carriers
- `POST /api/extract` - Extract hidden files
- `POST /api/contact` - Contact form
- And many more... (see enhanced_app.py for full list)

## File Upload Limits

Vercel has the following limits:
- Request body size: 4.5MB (Hobby), 100MB (Pro)
- Function execution time: 10s (Hobby), 60s (Pro), 900s (Enterprise)
- Function memory: 1024MB (Hobby), 3008MB (Pro/Enterprise)

For large file processing, consider:
1. Upgrading to Pro plan
2. Implementing chunked uploads
3. Using external storage (S3, etc.)

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   - Ensure all required .py files are in the root directory
   - Check that dependencies are in requirements.txt

2. **Build Failures**
   - Check Node.js version (should be ≥18)
   - Verify frontend/package.json dependencies

3. **Function Timeouts**
   - Large files may exceed execution time limits
   - Consider Pro plan or optimize processing

4. **CORS Issues**
   - CORS is configured in enhanced_app.py
   - Add your Vercel domain to allowed origins if needed

### Debugging
1. Check Vercel Function Logs in the dashboard
2. Use `vercel logs` CLI command
3. Test API endpoints individually

## Production Considerations

1. **Security**
   - Add rate limiting for API endpoints
   - Implement proper authentication
   - Validate all file uploads

2. **Performance**
   - Use CDN for static assets (automatic with Vercel)
   - Optimize image/video processing
   - Consider caching strategies

3. **Monitoring**
   - Set up error tracking (Sentry, etc.)
   - Monitor function execution times
   - Track usage metrics

## Next Steps After Deployment

1. Test all functionality on the deployed version
2. Set up custom domain (if needed)
3. Configure environment variables for production
4. Set up monitoring and alerts
5. Document API endpoints for users

## Support

For deployment issues:
- Vercel Documentation: https://vercel.com/docs
- Vercel Community: https://github.com/vercel/vercel/discussions
- FastAPI Documentation: https://fastapi.tiangolo.com/

## Changes Made for Vercel Compatibility

1. **File Structure**
   - Created `/api` directory with `index.py` entry point
   - Renamed `app.py` → `app_backup.py` (enhanced_app.py is main backend)

2. **Dependencies**
   - Optimized `requirements.txt` for serverless environment
   - Removed uvicorn (not needed in Vercel)
   - Used opencv-python-headless instead of opencv-python

3. **Code Changes**
   - Commented out uvicorn runner in enhanced_app.py
   - Removed StaticFiles import (not used)
   - Commented out template serving endpoint

4. **Configuration**
   - Added comprehensive vercel.json
   - Updated root package.json with build commands
   - Configured proper routing and CORS