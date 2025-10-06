"""
FastAPI Web Application for Steganography Operations
Provides a web interface for the advanced steganography functions.
"""

import os
import tempfile
import uuid
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import shutil

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Import our steganography modules
from stego_cli import SteganographyManager, ContainerAnalyzer
from stego_cli_enhanced import SteganographyManagerEnhanced
from simple_stego import SimpleSteganographyManager
from simple_audio_stego import SimpleAudioSteganographyManager
from working_audio_stego import WorkingAudioSteganographyManager
from final_audio_stego import FinalAudioSteganographyManager
from final_video_steganography import FinalVideoSteganographyManager
from fast_video_stego import FastVideoSteganographyManager
from robust_video_stego import RobustVideoSteganographyManager

# Configuration
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
TEMP_DIR = Path("temp")

# Create directories if they don't exist
for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Initialize FastAPI
app = FastAPI(
    title="VeilForge - Advanced Steganography Web Interface",
    description="Hide and extract data in images, audio, video, and documents",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic models for API
class HideRequest(BaseModel):
    password: str
    data: Optional[str] = None
    is_enhanced: bool = False

class ExtractRequest(BaseModel):
    password: str
    is_enhanced: bool = False

class AnalyzeRequest(BaseModel):
    pass

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    message: str
    result: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None
    error: Optional[str] = None

# In-memory job storage (in production, use Redis or database)
jobs: Dict[str, JobStatus] = {}

def cleanup_old_files():
    """Clean up old temporary files"""
    try:
        for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
            for file_path in directory.glob("*"):
                if file_path.is_file():
                    # Remove files older than 1 hour
                    if (file_path.stat().st_mtime < (time.time() - 3600)):
                        file_path.unlink()
    except Exception as e:
        print(f"Cleanup error: {e}")

@app.get("/")
async def index(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "image": ["png", "jpg", "jpeg", "bmp"],
        "audio": ["wav", "mp3", "flac"],
        "video": ["mp4", "avi", "mov", "mkv"],
        "document": ["pdf", "docx", "xml"],
        "text": ["txt", "py", "js", "html", "css", "json"]
    }

@app.post("/api/analyze")
async def analyze_container(
    file: UploadFile = File(...),
    request_data: str = Form(...)
):
    """Analyze container file capacity"""
    try:
        request_obj = AnalyzeRequest.parse_raw(request_data)
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Analyze capacity using enhanced manager
        manager = SteganographyManagerEnhanced("dummy_password")
        analysis_result = manager.analyze_capacity(str(file_path))
        
        # Clean up
        file_path.unlink()
        
        return {
            "success": True,
            "filename": file.filename,
            "file_size": len(content),
            "container_type": analysis_result.get("container_type", "unknown"),
            "estimated_capacity": analysis_result.get("estimated_capacity", 0),
            "safe_capacity": analysis_result.get("safe_capacity", 0),
            "recommendations": analysis_result.get("recommendations", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")

@app.post("/api/hide")
async def hide_data(
    background_tasks: BackgroundTasks,
    container_file: UploadFile = File(...),
    secret_file: Optional[UploadFile] = File(None),
    request_data: str = Form(...)
):
    """Hide data or file in container"""
    try:
        request_obj = HideRequest.parse_raw(request_data)
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status="pending",
            message="Job queued for processing"
        )
        
        # Read file contents before starting background task
        print(f"[DEBUG] Reading container file: {container_file.filename}")
        container_content = await container_file.read()
        print(f"[DEBUG] Container content size: {len(container_content)} bytes")
        
        secret_content = None
        if secret_file:
            print(f"[DEBUG] Reading secret file: {secret_file.filename}")
            secret_content = await secret_file.read()
            print(f"[DEBUG] Secret content size: {len(secret_content)} bytes")
        
        # Start background task with file contents
        background_tasks.add_task(
            process_hide_job,
            job_id,
            container_file.filename,
            container_content,
            secret_file.filename if secret_file else None,
            secret_content,
            request_obj
        )
        
        return {"job_id": job_id, "status": "pending"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Hide operation failed: {str(e)}")

@app.post("/api/extract")
async def extract_data(
    background_tasks: BackgroundTasks,
    container_file: UploadFile = File(...),
    request_data: str = Form(...)
):
    """Extract data from container file"""
    try:
        request_obj = ExtractRequest.parse_raw(request_data)
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status="pending",
            message="Job queued for processing"
        )
        
        # Read file content before starting background task
        print(f"[DEBUG] Reading container file for extraction: {container_file.filename}")
        container_content = await container_file.read()
        print(f"[DEBUG] Container content size: {len(container_content)} bytes")
        
        # Start background task with file content
        background_tasks.add_task(
            process_extract_job,
            job_id,
            container_file.filename,
            container_content,
            request_obj
        )
        
        return {"job_id": job_id, "status": "pending"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Extract operation failed: {str(e)}")

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and result"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/api/download/{job_id}")
async def download_result(job_id: str):
    """Download the result file"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job.status != "completed" or not job.download_url:
        raise HTTPException(status_code=400, detail="No file available for download")
    
    # Handle both absolute and relative paths
    file_path = Path(job.download_url)
    print(f"[DEBUG] Download requested for job {job_id}, download_url: {job.download_url}")
    
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    
    print(f"[DEBUG] Trying absolute path: {file_path}")
    if not file_path.exists():
        # Try without the full path, just the filename in outputs
        filename = file_path.name
        file_path = OUTPUT_DIR / filename
        print(f"[DEBUG] Trying outputs directory: {file_path}")
        
    if not file_path.exists():
        print(f"[DEBUG] File not found in either location")
        print(f"[DEBUG] Checked paths:")
        print(f"  1. {Path(job.download_url)}")
        print(f"  2. {Path.cwd() / job.download_url}")
        print(f"  3. {OUTPUT_DIR / Path(job.download_url).name}")
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    print(f"[DEBUG] File found at: {file_path}")
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type='application/octet-stream'
    )

async def process_hide_job(
    job_id: str,
    container_filename: str,
    container_content: bytes,
    secret_filename: Optional[str],
    secret_content: Optional[bytes],
    request_obj: HideRequest
):
    """Background task to process hide operation"""
    try:
        jobs[job_id].status = "processing"
        jobs[job_id].message = "Processing hide operation..."
        
        # Save container file
        container_path = UPLOAD_DIR / f"{job_id}_container_{container_filename}"
        print(f"[DEBUG] Saving container to: {container_path}")
        print(f"[DEBUG] Container content size: {len(container_content)} bytes")
        with open(container_path, "wb") as buffer:
            buffer.write(container_content)
        print(f"[DEBUG] Container file saved successfully")
        
        # Determine payload
        if secret_content is not None:
            # Hide file
            secret_path = UPLOAD_DIR / f"{job_id}_secret_{secret_filename}"
            print(f"[DEBUG] Saving secret file to: {secret_path}")
            print(f"[DEBUG] Secret content size: {len(secret_content)} bytes")
            with open(secret_path, "wb") as buffer:
                buffer.write(secret_content)
            print(f"[DEBUG] Secret file saved successfully")
            payload = str(secret_path)
            is_file = True
        else:
            # Hide text data
            payload = request_obj.data
            is_file = False
        
        # Output path
        output_path = OUTPUT_DIR / f"{job_id}_output_{container_filename}"
        
        # Simple file type detection from filename for reliability
        file_ext = container_filename.lower().split('.')[-1] if '.' in container_filename else ''
        
        # Use simple steganography for images to ensure reliability
        if file_ext in ['png', 'jpg', 'jpeg', 'bmp', 'webp', 'tiff']:
            # Use simple, reliable steganography for images
            print(f"[DEBUG] Using simple steganography for image file: {file_ext}")
            print(f"[DEBUG] Container path: {container_path}")
            print(f"[DEBUG] Payload: {payload}")
            print(f"[DEBUG] Output path: {output_path}")
            print(f"[DEBUG] Is file: {is_file}")
            
            try:
                manager = SimpleSteganographyManager(request_obj.password)
                print(f"[DEBUG] Created SimpleSteganographyManager")
                
                result_dict = manager.hide_data(str(container_path), payload, str(output_path), is_file)
                print(f"[DEBUG] Hide operation completed: {result_dict}")
            except Exception as e:
                print(f"[ERROR] SimpleSteganographyManager failed: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                raise
            
            # Ensure output is PNG for data preservation
            actual_output = result_dict.get('output_path', str(output_path))
            if actual_output != str(output_path):
                # Update output path if it was changed (e.g., converted to PNG)
                import shutil
                final_output = OUTPUT_DIR / f"{job_id}_output.png"
                shutil.move(actual_output, final_output)
                output_path = final_output
                
        elif file_ext in ['wav', 'mp3', 'flac', 'ogg', 'm4a', 'aac']:
            # Use the new Final Audio Steganography that supports multiple formats!
            print(f"[DEBUG] Using Final Audio Steganography for: {file_ext}")
            
            try:
                # Use the final working audio steganography
                audio_manager = FinalAudioSteganographyManager(request_obj.password)
                
                # Pass the original filename when embedding files to preserve extension
                original_filename = None
                if is_file and isinstance(payload, str) and os.path.isfile(payload):
                    original_filename = os.path.basename(payload)
                    print(f"[DEBUG] Preserving original filename for file embedding: {original_filename}")
                
                # Perform steganography directly (handles all audio formats and preserves format)
                result_dict = audio_manager.hide_data(str(container_path), payload, str(output_path), is_file)
                print(f"[DEBUG] Final audio hide operation completed: {result_dict}")
                
                # Use the actual output path returned by the steganography function
                actual_output = result_dict.get('output_path', str(output_path))
                
                # Update output path to match what was actually created
                if actual_output != str(output_path):
                    print(f"[DEBUG] Output path updated from {output_path} to {actual_output}")
                    # Determine the final output name based on the actual output
                    actual_ext = os.path.splitext(actual_output)[1]
                    final_output = OUTPUT_DIR / f"{job_id}_output{actual_ext}"
                    
                    if actual_output != str(final_output):
                        import shutil
                        if os.path.exists(actual_output):
                            shutil.move(actual_output, str(final_output))
                            print(f"[DEBUG] Moved output from {actual_output} to: {final_output}")
                        else:
                            print(f"[WARNING] Expected output file not found: {actual_output}")
                    output_path = final_output
                else:
                    output_path = Path(actual_output)
                
            except Exception as e:
                error_msg = f"Audio steganography failed: {str(e)}. The audio file may be too short or incompatible. Please try with a longer audio file for best results."
                print(f"[ERROR] {error_msg}")
                jobs[job_id].status = "failed"
                jobs[job_id].message = error_msg
                jobs[job_id].error = str(e)
                return
                
        elif file_ext in ['mp4', 'avi', 'mov', 'mkv', 'webm', 'wmv', 'flv']:
            # Use Robust Video Steganography for reliable performance
            print(f"[DEBUG] Using Robust Video Steganography for: {file_ext}")
            
            # For file hiding (especially images), prefer AVI format for lossless compression
            if is_file and file_ext != 'avi':
                base_name = output_path.stem
                output_path = output_path.parent / f"{base_name}.avi"
                print(f"[DEBUG] Using AVI format for better lossless compression: {output_path}")
            
            try:
                video_manager = RobustVideoSteganographyManager(request_obj.password)
                
                # Pass the original filename when embedding files to preserve extension
                original_filename = None
                if is_file and isinstance(payload, str) and os.path.isfile(payload):
                    original_filename = os.path.basename(payload)
                    print(f"[DEBUG] Preserving original filename for file embedding: {original_filename}")
                
                # Perform robust video steganography
                result_dict = video_manager.hide_data(str(container_path), payload, str(output_path), is_file)
                print(f"[DEBUG] Robust video hide operation completed: {result_dict}")
                
                # The robust video steganography creates the file directly at the specified path
                actual_output = result_dict.get('output_path', str(output_path))
                
                # Verify the file was created where expected
                if os.path.exists(actual_output):
                    output_path = Path(actual_output)
                    print(f"[DEBUG] Robust video output verified at: {output_path}")
                else:
                    print(f"[ERROR] Robust video output not found at: {actual_output}")
                    raise Exception(f"Output file not created: {actual_output}")
                
            except Exception as e:
                error_msg = f"Video steganography failed: {str(e)}. The video file may be too short or the data too large. Try with a longer video or smaller file."
                print(f"[ERROR] {error_msg}")
                jobs[job_id].status = "failed"
                jobs[job_id].message = error_msg
                jobs[job_id].error = str(e)
                return
                
        else:
            # For non-image, non-audio files, use basic steganography to avoid file handling issues
            print(f"[DEBUG] Using basic steganography for non-image, non-audio file: {file_ext}")
            try:
                manager = SteganographyManager(request_obj.password)
                print(f"[DEBUG] Created SteganographyManager")
                
                result_dict = manager.hide_data(str(container_path), payload, str(output_path), is_file)
                print(f"[DEBUG] Basic hide operation completed: {result_dict}")
            except Exception as e:
                print(f"[ERROR] SteganographyManager failed: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                raise
        
        jobs[job_id].status = "completed"
        jobs[job_id].message = "Hide operation completed successfully"
        jobs[job_id].result = result_dict
        jobs[job_id].download_url = output_path.name  # Store just the filename
        
        # Clean up input files
        container_path.unlink()
        if secret_content is not None and secret_path.exists():
            secret_path.unlink()
            
    except Exception as e:
        print(f"[ERROR] Exception in process_hide_job: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        jobs[job_id].status = "failed"
        jobs[job_id].message = f"Hide operation failed: {str(e)}"

async def process_extract_job(
    job_id: str,
    container_filename: str,
    container_content: bytes,
    request_obj: ExtractRequest
):
    """Background task to process extract operation"""
    try:
        jobs[job_id].status = "processing"
        jobs[job_id].message = "Processing extract operation..."
        
        # Save container file
        container_path = UPLOAD_DIR / f"{job_id}_extract_{container_filename}"
        print(f"[DEBUG] Saving container for extraction to: {container_path}")
        with open(container_path, "wb") as buffer:
            buffer.write(container_content)
        print(f"[DEBUG] Container file saved for extraction")
        
        # Simple file type detection from filename for reliability
        file_ext = container_filename.lower().split('.')[-1] if '.' in container_filename else ''
        
        # Use simple steganography for images to ensure reliability
        if file_ext in ['png', 'jpg', 'jpeg', 'bmp', 'webp', 'tiff']:
            # Use simple, reliable steganography for images
            manager = SimpleSteganographyManager(request_obj.password)
            extracted_data, filename = manager.extract_data(str(container_path))
            result_dict = {
                "success": True,
                "data_size": len(extracted_data),
                "filename": filename,
                "method": "Simple LSB"
            }
            
        elif file_ext in ['wav', 'mp3', 'flac', 'ogg', 'm4a', 'aac']:
            # Use the new Final Audio Steganography for extraction
            print(f"[DEBUG] Using Final Audio Steganography extraction for: {file_ext}")
            
            try:
                # Use the final working audio steganography
                audio_manager = FinalAudioSteganographyManager(request_obj.password)
                extracted_data, filename = audio_manager.extract_data(str(container_path))
                result_dict = {
                    "success": True,
                    "data_size": len(extracted_data),
                    "filename": filename,
                    "method": "Final PCM Audio Steganography"
                }
                print(f"[DEBUG] Final audio extraction completed: {result_dict}")
            except Exception as e:
                error_msg = f"Audio extraction failed: {str(e)}. Please ensure the audio file contains hidden data created with this system."
                print(f"[ERROR] {error_msg}")
                jobs[job_id].status = "failed"
                jobs[job_id].message = error_msg
                jobs[job_id].error = str(e)
                return
                # Don't raise, just mark as failed and return
        
        elif file_ext in ['mp4', 'avi', 'mov', 'mkv', 'webm', 'wmv', 'flv']:
            # Use Robust Video Steganography for extraction
            print(f"[DEBUG] Using Robust Video Steganography extraction for: {file_ext}")
            
            try:
                video_manager = RobustVideoSteganographyManager(request_obj.password)
                extracted_data, filename = video_manager.extract_data(str(container_path))
                
                if extracted_data and filename:
                    result_dict = {
                        "success": True,
                        "data_size": len(extracted_data),
                        "filename": filename,
                        "method": "Robust Video Steganography"
                    }
                    print(f"[DEBUG] Robust video extraction completed: {result_dict}")
                else:
                    # No data found
                    error_msg = "No hidden data found in video. The video may not contain steganographic data, may have been compressed, or was created with a different system."
                    print(f"[ERROR] {error_msg}")
                    jobs[job_id].status = "failed"
                    jobs[job_id].message = error_msg
                    jobs[job_id].error = "No data found"
                    return
                    
            except Exception as e:
                error_msg = f"Video extraction failed: {str(e)}. Please ensure the video file contains hidden data created with this system."
                print(f"[ERROR] {error_msg}")
                jobs[job_id].status = "failed"
                jobs[job_id].message = error_msg
                jobs[job_id].error = str(e)
                return
        
        elif request_obj.is_enhanced:
            # Use enhanced manager for non-images, non-audio
            manager = SteganographyManagerEnhanced(request_obj.password)
            try:
                result = manager.extract_data_robust(str(container_path))
                extracted_data = result.data
                filename = result.filename
                result_dict = {
                    "success": result.success,
                    "data_size": len(extracted_data) if extracted_data else 0,
                    "filename": filename,
                    "verification_passed": result.verification_passed,
                    "error_correction_applied": result.error_correction_applied
                }
            except ValueError as e:
                if "empty range" in str(e):
                    # Fallback to regular manager for small images
                    manager = SteganographyManager(request_obj.password)
                    extracted_data, filename = manager.extract_data(str(container_path))
                    result_dict = {
                        "success": True,
                        "data_size": len(extracted_data),
                        "filename": filename
                    }
                else:
                    raise e
        else:
            manager = SteganographyManager(request_obj.password)
            extracted_data, filename = manager.extract_data(str(container_path))
            result_dict = {
                "success": True,
                "data_size": len(extracted_data),
                "filename": filename
            }
        
        # Save extracted data with proper filename and extension
        if filename and filename != "embedded_text.txt":
            # Use the original filename with extension
            output_path = OUTPUT_DIR / f"{job_id}_extracted_{filename}"
        else:
            # Default to .txt for text data
            output_path = OUTPUT_DIR / f"{job_id}_extracted_data.txt"
        
        with open(output_path, "wb") as f:
            f.write(extracted_data)
        
        jobs[job_id].status = "completed"
        jobs[job_id].message = "Extract operation completed successfully"
        jobs[job_id].result = result_dict
        jobs[job_id].download_url = output_path.name  # Store just the filename
        
        # Clean up input file
        container_path.unlink()
        
    except Exception as e:
        jobs[job_id].status = "failed"
        jobs[job_id].message = f"Extract operation failed: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    import time
    
    # Cleanup old files on startup
    cleanup_old_files()
    
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)