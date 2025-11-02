#!/usr/bin/env python3
"""
Simple test server to verify steganography functionality
"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn
from pathlib import Path
import os

app = FastAPI()

# Test import managers
print("Testing manager imports...")
try:
    from final_video_steganography import FinalVideoSteganographyManager
    print("✅ Video steganography - OK")
except ImportError as e:
    print(f"❌ Video steganography - FAILED: {e}")

try:
    from universal_file_steganography import UniversalFileSteganography
    print("✅ Image/Document steganography - OK")
except ImportError as e:
    print(f"❌ Image/Document steganography - FAILED: {e}")

try:
    from universal_file_audio import UniversalFileAudio
    print("✅ Audio steganography - OK")
except ImportError as e:
    print(f"❌ Audio steganography - FAILED: {e}")

@app.get("/")
async def root():
    return {"message": "Test steganography server is running"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "message": "All systems operational"}

@app.post("/api/test-embed")
async def test_embed(
    carrier_file: UploadFile = File(...),
    content_type: str = Form(...),
    text_content: str = Form(None),
    password: str = Form(...)
):
    """Simple test endpoint for embedding"""
    
    # Just validate the request format
    file_extension = Path(carrier_file.filename).suffix.lower()
    
    if file_extension in ['.mp4', '.avi', '.mov']:
        media_type = "video"
    elif file_extension in ['.wav', '.mp3']:
        media_type = "audio"
    elif file_extension in ['.png', '.jpg', '.jpeg']:
        media_type = "image"
    else:
        media_type = "document"
    
    return {
        "success": True,
        "message": f"Test embed request received for {media_type}",
        "filename": carrier_file.filename,
        "content_type": content_type,
        "has_text": bool(text_content),
        "media_type": media_type
    }

if __name__ == "__main__":
    print("🚀 Starting test steganography server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)