#!/usr/bin/env python3
"""
Fixed Backend with Better Error Handling
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

app = FastAPI(title="Steganography Service", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
active_jobs = {}

# Import steganography modules
try:
    from enhanced_web_video_stego import EnhancedWebVideoSteganography
    print("✅ Video steganography module loaded")
    video_stego = EnhancedWebVideoSteganography()
except Exception as e:
    print(f"❌ Video steganography module failed: {e}")
    video_stego = None

def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """Generate unique filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = Path(original_filename).stem
    ext = Path(original_filename).suffix
    return f"{prefix}{name}_{timestamp}{ext}"

@app.get("/")
async def root():
    return {"message": "Steganography Service Running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "modules": {
            "video": video_stego is not None
        }
    }

@app.post("/api/extract")
async def extract_data(
    stego_file: UploadFile = File(...),
    password: str = Form(...),
    output_format: str = Form("auto")
):
    """Extract hidden data from steganographic file"""
    
    operation_id = str(uuid.uuid4())
    
    try:
        print(f"🔍 Starting extraction for operation: {operation_id}")
        
        # Initialize job tracking
        active_jobs[operation_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting extraction process",
            "created_at": datetime.now().isoformat(),
            "operation_type": "extract"
        }
        
        # Check file type
        file_extension = Path(stego_file.filename).suffix.lower()
        print(f"📁 File extension: {file_extension}")
        
        if file_extension not in ['.mp4', '.avi', '.mov', '.mkv']:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}")
        
        if not video_stego:
            raise HTTPException(status_code=500, detail="Video steganography module not available")
        
        # Save uploaded file
        stego_filename = generate_unique_filename(stego_file.filename, "stego_")
        stego_file_path = UPLOAD_DIR / stego_filename
        
        print(f"💾 Saving file to: {stego_file_path}")
        
        # Read and save file content
        content = await stego_file.read()
        with open(stego_file_path, "wb") as f:
            f.write(content)
        
        print(f"✅ File saved: {len(content)} bytes")
        
        # Update progress
        active_jobs[operation_id]["progress"] = 25
        active_jobs[operation_id]["message"] = "File uploaded, starting extraction"
        
        # Extract data
        print(f"🔓 Starting extraction with password")
        result = video_stego.extract_data_from_video(str(stego_file_path), password)
        
        if not result.get('success', False):
            error_msg = result.get('message', 'Extraction failed')
            print(f"❌ Extraction failed: {error_msg}")
            active_jobs[operation_id]["status"] = "failed"
            active_jobs[operation_id]["message"] = error_msg
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Update progress
        active_jobs[operation_id]["progress"] = 75
        active_jobs[operation_id]["message"] = "Data extracted, preparing output"
        
        # Get extracted data
        extracted_data = result['data']
        filename = result.get('filename', 'extracted_file')
        
        print(f"📊 Extracted data: {type(extracted_data)}, size: {len(extracted_data) if hasattr(extracted_data, '__len__') else 'unknown'}")
        print(f"📁 Original filename: {filename}")
        
        # Determine output filename
        if isinstance(extracted_data, bytes) and extracted_data.startswith(b'ID3'):
            # It's an MP3 file
            if not filename.endswith('.mp3'):
                filename = f"{filename}.mp3" if filename else "extracted_audio.mp3"
        
        # Save extracted file
        output_filename = generate_unique_filename(filename, "extracted_")
        output_file_path = UPLOAD_DIR / output_filename
        
        with open(output_file_path, 'wb') as f:
            if isinstance(extracted_data, bytes):
                f.write(extracted_data)
            else:
                f.write(str(extracted_data).encode())
        
        file_size = os.path.getsize(output_file_path)
        print(f"💾 Saved extracted file: {output_file_path} ({file_size} bytes)")
        
        # Update job completion
        active_jobs[operation_id]["status"] = "completed"
        active_jobs[operation_id]["progress"] = 100
        active_jobs[operation_id]["message"] = "Extraction completed successfully"
        active_jobs[operation_id]["output_file"] = str(output_file_path)
        active_jobs[operation_id]["output_filename"] = filename
        active_jobs[operation_id]["file_size"] = file_size
        
        # Clean up input file
        try:
            os.remove(stego_file_path)
        except:
            pass
        
        return {
            "success": True,
            "operation_id": operation_id,
            "message": "Extraction completed successfully",
            "filename": filename,
            "file_size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error in extraction: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        
        active_jobs[operation_id]["status"] = "failed"
        active_jobs[operation_id]["message"] = f"Internal error: {str(e)}"
        
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/operations/{operation_id}/status")
async def get_operation_status(operation_id: str):
    """Get operation status"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    return active_jobs[operation_id]

@app.get("/api/operations/{operation_id}/download")
async def download_result(operation_id: str):
    """Download extraction result"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    job = active_jobs[operation_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Operation not completed")
    
    output_file = job.get("output_file")
    if not output_file or not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    filename = job.get("output_filename", "extracted_file")
    
    return FileResponse(
        path=output_file,
        filename=filename,
        media_type='application/octet-stream'
    )

if __name__ == "__main__":
    print("🚀 Starting Fixed Steganography Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")