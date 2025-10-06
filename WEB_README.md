# VeilForge Web Application

A modern web interface for the VeilForge steganography suite, built with FastAPI and Bootstrap.

## Features

- **Hide Data**: Embed text messages or files in images, audio, video, and documents
- **Extract Data**: Retrieve hidden data from container files  
- **Analyze Capacity**: Determine how much data can be hidden in a container file
- **Multiple Formats**: Support for PNG, JPEG, WAV, MP4, PDF, DOCX, and more
- **Enhanced Security**: Military-grade AES encryption with error correction
- **Modern UI**: Responsive web interface with drag-and-drop file upload
- **Background Processing**: Non-blocking operations with real-time status updates

## Quick Start

### Windows
1. Double-click `start_web.bat` to automatically set up and run the application
2. Open your browser to `http://localhost:8000`

### Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir uploads outputs temp

# Start the web server
python app.py
```

## Usage

### Hide Data
1. Go to the "Hide Data" tab
2. Upload a container file (image, audio, video, or document)
3. Choose to hide either:
   - Text message: Enter your secret text
   - File: Upload any file to hide
4. Enter a strong password for encryption
5. Optionally enable Enhanced Security Mode for maximum protection
6. Click "Hide Data" and wait for processing
7. Download the result file containing your hidden data

### Extract Data
1. Go to the "Extract Data" tab
2. Upload a file containing hidden data
3. Enter the same password used for hiding
4. Enable Enhanced Security Mode if it was used during hiding
5. Click "Extract Data" and wait for processing
6. Download the extracted data/file

### Analyze Capacity
1. Go to the "Analyze Capacity" tab
2. Upload a file you want to use as a container
3. Click "Analyze Capacity"
4. View the maximum and safe hiding capacity
5. Get recommendations for optimal steganography

## API Endpoints

The web application provides a REST API for programmatic access:

- `POST /api/hide` - Hide data in container file
- `POST /api/extract` - Extract data from container file
- `POST /api/analyze` - Analyze container capacity
- `GET /api/job/{job_id}` - Get job status
- `GET /api/download/{job_id}` - Download result file
- `GET /api/supported-formats` - Get supported file formats

## Security Features

- **AES-256 Encryption**: Military-grade encryption for all hidden data
- **PBKDF2 Key Derivation**: 100,000 iterations with unique salts
- **Error Correction**: Reed-Solomon codes protect against data corruption
- **Enhanced Mode**: Additional security layers and redundancy
- **Anti-Detection**: Advanced techniques resist statistical analysis
- **Compression Resistance**: Survives format conversion and compression

## Supported Formats

### Images
- PNG, JPEG, BMP
- Uses DWT (Discrete Wavelet Transform) for secure embedding

### Audio  
- WAV, MP3, FLAC
- Hybrid DWT+DCT with frequency hopping

### Video
- MP4, AVI, MOV, MKV
- Multi-frame embedding with keyframe detection

### Documents
- PDF (metadata embedding)
- DOCX (XML structure modification)
- XML (custom object insertion)

### Text Files
- TXT, source code files
- Whitespace steganography for text files
- LSB steganography for binary files

## Technical Details

### Architecture
- **Backend**: FastAPI (Python)
- **Frontend**: Bootstrap 5 + vanilla JavaScript
- **Processing**: Background tasks with job queue
- **Storage**: Local filesystem (uploads/outputs/temp directories)

### Performance
- Asynchronous processing prevents UI blocking
- Background job system handles large files
- Automatic cleanup of temporary files
- Real-time status updates via polling

### Security Considerations
- Files are stored temporarily and cleaned up automatically
- All operations use strong encryption
- No data is logged or persisted beyond job completion
- Password verification prevents unauthorized access

## Troubleshooting

### Common Issues

**"Module not found" errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**"Permission denied" when creating directories**
- Run terminal/command prompt as administrator
- Check file system permissions

**Web interface not loading**
- Check if port 8000 is available
- Try accessing `http://127.0.0.1:8000` instead
- Check firewall settings

**Large file processing fails**
- Increase system memory if possible
- Try smaller files or enable Enhanced Mode for better error correction
- Check available disk space in temp directories

### Performance Tips
- Use Enhanced Security Mode for critical data
- Analyze capacity before hiding large files
- Use appropriate container types for your data size
- Keep container files larger than hidden data for better concealment

## Development

To extend the web application:

1. **Add new endpoints**: Modify `app.py`
2. **Update UI**: Edit `templates/index.html`
3. **Add new steganography methods**: Extend the CLI modules
4. **Customize styling**: Modify CSS in the template

## License

This web interface is part of the VeilForge steganography suite.