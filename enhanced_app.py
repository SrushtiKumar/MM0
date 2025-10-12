"""
Enhanced FastAPI Web Application for React Frontend Integration
Provides comprehensive API endpoints for the React steganography application
with Supabase integration
"""

import os
import tempfile
import uuid
import time
import secrets
import string
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import json
import shutil
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import steganography modules with fallbacks
steganography_managers = {}

try:
    from enhanced_web_video_stego import EnhancedWebVideoSteganographyManager
    steganography_managers['video'] = EnhancedWebVideoSteganographyManager
    print("✅ Video steganography module loaded")
except ImportError as e:
    print(f"❌ Video steganography module not available: {e}")
    steganography_managers['video'] = None

try:
    from enhanced_web_image_stego import EnhancedWebImageSteganographyManager
    steganography_managers['image'] = EnhancedWebImageSteganographyManager
    print("✅ Image steganography module loaded")
except ImportError as e:
    print(f"❌ Image steganography module not available: {e}")
    steganography_managers['image'] = None

try:
    from enhanced_web_document_stego import EnhancedWebDocumentSteganographyManager
    steganography_managers['document'] = EnhancedWebDocumentSteganographyManager
    print("✅ Document steganography module loaded")
except ImportError as e:
    print(f"❌ Document steganography module not available: {e}")
    steganography_managers['document'] = None

try:
    from safe_enhanced_web_audio_stego import SafeEnhancedWebAudioSteganographyManager
    steganography_managers['audio'] = SafeEnhancedWebAudioSteganographyManager
    print("✅ Safe Audio steganography module loaded")
except ImportError as e:
    print(f"❌ Safe Audio steganography module not available: {e}")
    try:
        from enhanced_web_audio_stego import EnhancedWebAudioSteganographyManager
        steganography_managers['audio'] = EnhancedWebAudioSteganographyManager
        print("✅ Fallback Audio steganography module loaded")
    except ImportError as e2:
        print(f"❌ Audio steganography module not available: {e2}")
        steganography_managers['audio'] = None

# Import Supabase service with fallback
database_available = False
try:
    from supabase_service import get_database, SteganographyDatabase
    database_available = True
    print("✅ Supabase database service loaded")
except ImportError as e:
    print(f"❌ Supabase database service not available: {e}")
    get_database = None
    SteganographyDatabase = None

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class UserModel(BaseModel):
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username")

class EmbedRequest(BaseModel):
    carrier_type: str = Field(..., description="Type of carrier file: image, video, audio, document")
    content_type: str = Field(..., description="Type of content to hide: text, file")
    text_content: Optional[str] = Field(None, description="Text content to hide")
    password: str = Field(..., description="Password for encryption")
    encryption_type: str = Field(default="aes-256-gcm", description="Encryption algorithm")
    project_name: Optional[str] = Field(None, description="Project name")
    project_description: Optional[str] = Field(None, description="Project description")

class ExtractRequest(BaseModel):
    password: str = Field(..., description="Password for decryption")
    output_format: str = Field(default="auto", description="Output format preference")

