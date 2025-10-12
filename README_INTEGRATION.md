# Enhanced Steganography Application Suite

A comprehensive steganography application with React frontend and FastAPI backend, featuring:

- 🖼️ **Image Steganography** - Hide data in PNG, JPEG, BMP, TIFF images
- 🎥 **Video Steganography** - Hide data in MP4, AVI, MOV, MKV videos  
- 🎵 **Audio Steganography** - Hide data in WAV, MP3, FLAC audio files
- 📄 **Document Steganography** - Hide data in PDF, DOCX, TXT documents
- 🔐 **Secure Encryption** - AES-256-GCM encryption with password protection
- 🌐 **Modern Web Interface** - React frontend with real-time progress tracking
- 💾 **Database Integration** - Supabase database for operation logging and user management

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Supabase account (optional, for database features)

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python start_application.bat
# Choose option 1 to start backend only
```

### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install Node.js dependencies  
npm install

# Start the development server
npm run dev
```

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
vF/
├── enhanced_app.py                 # Main FastAPI backend server
├── supabase_config.py             # Supabase database configuration
├── supabase_service.py            # Database service layer
├── setup_database.py              # Database setup script
├── start_application.bat          # Master startup script
├── start_enhanced_backend.bat     # Backend startup script
├── start_frontend.bat             # Frontend startup script
├── database_schema.sql            # Database schema
├── enhanced_web_*_stego.py        # Steganography modules
├── frontend/                      # React frontend application
│   ├── src/
│   │   ├── pages/General.tsx      # Main steganography interface
│   │   ├── services/apiService.ts # API client service
│   │   └── ...
│   ├── package.json
│   └── ...
└── README_INTEGRATION.md          # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Supabase Configuration (optional)
SUPABASE_URL=https://ldhzvzxmnshpboocnpiv.supabase.co
SUPABASE_KEY=your-anon-key-here
```

### Frontend Configuration

The frontend automatically connects to the backend at `http://localhost:8000`. 

To change the API endpoint, update `API_BASE_URL` in `frontend/src/services/apiService.ts`.

## 🎯 Features

### Steganography Operations

1. **Embed Data**
   - Upload carrier files (images, videos, audio, documents)
   - Hide text messages or files
   - Secure encryption with custom passwords
   - Real-time progress tracking

2. **Extract Data**  
   - Upload steganographic files
   - Enter decryption password
   - Download extracted content
   - Support for various output formats

### Security Features

- 🔐 **AES-256-GCM Encryption** - Military-grade encryption
- 🗝️ **Password Protection** - Custom passwords with strength validation
- 🛡️ **Secure Password Generation** - Built-in secure password generator
- ✅ **Integrity Verification** - SHA-256 checksums for data integrity

### Database Features (Optional)

- 👤 **User Management** - User registration and authentication
- 📊 **Operation Logging** - Track all steganography operations
- 📈 **Statistics** - Usage analytics and success rates
- 🗂️ **File Metadata** - Detailed file information storage

## 🌐 API Endpoints

### Core Endpoints

- `GET /api/health` - Health check and system status
- `GET /api/supported-formats` - Get supported file formats
- `POST /api/embed` - Embed data into carrier files
- `POST /api/extract` - Extract data from steganographic files
- `GET /api/generate-password` - Generate secure passwords

### Operation Management

- `GET /api/operations/{id}/status` - Check operation status
- `GET /api/operations/{id}/download` - Download result files
- `DELETE /api/operations/{id}` - Delete operation and files

### User Management (Optional)

- `POST /api/users/register` - Register new user
- `GET /api/users/{id}/operations` - Get user operation history
- `GET /api/users/{id}/stats` - Get user statistics

## 📱 Frontend Interface

### General Protection Page

The main steganography interface (`/general`) provides:

1. **Embed Tab**
   - Carrier file upload with drag-and-drop
   - Content type selection (text, image, audio, video, file)
   - Text editor for messages
   - Password input with generation
   - Encryption settings
   - Real-time progress tracking

2. **Extract Tab**
   - Steganographic file upload
   - Password input
   - Output format selection
   - Progress monitoring
   - Result download

3. **Settings Tab**
   - Project configuration
   - Encryption preferences
   - Advanced options

## 🛠️ Development

### Running in Development Mode

1. **Backend Development**
   ```bash
   # Start with auto-reload
   python enhanced_app.py
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   npm run dev
   ```

### Testing the API

```bash
# Health check
curl http://localhost:8000/api/health

# Generate password
curl http://localhost:8000/api/generate-password?length=16

# Get supported formats
curl http://localhost:8000/api/supported-formats
```

## 📋 Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Find and kill process using port 8000
   netstat -ano | findstr :8000
   taskkill /PID <process_id> /F
   ```

2. **Module import errors**
   ```bash
   # Install missing dependencies
   pip install -r requirements.txt
   ```

3. **Database connection issues**
   - Check Supabase URL and key
   - Verify internet connection
   - Run `python setup_database.py test`

4. **Frontend build errors**
   ```bash
   # Clear cache and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

## 🔒 Security Notes

1. **Password Security**
   - Use strong passwords (minimum 12 characters)
   - Enable special characters for better security
   - Store passwords securely

2. **File Security**
   - Files are automatically cleaned up after 24 hours
   - Temporary files are stored in secure directories
   - No file content is logged in plain text

3. **Network Security**
   - API uses HTTPS in production
   - CORS configured for trusted origins
   - Input validation on all endpoints

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:

1. Check this README
2. Review the API documentation at `/docs`
3. Check the troubleshooting section
4. Create an issue on GitHub

---

**Happy Steganography!** 🎭