class ProjectRequest(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    project_type: str = Field(default="general", description="Project type")

class OperationResponse(BaseModel):
    success: bool
    operation_id: str
    message: str
    data: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Steganography API",
    description="Advanced steganography API with React frontend integration",
    version="2.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://localhost:8080",
        "http://localhost:8082",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8082"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
TEMP_DIR = Path("temp")

for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Global variables for job tracking
active_jobs: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_db() -> Optional[SteganographyDatabase]:
    """Get database instance if available"""
    if get_database and callable(get_database):
        try:
            return get_database()
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    return None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """Generate unique filename with timestamp and UUID"""
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    name, ext = os.path.splitext(original_filename)
    return f"{prefix}{name}_{timestamp}_{unique_id}{ext}"

def get_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def cleanup_old_files(directory: Path, max_age_hours: int = 24):
    """Clean up old files from directory"""
    try:
        current_time = time.time()
        for file_path in directory.glob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > (max_age_hours * 3600):
                    file_path.unlink()
    except Exception as e:
        print(f"Cleanup error: {e}")

def update_job_status(job_id: str, status: str, progress: int = None, 
                     message: str = None, error: str = None, result: Dict = None):
    """Update job status in memory"""
    if job_id in active_jobs:
        active_jobs[job_id].update({
            "status": status,
            "progress": progress,
            "message": message,
            "error": error,
            "result": result,
            "updated_at": datetime.now().isoformat()
        })

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/users/register", response_model=Dict[str, Any])
async def register_user(user: UserModel, db: Optional[SteganographyDatabase] = Depends(get_db)):
    """Register a new user"""
    try:
        if db:
            # Check if user already exists
            existing_user = db.get_user_by_email(user.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="User already exists")
            
            user_id = db.create_user(user.email, user.username)
            if user_id:
                return {
                    "success": True,
                    "user_id": user_id,
                    "message": "User registered successfully"
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to create user")
        else:
            return {
                "success": True,
                "user_id": str(uuid.uuid4()),
                "message": "User registered (no database)"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/operations")
async def get_user_operations(user_id: str, limit: int = 50, 
                             db: Optional[SteganographyDatabase] = Depends(get_db)):
    """Get user's operation history"""
    try:
        if db:
            operations = db.get_user_operations(user_id, limit)
            return {"success": True, "operations": operations}
        else:
            return {"success": True, "operations": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/stats")
async def get_user_stats(user_id: str, db: Optional[SteganographyDatabase] = Depends(get_db)):
    """Get user operation statistics"""
    try:
        if db:
            stats = db.get_operation_stats(user_id)
            return {"success": True, "stats": stats}
        else:
            return {"success": True, "stats": {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/projects", response_model=Dict[str, Any])
async def create_project(project: ProjectRequest):
    """Create a new steganography project"""
    try:
        project_id = str(uuid.uuid4())
        
        # Create project directory
        project_dir = OUTPUT_DIR / project_id
        project_dir.mkdir(exist_ok=True)
        
        project_data = {
            "id": project_id,
            "name": project.name,
            "description": project.description,
            "type": project.project_type,
            "created_at": datetime.now().isoformat(),
            "directory": str(project_dir)
        }
        
        return {
            "success": True,
            "project": project_data,
            "message": "Project created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STEGANOGRAPHY ENDPOINTS
# ============================================================================

@app.get("/api/supported-formats")
async def get_supported_formats():
    """Get supported file formats for each steganography type"""
    return {
        "image": {
            "carrier_formats": ["png", "jpg", "jpeg", "bmp", "tiff", "gif"],
            "content_formats": ["text", "file"],
            "max_size_mb": 0  # No limit
        },
        "video": {
            "carrier_formats": ["mp4", "avi", "mov", "mkv", "wmv", "flv"],
            "content_formats": ["text", "file"],
            "max_size_mb": 0  # No limit
        },
        "audio": {
            "carrier_formats": ["wav", "mp3", "flac", "ogg", "aac", "m4a"],
            "content_formats": ["text", "file"],
            "max_size_mb": 0  # No limit
        },
        "document": {
            "carrier_formats": ["pdf", "docx", "txt", "rtf"],
            "content_formats": ["text", "file"],
            "max_size_mb": 0  # No limit
        }
    }

@app.get("/api/generate-password")
async def generate_password(length: int = 16, include_symbols: bool = True):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    return {
        "password": password,
        "length": length,
        "strength": "strong" if length >= 12 else "medium" if length >= 8 else "weak"
    }

@app.post("/api/embed", response_model=OperationResponse)
async def embed_data(
    carrier_file: UploadFile = File(...),
    content_file: Optional[UploadFile] = File(None),
    carrier_type: Optional[str] = Form(None),
    content_type: str = Form(...),
    text_content: Optional[str] = Form(None),
    password: str = Form(...),
    encryption_type: str = Form("aes-256-gcm"),
    project_name: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Optional[SteganographyDatabase] = Depends(get_db)
):
    """Embed data into carrier file"""
    
    # Generate operation ID
    operation_id = str(uuid.uuid4())
    
    try:
        # Auto-detect carrier type if not provided
        if not carrier_type:
            file_extension = Path(carrier_file.filename).suffix.lower()
            if file_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
                carrier_type = "image"
            elif file_extension in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                carrier_type = "video"
            elif file_extension in ['.wav', '.mp3', '.flac', '.ogg', '.aac', '.m4a']:
                carrier_type = "audio"
            elif file_extension in ['.pdf', '.docx', '.txt', '.doc']:
                carrier_type = "document"
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}")
        
        print(f"[API] Detected carrier type: {carrier_type} for file: {carrier_file.filename}")
        
        # Validate inputs
        if content_type == "text" and not text_content:
            raise HTTPException(status_code=400, detail="Text content required for text embedding")
        
        if content_type == "file" and not content_file:
            raise HTTPException(status_code=400, detail="File required for file embedding")
        
        # Initialize job tracking
        active_jobs[operation_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting embedding process",
            "created_at": datetime.now().isoformat(),
            "carrier_type": carrier_type,
            "content_type": content_type
        }
        
        # Save carrier file synchronously
        carrier_filename = generate_unique_filename(carrier_file.filename, "carrier_")
        carrier_path = UPLOAD_DIR / carrier_filename
        
        with open(carrier_path, "wb") as f:
            content = await carrier_file.read()
            f.write(content)
        
        # Save content file if provided
        content_file_path = None
        if content_file:
            content_filename = generate_unique_filename(content_file.filename, "content_")
            content_file_path = UPLOAD_DIR / content_filename
            
            with open(content_file_path, "wb") as f:
                content = await content_file.read()
                f.write(content)
        
        # Log operation start in database
        if db and user_id:
            db.log_operation_start(
                user_id=user_id,
                operation_type="embed",
                media_type=carrier_type,
                original_filename=carrier_file.filename,
                password=password
            )
        
        # Start background processing with file paths instead of UploadFile objects
        background_tasks.add_task(
            process_embed_operation,
            operation_id,
            str(carrier_path),
            str(content_file_path) if content_file_path else None,
            carrier_type,
            content_type,
            text_content,
            password,
            encryption_type,
            project_name,
            user_id,
            db
        )
        
        return OperationResponse(
            success=True,
            operation_id=operation_id,
            message="Embedding operation started"
        )
        
    except Exception as e:
        if operation_id in active_jobs:
            update_job_status(operation_id, "failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract", response_model=OperationResponse)
async def extract_data(
    stego_file: UploadFile = File(...),
    password: str = Form(...),
    output_format: str = Form("auto"),
    user_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Optional[SteganographyDatabase] = Depends(get_db)
):
    """Extract hidden data from steganographic file"""
    
    operation_id = str(uuid.uuid4())
    
    try:
        # Initialize job tracking
        active_jobs[operation_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting extraction process",
            "created_at": datetime.now().isoformat(),
            "operation_type": "extract"
        }
        
        # Determine file type
        file_extension = Path(stego_file.filename).suffix.lower()
        if file_extension in ['.png', '.jpg', '.jpeg', '.bmp']:
            carrier_type = "image"
        elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
            carrier_type = "video"
        elif file_extension in ['.wav', '.mp3', '.flac']:
            carrier_type = "audio"
        elif file_extension in ['.pdf', '.docx', '.txt']:
            carrier_type = "document"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Save stego file synchronously
        stego_filename = generate_unique_filename(stego_file.filename, "stego_")
        stego_file_path = UPLOAD_DIR / stego_filename
        
        with open(stego_file_path, "wb") as f:
            content = await stego_file.read()
            f.write(content)
        
        # Log operation start in database
        if db and user_id:
            db.log_operation_start(
                user_id=user_id,
                operation_type="extract",
                media_type=carrier_type,
                original_filename=stego_file.filename,
                password=password
            )
        
        # Start background processing with file path instead of UploadFile
        background_tasks.add_task(
            process_extract_operation,
            operation_id,
            str(stego_file_path),
            carrier_type,
            password,
            output_format,
            user_id,
            db
        )
        
        return OperationResponse(
            success=True,
            operation_id=operation_id,
            message="Extraction operation started"
        )
        
    except Exception as e:
        if operation_id in active_jobs:
            update_job_status(operation_id, "failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# JOB STATUS AND DOWNLOAD ENDPOINTS
# ============================================================================

@app.get("/api/operations/{operation_id}/status", response_model=StatusResponse)
async def get_operation_status(operation_id: str):
    """Get status of a steganography operation"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    job = active_jobs[operation_id]
    return StatusResponse(
        status=job["status"],
        progress=job.get("progress"),
        message=job.get("message"),
        error=job.get("error"),
        result=job.get("result")
    )

@app.get("/api/operations/{operation_id}/download")
async def download_result(operation_id: str):
    """Download the result file of an operation"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    job = active_jobs[operation_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Operation not completed")
    
    result = job.get("result")
    if not result or not result.get("output_file"):
        raise HTTPException(status_code=404, detail="Result file not found")
    
    output_file = result["output_file"]
    if not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    filename = result.get("filename", os.path.basename(output_file))
    
    # Determine media type based on file extension
    file_ext = Path(filename).suffix.lower()
    media_type_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg', 
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.flac': 'audio/flac',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    media_type = media_type_map.get(file_ext, "application/octet-stream")
    
    return FileResponse(
        output_file,
        filename=filename,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
    )

@app.delete("/api/operations/{operation_id}")
async def delete_operation(operation_id: str):
    """Delete an operation and its files"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    job = active_jobs[operation_id]
    
    # Clean up files
    result = job.get("result", {})
    if result.get("output_file") and os.path.exists(result["output_file"]):
        os.remove(result["output_file"])
    
    # Remove from active jobs
    del active_jobs[operation_id]
    
    return {"success": True, "message": "Operation deleted"}

# ============================================================================
# BACKGROUND PROCESSING FUNCTIONS
# ============================================================================

async def process_embed_operation(
    operation_id: str,
    carrier_file_path: str,
    content_file_path: Optional[str],
    carrier_type: str,
    content_type: str,
    text_content: Optional[str],
    password: str,
    encryption_type: str,
    project_name: Optional[str],
    user_id: Optional[str],
    db: Optional[SteganographyDatabase]
):
    """Background task to process embedding operation"""
    
    start_time = time.time()
    
    try:
        update_job_status(operation_id, "processing", 30, "Preparing content")
        
        # Prepare content to hide
        if content_type == "text":
            content_to_hide = text_content
        else:
            # Read content from file
            with open(content_file_path, "rb") as f:
                content_to_hide = f.read()
        
        update_job_status(operation_id, "processing", 50, "Performing steganography")
        
        # Get appropriate steganography manager
        manager = get_steganography_manager(carrier_type, password)
        if not manager:
            raise Exception(f"No manager available for {carrier_type}")
        
        # Generate output filename
        carrier_filename = Path(carrier_file_path).name
        output_filename = generate_unique_filename(carrier_filename, "stego_")
        output_path = OUTPUT_DIR / output_filename
        
        # Perform embedding
        is_file = content_type == "file"
        original_filename = None
        if is_file and content_file_path:
            original_filename = Path(content_file_path).name
        
        if carrier_type == "video":
            # Video manager returns a dict result
            result = manager.hide_data(
                carrier_file_path,
                content_to_hide,
                str(output_path),
                is_file,
                original_filename
            )
            success = result.get("success", False)
            # Get actual output path from result if available
            actual_output_path = result.get("output_path", str(output_path))
        else:
            # Other managers (image, audio, document) return dict results too
            # Check if manager supports original_filename parameter
            import inspect
            sig = inspect.signature(manager.hide_data)
            if 'original_filename' in sig.parameters:
                result = manager.hide_data(
                    carrier_file_path,
                    content_to_hide,
                    str(output_path),
                    is_file,
                    original_filename
                )
            else:
                result = manager.hide_data(
                    carrier_file_path,
                    content_to_hide,
                    str(output_path),
                    is_file
                )
            success = result.get("success", False)
            # Get actual output path from result if available
            actual_output_path = result.get("output_path", str(output_path))
        
        if not success:
            error_msg = result.get("error", "Embedding operation failed") if isinstance(result, dict) else "Embedding operation failed"
            raise Exception(error_msg)
        
        # Use actual output path instead of expected path
        if actual_output_path != str(output_path):
            output_path = Path(actual_output_path)
            output_filename = output_path.name
        
        update_job_status(operation_id, "processing", 90, "Finalizing")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log completion in database
        if db and user_id:
            message_preview = text_content[:100] if content_type == "text" else f"File: {Path(content_file_path).name if content_file_path else 'unknown'}"
            db.log_operation_complete(
                operation_id,
                success=True,
                output_filename=output_filename,
                file_size=os.path.getsize(output_path),
                message_preview=message_preview,
                processing_time=processing_time
            )
        
        # Update job status with result
        result = {
            "output_file": str(output_path),
            "filename": output_filename,
            "file_size": os.path.getsize(output_path),
            "processing_time": processing_time,
            "carrier_type": carrier_type,
            "content_type": content_type
        }
        
        update_job_status(operation_id, "completed", 100, "Embedding completed successfully", result=result)
        
        # Cleanup input files
        os.remove(carrier_file_path)
        if content_type == "file" and content_file_path and os.path.exists(content_file_path):
            os.remove(content_file_path)
            
    except Exception as e:
        error_msg = str(e)
        update_job_status(operation_id, "failed", error=error_msg)
        
        # Log failure in database
        if db and user_id:
            db.log_operation_complete(
                operation_id,
                success=False,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )

async def process_extract_operation(
    operation_id: str,
    stego_file_path: str,
    carrier_type: str,
    password: str,
    output_format: str,
    user_id: Optional[str],
    db: Optional[SteganographyDatabase]
):
    """Background task to process extraction operation"""
    
    start_time = time.time()
    
    try:
        update_job_status(operation_id, "processing", 50, "Extracting hidden data")
        
        # Get appropriate steganography manager
        manager = get_steganography_manager(carrier_type, password)
        if not manager:
            raise Exception(f"No manager available for {carrier_type}")
        
        # Extract data
        extraction_result = manager.extract_data(stego_file_path)
        
        if extraction_result is None or (isinstance(extraction_result, tuple) and extraction_result[0] is None):
            raise Exception("Extraction failed - wrong password or no hidden data")
        
        # Handle tuple return (data, filename) from managers
        if isinstance(extraction_result, tuple):
            extracted_data, original_filename = extraction_result
        else:
            extracted_data = extraction_result
            original_filename = None
        
        update_job_status(operation_id, "processing", 80, "Saving extracted data")
        
        # Determine if this is a text message vs a file based on filename
        # Only treat as text message if explicitly returned as a text extraction
        is_text_message = (
            original_filename == "extracted_message.txt" or
            original_filename == "embedded_text.txt"
        )
        
        # Save extracted data
        if original_filename and original_filename.strip():
            # Use the original filename as provided by the steganography module
            output_filename = original_filename
            # Basic sanitization - only remove truly problematic characters
            import re
            output_filename = re.sub(r'[<>:"/\\|?*]', '_', output_filename)
            
            # Ensure we have a valid filename
            if not output_filename or output_filename.startswith('.') or len(output_filename.strip()) == 0:
                # Extract extension from original filename if possible
                original_ext = Path(original_filename).suffix if original_filename else ".bin"
                output_filename = f"extracted_file_{int(time.time())}{original_ext}"
        else:
            # Fallback to generic filename
            if isinstance(extracted_data, str):
                output_filename = f"extracted_text_{int(time.time())}.txt"
            else:
                output_filename = f"extracted_file_{int(time.time())}.bin"
        
        output_path = OUTPUT_DIR / output_filename
        
        # Save the file based on data type and whether it's a text message
        if isinstance(extracted_data, str):
            # String data - always save as text
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(extracted_data)
        elif isinstance(extracted_data, bytes):
            if is_text_message:
                # This is a text message returned as bytes - decode and save as text
                try:
                    decoded_text = extracted_data.decode('utf-8')
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(decoded_text)
                except UnicodeDecodeError:
                    # If decoding fails, save as binary anyway
                    with open(output_path, "wb") as f:
                        f.write(extracted_data)
            else:
                # This is file content - save as binary to preserve format
                with open(output_path, "wb") as f:
                    f.write(extracted_data)
        else:
            raise Exception(f"Unexpected extracted data type: {type(extracted_data)}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log completion in database
        if db and user_id:
            if isinstance(extracted_data, str):
                preview = extracted_data[:100]
            elif isinstance(extracted_data, bytes):
                preview = f"Binary file ({len(extracted_data)} bytes)"
            else:
                preview = f"Unknown data type: {type(extracted_data)}"
            
            db.log_operation_complete(
                operation_id,
                success=True,
                output_filename=output_filename,
                file_size=os.path.getsize(output_path),
                message_preview=preview,
                processing_time=processing_time
            )
        
        # Update job status with result
        result = {
            "output_file": str(output_path),
            "filename": output_filename,
            "file_size": os.path.getsize(output_path),
            "processing_time": processing_time,
            "data_type": "text" if isinstance(extracted_data, str) else "binary",
            "preview": extracted_data[:200] if isinstance(extracted_data, str) else (
                extracted_data.decode('utf-8', errors='ignore')[:200] 
                if isinstance(extracted_data, bytes) and len(extracted_data) < 1000 
                else None
            ),
            "original_filename": original_filename
        }
        
        update_job_status(operation_id, "completed", 100, "Extraction completed successfully", result=result)
        
        # Cleanup input file
        os.remove(stego_file_path)
        
    except Exception as e:
        error_msg = str(e)
        update_job_status(operation_id, "failed", error=error_msg)
        
        # Log failure in database
        if db and user_id:
            db.log_operation_complete(
                operation_id,
                success=False,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )

def get_steganography_manager(carrier_type: str, password: str = ""):
    """Get appropriate steganography manager based on carrier type"""
    manager_class = steganography_managers.get(carrier_type)
    if manager_class:
        # Try to create with password parameter
        try:
            return manager_class(password=password)
        except TypeError:
            # Fallback for managers that don't take password in constructor
            return manager_class()
    return None

# ============================================================================
# HEALTH AND STATUS ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check(db: Optional[SteganographyDatabase] = Depends(get_db)):
    """Health check endpoint"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "active_jobs": len(active_jobs),
        "available_managers": {
            "image": steganography_managers['image'] is not None,
            "video": steganography_managers['video'] is not None,
            "audio": steganography_managers['audio'] is not None,
            "document": steganography_managers['document'] is not None
        },
        "database_available": database_available
    }
    
    if db:
        db_health = db.health_check()
        health_data["database"] = db_health
    else:
        health_data["database"] = {"status": "not_configured"}
    
    return health_data

@app.get("/api/status")
async def simple_status():
    """Simple status endpoint without database dependencies"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/api/operations")
async def list_operations(limit: int = 100):
    """List recent operations"""
    operations = []
    for op_id, job in list(active_jobs.items())[-limit:]:
        operations.append({
            "operation_id": op_id,
            "status": job["status"],
            "progress": job.get("progress"),
            "created_at": job["created_at"],
            "carrier_type": job.get("carrier_type"),
            "content_type": job.get("content_type"),
            "operation_type": job.get("operation_type", "embed")
        })
    
    return {"operations": operations}

# ============================================================================
# CLEANUP AND MAINTENANCE
# ============================================================================

# @app.on_event("startup")
# async def startup_event():
#     """Application startup tasks"""
#     print("🚀 Enhanced Steganography API starting up...")
    
#     # Clean up old files
#     cleanup_old_files(UPLOAD_DIR, 2)  # 2 hours for uploads
#     cleanup_old_files(OUTPUT_DIR, 24)  # 24 hours for outputs
    
#     print("✅ Startup complete!")

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Application shutdown tasks"""
#     print("🛑 Enhanced Steganography API shutting down...")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "enhanced_app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )