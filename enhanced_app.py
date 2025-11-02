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
import zipfile
import base64
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

# Video Steganography - Try existing modules
try:
    from final_video_steganography import FinalVideoSteganographyManager
    steganography_managers['video'] = FinalVideoSteganographyManager
    print("[OK] Final Video steganography module loaded")
except ImportError:
    try:
        from video_steganography import VideoSteganographyManager
        steganography_managers['video'] = VideoSteganographyManager
        print("[OK] Video steganography module loaded")
    except ImportError as e:
        print(f"[ERROR] Video steganography module not available: {e}")
        steganography_managers['video'] = None

# Image Steganography - Use universal file steganography
try:
    from universal_file_steganography import UniversalFileSteganography
    steganography_managers['image'] = UniversalFileSteganography
    print("[OK] Universal file steganography module loaded for images")
except ImportError as e:
    print(f"[ERROR] Image steganography module not available: {e}")
    steganography_managers['image'] = None

# Document Steganography - Use universal file steganography  
try:
    from universal_file_steganography import UniversalFileSteganography
    steganography_managers['document'] = UniversalFileSteganography
    print("[OK] Universal file steganography module loaded for documents")
except ImportError as e:
    print(f"[ERROR] Document steganography module not available: {e}")
    steganography_managers['document'] = None

# Audio Steganography - Use working module
try:
    from universal_file_audio import UniversalFileAudio
    steganography_managers['audio'] = UniversalFileAudio
    print("[OK] Universal file audio steganography module loaded")
except ImportError as e:
    print(f"[ERROR] Audio steganography module not available: {e}")
    steganography_managers['audio'] = None

# Import Supabase service with fallback
database_available = False
try:
    from supabase_service import get_database, SteganographyDatabase
    database_available = True
    print("[OK] Supabase database service loaded")
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
    output_filename: Optional[str] = None
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

def detect_file_format_from_binary(binary_content):
    """Detect file format from binary content and return appropriate extension"""
    if not binary_content or not isinstance(binary_content, bytes):
        return None
    
    # Check various file signatures
    if binary_content.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    elif binary_content.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    elif binary_content.startswith(b'GIF87a') or binary_content.startswith(b'GIF89a'):
        return '.gif'
    elif binary_content.startswith(b'BM'):
        return '.bmp'
    elif binary_content.startswith(b'RIFF') and len(binary_content) > 12 and b'WEBP' in binary_content[8:12]:
        return '.webp'
    elif binary_content.startswith(b'RIFF') and len(binary_content) > 12 and b'WAVE' in binary_content[8:12]:
        return '.wav'
    elif binary_content.startswith(b'ID3') or binary_content[0:2] in [b'\xff\xfb', b'\xff\xf3', b'\xff\xf2']:
        return '.mp3'
    elif binary_content.startswith(b'%PDF'):
        return '.pdf'
    elif binary_content.startswith(b'PK\x03\x04'):
        # ZIP-based formats
        if b'word/' in binary_content[:1000]:
            return '.docx'
        elif b'xl/' in binary_content[:1000]:
            return '.xlsx'
        else:
            return '.zip'
    
    # If no format detected, return None to keep original filename
    return None

def create_layered_data_container(layers_info):
    """Create a container that holds multiple data layers with proper format preservation
    
    Args:
        layers_info: List of tuples (data, filename, is_binary) or just data items
    
    Returns:
        JSON string containing the layered container
    """
    import json
    import base64
    import mimetypes
    
    container = {
        "version": "1.0",
        "type": "layered_container", 
        "created_at": datetime.now().isoformat(),
        "layers": []
    }
    
    for i, layer_item in enumerate(layers_info):
        # Defensive check for None or invalid layer items
        if layer_item is None:
            print(f"Warning: None layer item at index {i}, skipping")
            continue
            
        # Handle different input formats
        if isinstance(layer_item, tuple) and len(layer_item) >= 2:
            # Format: (data, filename) or (data, filename, is_binary)
            layer_content = layer_item[0]
            original_filename = layer_item[1]
            is_binary = layer_item[2] if len(layer_item) > 2 else isinstance(layer_content, bytes)
            
            # Check for None content in tuple
            if layer_content is None:
                print(f"Warning: None content in layer tuple at index {i}, skipping")
                continue
        else:
            # Just data, infer format
            layer_content = layer_item
            original_filename = None
            is_binary = isinstance(layer_content, bytes)
            
            # Check for None content
            if layer_content is None:
                print(f"Warning: None content at index {i}, skipping")
                continue
        
        # Determine data type and filename
        if isinstance(layer_content, str):
            encoded_content = base64.b64encode(layer_content.encode('utf-8')).decode('ascii')
            data_type = "text"
            if not original_filename:
                original_filename = f"layer_{i+1}.txt"
        elif isinstance(layer_content, bytes):
            encoded_content = base64.b64encode(layer_content).decode('ascii')
            data_type = "binary"
            
            # Enhanced filename detection for binary data
            if not original_filename or original_filename in ["existing_data", "extracted_data.bin", "layer_data"]:
                # Check for common binary file signatures to determine proper extension
                if layer_content.startswith(b'\x89PNG\r\n\x1a\n'):
                    original_filename = f"layer_{i+1}.png"
                elif layer_content.startswith(b'\xff\xd8\xff'):
                    original_filename = f"layer_{i+1}.jpg"
                elif layer_content.startswith(b'GIF87a') or layer_content.startswith(b'GIF89a'):
                    original_filename = f"layer_{i+1}.gif"
                elif layer_content.startswith(b'BM'):
                    original_filename = f"layer_{i+1}.bmp"
                elif layer_content.startswith(b'RIFF') and b'WEBP' in layer_content[:12]:
                    original_filename = f"layer_{i+1}.webp"
                elif layer_content.startswith(b'RIFF') and b'WAVE' in layer_content[:12]:
                    original_filename = f"layer_{i+1}.wav"
                elif layer_content.startswith(b'ID3') or layer_content[0:2] == b'\xff\xfb' or layer_content[0:2] == b'\xff\xf3':
                    original_filename = f"layer_{i+1}.mp3"
                elif layer_content.startswith(b'%PDF'):
                    original_filename = f"layer_{i+1}.pdf"
                elif layer_content.startswith(b'PK\x03\x04'):  # ZIP file
                    # Could be DOCX, XLSX, etc.
                    if b'word/' in layer_content[:1000]:
                        original_filename = f"layer_{i+1}.docx"
                    elif b'xl/' in layer_content[:1000]:
                        original_filename = f"layer_{i+1}.xlsx"
                    else:
                        original_filename = f"layer_{i+1}.zip"
                else:
                    original_filename = f"layer_{i+1}.bin"
            
            # If we have a filename but it doesn't have proper extension, try to fix it
            elif original_filename and not any(original_filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.wav', '.mp3', '.pdf', '.docx', '.xlsx', '.zip', '.bin']):
                # Add proper extension based on content
                if layer_content.startswith(b'\x89PNG\r\n\x1a\n'):
                    original_filename += ".png"
                elif layer_content.startswith(b'\xff\xd8\xff'):
                    original_filename += ".jpg"
                elif layer_content.startswith(b'GIF87a') or layer_content.startswith(b'GIF89a'):
                    original_filename += ".gif"
                elif layer_content.startswith(b'BM'):
                    original_filename += ".bmp"
                elif layer_content.startswith(b'RIFF') and b'WAVE' in layer_content[:12]:
                    original_filename += ".wav"
                elif layer_content.startswith(b'ID3') or layer_content[0:2] in [b'\xff\xfb', b'\xff\xf3']:
                    original_filename += ".mp3"
                elif layer_content.startswith(b'%PDF'):
                    original_filename += ".pdf"
                else:
                    original_filename += ".bin"
        else:
            # Convert other types to string
            encoded_content = base64.b64encode(str(layer_content).encode('utf-8')).decode('ascii')
            data_type = "text"
            if not original_filename:
                original_filename = f"layer_{i+1}.txt"
        
        container["layers"].append({
            "index": i,
            "filename": original_filename,
            "type": data_type,
            "content": encoded_content,
            "size": len(layer_content) if isinstance(layer_content, (str, bytes)) else len(str(layer_content))
        })
    
    return json.dumps(container)

def extract_layered_data_container(container_data):
    """Extract all layers from a layered data container"""
    import json
    import base64
    
    try:
        if isinstance(container_data, bytes):
            container_json = container_data.decode('utf-8')
        else:
            container_json = container_data
        
        container = json.loads(container_json)
        
        if container.get("type") != "layered_container":
            # Not a layered container, return as-is
            return [(container_data, "extracted_data.bin")]
        
        extracted_layers = []
        for layer in container.get("layers", []):
            # Add defensive check for None layer
            if layer is None:
                print(f"Warning: None layer found in container, skipping")
                continue
            
            # Ensure layer is a dictionary
            if not isinstance(layer, dict):
                print(f"Warning: Invalid layer type {type(layer)}, skipping")
                continue
                
            filename = layer.get("filename", f"layer_{layer.get('index', 0)}.bin")
            content_b64 = layer.get("content", "")
            content_type = layer.get("type", "binary")
            
            # Defensive check for None or empty content
            if not content_b64:
                print(f"Warning: Empty content in layer {layer.get('index', 0)}, skipping")
                continue
            
            try:
                decoded_content = base64.b64decode(content_b64)
                if content_type == "text":
                    # Convert back to string for text content
                    decoded_content = decoded_content.decode('utf-8')
                else:
                    # For binary content, detect file format and fix filename
                    if isinstance(decoded_content, bytes) and decoded_content:
                        detected_extension = detect_file_format_from_binary(decoded_content)
                        if detected_extension and (filename.endswith('.bin') or 'layer_' in filename):
                            # Replace generic filename with detected format
                            layer_num = layer.get('index', len(extracted_layers) + 1)
                            filename = f"layer_{layer_num}{detected_extension}"
                            print(f"[EXTRACT] Detected format for layer {layer_num}: {detected_extension}")
                
                extracted_layers.append((decoded_content, filename))
            except Exception as decode_error:
                print(f"Error decoding layer {layer.get('index', 0)}: {decode_error}")
                continue
        
        return extracted_layers
        
    except Exception as e:
        print(f"Error extracting layered container: {e}")
        # Return original data if parsing fails
        return [(container_data, "extracted_data.bin")]

def is_layered_container(data):
    """Check if the data is a layered container"""
    try:
        if isinstance(data, bytes):
            data_str = data.decode('utf-8')
        else:
            data_str = str(data)
        
        parsed = json.loads(data_str)
        return parsed.get("type") == "layered_container"
    except:
        return False

def get_steganography_manager(carrier_type: str, password: str = ""):
    """Get the appropriate steganography manager for the carrier type"""
    if carrier_type not in steganography_managers or steganography_managers[carrier_type] is None:
        return None
    
    try:
        manager_class = steganography_managers[carrier_type]
        
        # Handle different initialization patterns for different managers
        if carrier_type == "audio":
            # UniversalFileAudio now takes password in __init__
            return manager_class(password=password)
        else:
            # Other managers take password in __init__
            return manager_class(password=password)
            
    except Exception as e:
        print(f"Error creating {carrier_type} manager: {e}")
        return None

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
        
        # Log operation start in database - completely optional, don't let it fail the main operation
        db_operation_id = None
        if db:
            try:
                # Only attempt database logging if we have a valid user_id
                # If user_id is invalid or missing, just skip database logging entirely
                if user_id and user_id.strip():
                    db_operation_id = db.log_operation_start(
                        user_id=user_id,
                        operation_type="hide",
                        media_type=carrier_type,
                        original_filename=carrier_file.filename,
                        password=password
                    )
                else:
                    print(f"[INFO] Skipping database logging - no valid user_id provided")
                        
            except Exception as e:
                # Database logging is completely optional - continue without it
                print(f"[INFO] Database logging failed, continuing without it: {e}")
                db_operation_id = None
        
        # Start background processing with file paths instead of UploadFile objects
        # Generate output filename early so we can return it in the response
        expected_output_filename = generate_unique_filename(carrier_filename, "stego_")
        
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
            db,
            expected_output_filename,  # Pass the expected filename
            db_operation_id  # Pass the database operation ID separately
        )
        
        return OperationResponse(
            success=True,
            operation_id=operation_id,
            message="Embedding operation started",
            output_filename=expected_output_filename
        )
        
    except Exception as e:
        if operation_id in active_jobs:
            update_job_status(operation_id, "failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/embed-batch", response_model=OperationResponse)
async def embed_data_batch(
    carrier_files: List[UploadFile] = File(...),
    content_file: Optional[UploadFile] = File(None),
    content_type: str = Form(...),
    text_content: Optional[str] = Form(None),
    password: str = Form(...),
    encryption_type: str = Form("aes-256-gcm"),
    project_name: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Optional[SteganographyDatabase] = Depends(get_db)
):
    """
    Embed the same data/message into multiple carrier files
    Returns a batch operation ID that manages all individual operations
    """
    try:
        batch_operation_id = str(uuid.uuid4())
        
        # Validate that we have carrier files
        if not carrier_files or len(carrier_files) == 0:
            raise HTTPException(status_code=400, detail="At least one carrier file is required")
        
        # Validate that all carrier files are properly uploaded
        for i, carrier_file in enumerate(carrier_files):
            if not carrier_file.filename:
                raise HTTPException(status_code=400, detail=f"Carrier file {i+1} has no filename")
        
        # Initialize batch job tracking
        batch_jobs = {
            "batch_id": batch_operation_id,
            "total_files": len(carrier_files),
            "completed_files": 0,
            "failed_files": 0,
            "individual_operations": [],
            "output_files": [],
            "status": "starting",
            "created_at": datetime.now().isoformat()
        }
        
        active_jobs[batch_operation_id] = batch_jobs
        
        # Process each carrier file
        for i, carrier_file in enumerate(carrier_files):
            try:
                # Auto-detect carrier type if not provided
                file_extension = Path(carrier_file.filename).suffix.lower()
                carrier_type = None
                
                # Detect carrier type based on file extension
                if file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
                    carrier_type = "video"
                elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                    carrier_type = "image"
                elif file_extension in ['.wav', '.mp3', '.flac', '.ogg']:
                    carrier_type = "audio"
                elif file_extension in ['.pdf', '.doc', '.docx']:
                    carrier_type = "document"
                else:
                    # Default to document for unknown types
                    carrier_type = "document"
                
                print(f"[BATCH] Processing carrier file {i+1}/{len(carrier_files)}: {carrier_file.filename} as {carrier_type}")
                
                # Generate unique filenames for this carrier file
                carrier_filename = generate_unique_filename(carrier_file.filename, f"batch_{i+1}_carrier_")
                carrier_path = UPLOAD_DIR / carrier_filename
                
                # Save carrier file
                with open(carrier_path, "wb") as f:
                    content = await carrier_file.read()
                    f.write(content)
                
                # Handle content file for this iteration (need to read it fresh each time)
                content_file_path = None
                if content_file and content_type == "file":
                    content_filename = generate_unique_filename(content_file.filename, f"batch_{i+1}_content_")
                    content_file_path = UPLOAD_DIR / content_filename
                    
                    # Read the content file (need to reset the read position)
                    await content_file.seek(0)  # Reset file position
                    with open(content_file_path, "wb") as f:
                        content = await content_file.read()
                        f.write(content)
                
                # Create individual operation ID
                individual_operation_id = str(uuid.uuid4())
                
                # Log operation start in database for each file
                db_operation_id = None
                if db and user_id:
                    db_operation_id = db.log_operation_start(
                        user_id=user_id,
                        operation_type="hide",
                        media_type=carrier_type,
                        original_filename=carrier_file.filename,
                        password=password
                    )
                
                # Generate expected output filename
                expected_output_filename = generate_unique_filename(carrier_filename, "stego_")
                
                # Add to batch tracking
                batch_jobs["individual_operations"].append({
                    "operation_id": individual_operation_id,
                    "carrier_filename": carrier_file.filename,
                    "carrier_type": carrier_type,
                    "status": "pending",
                    "expected_output": expected_output_filename
                })
                
                # Start background processing for this file
                background_tasks.add_task(
                    process_batch_embed_operation,
                    individual_operation_id,
                    batch_operation_id,
                    i,  # file index
                    str(carrier_path),
                    str(content_file_path) if content_file_path else None,
                    carrier_type,
                    content_type,
                    text_content,
                    password,
                    encryption_type,
                    project_name,
                    user_id,
                    db,
                    expected_output_filename,
                    db_operation_id
                )
                
            except Exception as e:
                print(f"[BATCH ERROR] Failed to process carrier file {i+1}: {str(e)}")
                batch_jobs["failed_files"] += 1
                batch_jobs["individual_operations"].append({
                    "operation_id": "failed",
                    "carrier_filename": carrier_file.filename if hasattr(carrier_file, 'filename') else f"file_{i+1}",
                    "carrier_type": "unknown",
                    "status": "failed",
                    "error": str(e),
                    "expected_output": None
                })
        
        # Update batch status
        active_jobs[batch_operation_id]["status"] = "processing"
        
        return OperationResponse(
            success=True,
            operation_id=batch_operation_id,
            message=f"Batch embedding started for {len(carrier_files)} files",
            output_filename=f"batch_{len(carrier_files)}_files"
        )
        
    except Exception as e:
        if batch_operation_id in active_jobs:
            active_jobs[batch_operation_id]["status"] = "failed"
            active_jobs[batch_operation_id]["error"] = str(e)
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
        
        # Log operation start in database - completely optional, don't let it fail the main operation
        db_operation_id = None
        if db:
            try:
                # Only attempt database logging if we have a valid user_id
                # If user_id is invalid or missing, just skip database logging entirely
                if user_id and user_id.strip():
                    db_operation_id = db.log_operation_start(
                        user_id=user_id,
                        operation_type="extract",
                        media_type=carrier_type,
                        original_filename=stego_file.filename,
                        password=password
                    )
                else:
                    print(f"[INFO] Skipping database logging - no valid user_id provided")
                        
            except Exception as e:
                # Database logging is completely optional - continue without it
                print(f"[INFO] Database logging failed, continuing without it: {e}")
                db_operation_id = None
        
        # Start background processing with file path instead of UploadFile
        background_tasks.add_task(
            process_extract_operation,
            operation_id,
            str(stego_file_path),
            carrier_type,
            password,
            output_format,
            user_id,
            db,
            db_operation_id  # Pass the database operation ID
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

@app.post("/api/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    password: str = Form(...),
    user_id: Optional[str] = Form(None)
):
    """Analyze a file to check for existing hidden data"""
    try:
        # Determine file type
        file_extension = Path(file.filename).suffix.lower()
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
        
        # Save file temporarily
        temp_filename = generate_unique_filename(file.filename, "analyze_")
        temp_file_path = UPLOAD_DIR / temp_filename
        
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Get appropriate steganography manager
        manager = get_steganography_manager(carrier_type, password)
        if not manager:
            raise HTTPException(status_code=500, detail=f"No manager available for {carrier_type}")
        
        # Try to extract existing data
        analysis_result = {
            "has_hidden_data": False,
            "is_layered": False,
            "layer_count": 0,
            "data_preview": None,
            "error": None
        }
        
        try:
            extracted_data = manager.extract_data(str(temp_file_path))
            
            if extracted_data and extracted_data.strip():
                analysis_result["has_hidden_data"] = True
                
                # Check if it's layered data
                data_to_check = extracted_data
                if isinstance(extracted_data, tuple):
                    data_to_check = extracted_data[0]
                
                if isinstance(data_to_check, bytes):
                    try:
                        data_to_check = data_to_check.decode('utf-8')
                    except UnicodeDecodeError:
                        data_to_check = str(data_to_check)
                
                if is_layered_container(data_to_check):
                    analysis_result["is_layered"] = True
                    layers = extract_layered_data_container(data_to_check)
                    analysis_result["layer_count"] = len(layers)
                    analysis_result["data_preview"] = f"Layered container with {len(layers)} layers"
                else:
                    analysis_result["layer_count"] = 1
                    # Provide safe preview
                    if isinstance(data_to_check, str):
                        analysis_result["data_preview"] = data_to_check[:100] + "..." if len(data_to_check) > 100 else data_to_check
                    else:
                        analysis_result["data_preview"] = f"Binary data ({len(data_to_check)} bytes)"
        
        except Exception as e:
            analysis_result["error"] = f"Failed to extract data: {str(e)}"
        
        finally:
            # Clean up temporary file
            if temp_file_path.exists():
                os.remove(temp_file_path)
        
        return {
            "success": True,
            "analysis": analysis_result
        }
        
    except Exception as e:
        # Clean up on error
        if 'temp_file_path' in locals() and temp_file_path.exists():
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# JOB STATUS AND DOWNLOAD ENDPOINTS
# ============================================================================

@app.get("/api/operations/{operation_id}/status", response_model=StatusResponse)
async def get_operation_status(operation_id: str):
    """Get status of a steganography operation (regular or batch)"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    job = active_jobs[operation_id]
    
    # Handle batch operations
    if "batch_id" in job:
        total_files = job.get("total_files", 0)
        completed_files = job.get("completed_files", 0)
        failed_files = job.get("failed_files", 0)
        
        # Calculate overall progress
        progress = 0
        if total_files > 0:
            progress = int((completed_files + failed_files) * 100 / total_files)
        
        # Create batch-specific result
        batch_result = {
            "batch_operation": True,
            "total_files": total_files,
            "completed_files": completed_files,
            "failed_files": failed_files,
            "output_files": job.get("output_files", []),
            "individual_operations": job.get("individual_operations", [])
        }
        
        return StatusResponse(
            status=job["status"],
            progress=progress,
            message=f"Processed {completed_files + failed_files}/{total_files} files",
            error=job.get("error"),
            result=batch_result
        )
    else:
        # Handle regular operations
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

@app.get("/api/operations/{operation_id}/download-batch")
async def download_batch_result(operation_id: str):
    """Download all result files from a batch operation as a ZIP archive"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Batch operation not found")
    
    job = active_jobs[operation_id]
    
    # Check if this is a batch operation
    if "batch_id" not in job:
        raise HTTPException(status_code=400, detail="This is not a batch operation")
    
    if job["status"] not in ["completed", "completed_with_errors"]:
        raise HTTPException(status_code=400, detail="Batch operation not completed")
    
    output_files = job.get("output_files", [])
    if not output_files:
        raise HTTPException(status_code=404, detail="No output files found")
    
    # Create a temporary ZIP file
    zip_filename = f"batch_results_{operation_id[:8]}.zip"
    zip_path = OUTPUT_DIR / zip_filename
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file_info in enumerate(output_files):
                output_file_path = file_info["output_path"]
                if os.path.exists(output_file_path):
                    # Use original filename or create a numbered filename
                    archive_filename = file_info["output_filename"]
                    
                    # Add file to ZIP with the proper name
                    zipf.write(output_file_path, archive_filename)
                    print(f"[BATCH ZIP] Added {archive_filename} to archive")
                else:
                    print(f"[BATCH ZIP] Warning: File not found: {output_file_path}")
        
        if not os.path.exists(zip_path):
            raise HTTPException(status_code=500, detail="Failed to create ZIP archive")
        
        # Return the ZIP file
        return FileResponse(
            zip_path,
            filename=zip_filename,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=\"{zip_filename}\""}
        )
        
    except Exception as e:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        raise HTTPException(status_code=500, detail=f"Failed to create ZIP archive: {str(e)}")

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
    db: Optional[SteganographyDatabase],
    expected_output_filename: Optional[str] = None,
    db_operation_id: Optional[str] = None
):
    """Background task to process embedding operation"""
    
    import json
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
        
        update_job_status(operation_id, "processing", 40, "Checking for existing hidden data")
        
        # Check if carrier already contains hidden data
        existing_data = None
        original_filename = None
        try:
            print(f"[EMBED] Checking if carrier file already contains hidden data...")
            # Try to extract existing data (this will show extraction logs but failure is normal for clean files)
            extraction_result = manager.extract_data(carrier_file_path)
            
            # Handle tuple return (data, filename) from some managers
            if isinstance(extraction_result, tuple):
                existing_data, original_filename = extraction_result
            else:
                existing_data = extraction_result
                original_filename = None
            
            # Check if we found meaningful existing data
            if existing_data:
                print(f"[EMBED] ✅ Found existing data: type={type(existing_data)}, size={len(existing_data) if hasattr(existing_data, '__len__') else 'unknown'}")
                
                # Check if existing data is already a layered container
                is_existing_layered = False
                existing_data_for_check = existing_data
                
                # Add comprehensive debugging for second embedding attempt
                print(f"[EMBED DEBUG] Processing existing data - Type: {type(existing_data)}")
                print(f"[EMBED DEBUG] Current operation - content_type: {content_type}")
                print(f"[EMBED DEBUG] Current operation - content_file_path: {content_file_path}")
                print(f"[EMBED DEBUG] Current operation - text_content: {text_content is not None}")
                
                if isinstance(existing_data, bytes):
                    print(f"[EMBED DEBUG] Bytes data length: {len(existing_data)}")
                    print(f"[EMBED DEBUG] First 100 bytes: {existing_data[:100]}")
                
                # Only try to decode bytes to string if it looks like JSON
                if isinstance(existing_data, bytes):
                    try:
                        # Only decode if it starts with { (JSON indicator)
                        if existing_data.startswith(b'{'):
                            decoded_str = existing_data.decode('utf-8')
                            print(f"[EMBED DEBUG] Decoded string length: {len(decoded_str)}")
                            print(f"[EMBED DEBUG] First 200 chars: {decoded_str[:200]}")
                            
                            is_existing_layered = is_layered_container(decoded_str)
                            print(f"[EMBED DEBUG] is_layered_container result: {is_existing_layered}")
                            
                            if is_existing_layered:
                                existing_data_for_check = decoded_str
                                print(f"[EMBED DEBUG] Set existing_data_for_check to decoded string")
                            else:
                                print(f"[EMBED DEBUG] Not a layered container, treating as binary data")
                    except (UnicodeDecodeError, json.JSONDecodeError) as decode_error:
                        # Not a layered container, treat as binary data
                        print(f"[EMBED DEBUG] Decode error: {decode_error}, treating as binary data")
                        pass
                elif isinstance(existing_data, str):
                    print(f"[EMBED DEBUG] String data length: {len(existing_data)}")
                    print(f"[EMBED DEBUG] First 200 chars: {existing_data[:200]}")
                    is_existing_layered = is_layered_container(existing_data)
                    print(f"[EMBED DEBUG] is_layered_container result for string: {is_existing_layered}")
                
                print(f"[EMBED DEBUG] Final check - is_existing_layered: {is_existing_layered}, existing_data_for_check type: {type(existing_data_for_check)}")
                
                # Only proceed with layering if we have non-empty data
                should_create_layer = False
                if isinstance(existing_data, str) and existing_data.strip():
                    should_create_layer = True
                elif isinstance(existing_data, bytes) and len(existing_data) > 0:
                    should_create_layer = True
                
                print(f"[EMBED DEBUG] should_create_layer: {should_create_layer}")
                
                if should_create_layer:
                    update_job_status(operation_id, "processing", 45, f"Found existing data, creating layered container")
                    
                    # Prepare existing layers
                    existing_layers = []  # Initialize to prevent NoneType errors
                    
                    if is_existing_layered:
                        # Extract existing layers from layered container
                        print(f"[EMBED DEBUG] Attempting to extract existing layers from layered container")
                        print(f"[EMBED DEBUG] existing_data_for_check type: {type(existing_data_for_check)}")
                        print(f"[EMBED DEBUG] existing_data_for_check value preview: {str(existing_data_for_check)[:500] if existing_data_for_check else 'None'}")
                        
                        try:
                            # Add extra safety check before calling extraction
                            if existing_data_for_check is None:
                                print(f"[EMBED ERROR] existing_data_for_check is None before extraction!")
                                existing_layers = []
                            else:
                                extracted_layers = extract_layered_data_container(existing_data_for_check)
                                print(f"[EMBED DEBUG] extract_layered_data_container returned: {type(extracted_layers)}")
                                
                                if extracted_layers is not None and isinstance(extracted_layers, list):
                                    existing_layers = extracted_layers
                                    print(f"[EMBED DEBUG] Successfully extracted {len(existing_layers)} existing layers")
                                    update_job_status(operation_id, "processing", 47, f"Extracted {len(existing_layers)} existing layers")
                                    
                                    # Debug each extracted layer
                                    for idx, layer in enumerate(existing_layers):
                                        if layer is None:
                                            print(f"[EMBED ERROR] Layer {idx} is None!")
                                        elif not isinstance(layer, tuple) or len(layer) != 2:
                                            print(f"[EMBED ERROR] Layer {idx} has invalid format: {type(layer)}, length: {len(layer) if hasattr(layer, '__len__') else 'no length'}")
                                        else:
                                            print(f"[EMBED DEBUG] Layer {idx}: content type={type(layer[0])}, filename='{layer[1]}'")
                                else:
                                    print(f"[EMBED WARNING] extract_layered_data_container returned {type(extracted_layers)}, using empty list")
                                    existing_layers = []
                        except Exception as e:
                            print(f"[EMBED ERROR] Failed to extract existing layers: {e}")
                            print(f"[EMBED ERROR] Exception type: {type(e)}")
                            import traceback
                            print(f"[EMBED ERROR] Traceback: {traceback.format_exc()}")
                            existing_layers = []
                    else:
                        # Convert existing single data to first layer
                        # Determine appropriate filename for existing data
                        if original_filename and original_filename.strip():
                            existing_filename = original_filename
                        else:
                            # Auto-detect filename based on content type
                            if isinstance(existing_data, bytes):
                                detected_ext = detect_file_format_from_binary(existing_data)
                                if detected_ext:
                                    existing_filename = f"existing_file{detected_ext}"
                                else:
                                    existing_filename = "existing_file.bin"
                            else:
                                existing_filename = "existing_text.txt"
                        
                        existing_layers = [(existing_data, existing_filename)]
                        update_job_status(operation_id, "processing", 47, f"Converting existing data to layer: {existing_filename}")
                    
                    # Prepare new content layer
                    new_layer_info = None
                    try:
                        if content_type == "text":
                            new_layer_info = (content_to_hide, "new_message.txt")
                            print(f"[EMBED DEBUG] Created text layer: new_message.txt")
                        else:
                            # For file content, preserve original filename
                            new_filename = "new_file.bin"  # Default fallback
                            
                            if content_file_path and Path(content_file_path).exists():
                                new_filename = Path(content_file_path).name
                                print(f"[EMBED DEBUG] Using original filename: {new_filename}")
                            else:
                                # Detect format if no filename available or file doesn't exist
                                if isinstance(content_to_hide, bytes):
                                    detected_ext = detect_file_format_from_binary(content_to_hide)
                                    new_filename = f"new_file{detected_ext}" if detected_ext else "new_file.bin"
                                    print(f"[EMBED DEBUG] Detected filename: {new_filename}")
                                else:
                                    print(f"[EMBED DEBUG] Using default filename: {new_filename}")
                            
                            new_layer_info = (content_to_hide, new_filename)
                            print(f"[EMBED DEBUG] Created file layer: {new_filename}")
                    except Exception as e:
                        print(f"[EMBED ERROR] Failed to create new layer info: {e}")
                        print(f"[EMBED ERROR] content_file_path: {content_file_path}")
                        print(f"[EMBED ERROR] content_to_hide type: {type(content_to_hide)}")
                        import traceback
                        print(f"[EMBED ERROR] Traceback: {traceback.format_exc()}")
                        new_layer_info = (content_to_hide, "error_recovery.bin")
                    
                    # Add new layer to existing layers only if valid AND we have enough capacity
                    if new_layer_info is not None and existing_layers is not None:
                        # CAPACITY CHECK: For document steganography with small containers, 
                        # skip layered containers due to JSON overhead
                        carrier_size = os.path.getsize(carrier_file_path) if os.path.exists(carrier_file_path) else 0
                        is_small_container = carrier_size < 1000  # Less than 1KB
                        is_document = carrier_type == "document"
                        
                        if is_small_container and is_document:
                            print(f"[EMBED] CAPACITY OPTIMIZATION: Skipping layered container for small document ({carrier_size} bytes)")
                            print(f"[EMBED] Using direct embedding to avoid JSON overhead")
                            update_job_status(operation_id, "processing", 48, f"Using direct embedding for small document")
                        else:
                            existing_layers.append(new_layer_info)
                            update_job_status(operation_id, "processing", 48, f"Added new content as layer {len(existing_layers)}: {new_layer_info[1]}")
                            
                            # Create layered container with all layers
                            try:
                                layered_container = create_layered_data_container(existing_layers)
                                if layered_container is not None:
                                    # Replace content with layered container (as string since it's JSON)
                                    content_to_hide = layered_container
                                    # Update content type since we're now embedding JSON text, not the original file
                                    content_type = "text"
                                    original_filename = None
                                    
                                    update_job_status(operation_id, "processing", 49, f"Created layered container with {len(existing_layers)} layers")
                                    print(f"[EMBED] Successfully created layered container with {len(existing_layers)} layers")
                                else:
                                    print("[EMBED ERROR] create_layered_data_container returned None, falling back to normal embedding")
                            except Exception as e:
                                print(f"[EMBED ERROR] Failed to create layered container: {e}, falling back to normal embedding")
                    
        except Exception as e:
            # If extraction fails, it means no hidden data exists (this is normal for clean files)
            update_job_status(operation_id, "processing", 42, "No existing data found - ready for fresh embedding")
            print(f"[EMBED] ✅ No existing data detected (normal for clean files) - proceeding with fresh embedding")
            # Continue with normal embedding
            pass
        
        # Generate output filename
        carrier_filename = Path(carrier_file_path).name
        if expected_output_filename:
            output_filename = expected_output_filename
        else:
            output_filename = generate_unique_filename(carrier_filename, "stego_")
        output_path = OUTPUT_DIR / output_filename
        
        # Perform embedding
        # After layered container creation, content_type might have been changed to "text"
        # So we need to determine is_file and original_filename based on the current state
        is_file = content_type == "file"
        original_filename = None
        
        # Only set original_filename if we're still dealing with a file (not layered container)
        if is_file and content_file_path and Path(content_file_path).exists():
            original_filename = Path(content_file_path).name
        
        print(f"[EMBED DEBUG] Final embedding parameters:")
        print(f"  content_type: {content_type}")
        print(f"  is_file: {is_file}")
        print(f"  original_filename: {original_filename}")
        print(f"  content_file_path: {content_file_path}")
        print(f"  content_to_hide type: {type(content_to_hide)}")
        print(f"  content_to_hide size: {len(content_to_hide) if hasattr(content_to_hide, '__len__') else 'unknown'}")
        
        if carrier_type == "video":
            # Video manager returns a dict result
            try:
                print(f"[DEBUG VIDEO] About to call video manager.hide_data")
                print(f"[DEBUG VIDEO] Parameters: video_path={carrier_file_path}, output_path={str(output_path)}")
                manager_result = manager.hide_data(
                    carrier_file_path,
                    content_to_hide,
                    str(output_path),
                    password,
                    is_file,
                    original_filename
                )
                print(f"[DEBUG VIDEO] Video manager returned: {manager_result}")
                success = manager_result.get("success", False)
                # Get actual output path from result if available
                actual_output_path = manager_result.get("output_path", str(output_path))
                print(f"[DEBUG VIDEO] Expected path: {output_path}")
                print(f"[DEBUG VIDEO] Video result output_path: {manager_result.get('output_path')}")
                print(f"[DEBUG VIDEO] Actual output path: {actual_output_path}")
                print(f"[DEBUG VIDEO] File exists check: {os.path.exists(actual_output_path)}")
            except Exception as e:
                print(f"[DEBUG VIDEO] Exception in video manager: {e}")
                print(f"[DEBUG VIDEO] Exception type: {type(e)}")
                import traceback
                traceback.print_exc()
                raise
        else:
            # Other managers (image, audio, document) return dict results too
            # Check if manager supports original_filename parameter
            import inspect
            sig = inspect.signature(manager.hide_data)
            if 'original_filename' in sig.parameters:
                manager_result = manager.hide_data(
                    carrier_file_path,
                    content_to_hide,
                    str(output_path),
                    is_file,
                    original_filename
                )
            else:
                manager_result = manager.hide_data(
                    carrier_file_path,
                    content_to_hide,
                    str(output_path),
                    is_file
                )
            success = manager_result.get("success", False)
            # Get actual output path from result if available
            actual_output_path = manager_result.get("output_path", str(output_path))
        
        if not success:
            error_msg = manager_result.get("error", "Embedding operation failed") if isinstance(manager_result, dict) else "Embedding operation failed"
            raise Exception(error_msg)
        
        # Use actual output path instead of expected path
        if actual_output_path != str(output_path):
            output_path = Path(actual_output_path)
            output_filename = output_path.name
        
        update_job_status(operation_id, "processing", 90, "Finalizing")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log completion in database
        if db and user_id and db_operation_id:
            message_preview = text_content[:100] if content_type == "text" else f"File: {Path(content_file_path).name if content_file_path else 'unknown'}"
            db.log_operation_complete(
                db_operation_id,
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
        
        # Add format-specific warnings for video files
        if carrier_type == "video" and 'manager_result' in locals() and isinstance(manager_result, dict):
            if manager_result.get('video_format') == 'AVI':
                result["format_warning"] = "AVI format detected - audio may not play properly. Consider using MP4 format for better compatibility."
            elif manager_result.get('compatibility_warning'):
                result["format_warning"] = manager_result['compatibility_warning']
        
        update_job_status(operation_id, "completed", 100, "Embedding completed successfully", result=result)
        
        # Cleanup input files
        os.remove(carrier_file_path)
        if content_type == "file" and content_file_path and os.path.exists(content_file_path):
            os.remove(content_file_path)
            
    except Exception as e:
        error_msg = str(e)
        update_job_status(operation_id, "failed", error=error_msg)
        
        # Log failure in database
        if db and user_id and db_operation_id:
            db.log_operation_complete(
                db_operation_id,
                success=False,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )

async def process_batch_embed_operation(
    individual_operation_id: str,
    batch_operation_id: str,
    file_index: int,
    carrier_file_path: str,
    content_file_path: Optional[str],
    carrier_type: str,
    content_type: str,
    text_content: Optional[str],
    password: str,
    encryption_type: str,
    project_name: Optional[str],
    user_id: Optional[str],
    db: Optional[SteganographyDatabase],
    expected_output_filename: Optional[str] = None,
    db_operation_id: Optional[str] = None
):
    """Background task to process embedding operation for one file in a batch"""
    
    import json
    start_time = time.time()
    
    try:
        print(f"[BATCH] Starting processing for file {file_index + 1} - {individual_operation_id}")
        
        # Update batch status
        if batch_operation_id in active_jobs:
            active_jobs[batch_operation_id]["individual_operations"][file_index]["status"] = "processing"
        
        # Prepare content to hide (same logic as regular embed)
        if content_type == "text":
            content_to_hide = text_content
        else:
            # Read content from file
            with open(content_file_path, "rb") as f:
                content_to_hide = f.read()
        
        # Get appropriate steganography manager
        manager = get_steganography_manager(carrier_type, password)
        if not manager:
            raise Exception(f"No manager available for {carrier_type}")
        
        # Check if carrier already contains hidden data (same logic as regular embed)
        existing_data = None
        original_filename = None
        try:
            extraction_result = manager.extract_data(carrier_file_path)
            
            if isinstance(extraction_result, tuple):
                existing_data, original_filename = extraction_result
            else:
                existing_data = extraction_result
                original_filename = None
            
            if existing_data:
                print(f"[BATCH] Found existing data in carrier file {file_index + 1}")
                
                # Handle layered containers (same logic as regular embed)
                if isinstance(existing_data, str):
                    try:
                        layered_data = json.loads(existing_data)
                        if isinstance(layered_data, dict) and layered_data.get("type") == "layered_container":
                            existing_layers = layered_data.get("layers", [])
                            print(f"[BATCH] Found {len(existing_layers)} existing layers")
                            
                            # Add new layer
                            if content_type == "text":
                                new_layer_info = (content_to_hide, "new_message.txt")
                            else:
                                new_filename = Path(content_file_path).name if content_file_path else "new_file.bin"
                                new_layer_info = (content_to_hide, new_filename)
                            
                            existing_layers.append(new_layer_info)
                            layered_container = create_layered_data_container(existing_layers)
                            
                            if layered_container:
                                content_to_hide = layered_container
                                content_type = "text"
                                original_filename = None
                                print(f"[BATCH] Created layered container with {len(existing_layers)} layers")
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            print(f"[BATCH] No existing data detected in file {file_index + 1}: {e}")
            pass
        
        # Generate output filename
        carrier_filename = Path(carrier_file_path).name
        if expected_output_filename:
            output_filename = expected_output_filename
        else:
            output_filename = generate_unique_filename(carrier_filename, "stego_")
        output_path = OUTPUT_DIR / output_filename
        
        # Perform embedding
        is_file = content_type == "file"
        original_filename = None
        
        if is_file and content_file_path and Path(content_file_path).exists():
            original_filename = Path(content_file_path).name
        
        print(f"[BATCH] Embedding in file {file_index + 1}: {carrier_type}, is_file: {is_file}")
        
        if carrier_type == "video":
            result = manager.hide_data(
                carrier_file_path,
                content_to_hide,
                str(output_path),
                is_file,
                original_filename
            )
            success = result.get("success", False)
            actual_output_path = result.get("output_path", str(output_path))
        else:
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
            actual_output_path = result.get("output_path", str(output_path))
        
        if not success:
            error_msg = result.get("error", "Embedding operation failed") if isinstance(result, dict) else "Embedding operation failed"
            raise Exception(error_msg)
        
        # Use actual output path
        if actual_output_path != str(output_path):
            output_path = Path(actual_output_path)
            output_filename = output_path.name
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log completion in database
        if db and user_id and db_operation_id:
            message_preview = text_content[:100] if content_type == "text" else f"File: {Path(content_file_path).name if content_file_path else 'unknown'}"
            db.log_operation_complete(
                db_operation_id,
                success=True,
                output_filename=output_filename,
                file_size=os.path.getsize(output_path),
                message_preview=message_preview,
                processing_time=processing_time
            )
        
        # Update batch tracking
        if batch_operation_id in active_jobs:
            active_jobs[batch_operation_id]["completed_files"] += 1
            active_jobs[batch_operation_id]["individual_operations"][file_index]["status"] = "completed"
            active_jobs[batch_operation_id]["individual_operations"][file_index]["output_file"] = str(output_path)
            active_jobs[batch_operation_id]["individual_operations"][file_index]["processing_time"] = processing_time
            active_jobs[batch_operation_id]["output_files"].append({
                "original_filename": Path(carrier_file_path).name,
                "output_filename": output_filename,
                "output_path": str(output_path),
                "file_size": os.path.getsize(output_path),
                "carrier_type": carrier_type
            })
            
            # Check if batch is complete
            total_files = active_jobs[batch_operation_id]["total_files"]
            completed_files = active_jobs[batch_operation_id]["completed_files"]
            failed_files = active_jobs[batch_operation_id]["failed_files"]
            
            if completed_files + failed_files >= total_files:
                if failed_files == 0:
                    active_jobs[batch_operation_id]["status"] = "completed"
                else:
                    active_jobs[batch_operation_id]["status"] = "completed_with_errors"
                
                print(f"[BATCH] Batch {batch_operation_id} completed: {completed_files} success, {failed_files} failed")
        
        # Cleanup input files for this operation
        os.remove(carrier_file_path)
        if content_type == "file" and content_file_path and os.path.exists(content_file_path):
            os.remove(content_file_path)
            
        print(f"[BATCH] Successfully completed file {file_index + 1}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"[BATCH ERROR] Failed to process file {file_index + 1}: {error_msg}")
        
        # Log failure in database
        if db and user_id and db_operation_id:
            db.log_operation_complete(
                db_operation_id,
                success=False,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )
        
        # Update batch tracking
        if batch_operation_id in active_jobs:
            active_jobs[batch_operation_id]["failed_files"] += 1
            active_jobs[batch_operation_id]["individual_operations"][file_index]["status"] = "failed"
            active_jobs[batch_operation_id]["individual_operations"][file_index]["error"] = error_msg
            
            # Check if batch is complete
            total_files = active_jobs[batch_operation_id]["total_files"]
            completed_files = active_jobs[batch_operation_id]["completed_files"]
            failed_files = active_jobs[batch_operation_id]["failed_files"]
            
            if completed_files + failed_files >= total_files:
                if failed_files == total_files:
                    active_jobs[batch_operation_id]["status"] = "failed"
                else:
                    active_jobs[batch_operation_id]["status"] = "completed_with_errors"

async def process_extract_operation(
    operation_id: str,
    stego_file_path: str,
    carrier_type: str,
    password: str,
    output_format: str,
    user_id: Optional[str],
    db: Optional[SteganographyDatabase],
    db_operation_id: Optional[str] = None
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
        print(f"[DEBUG EXTRACT] About to call manager.extract_data for {carrier_type}")
        print(f"[DEBUG EXTRACT] Password received: {repr(password)}")
        if hasattr(manager, 'safe_stego') and hasattr(manager.safe_stego, 'password'):
            print(f"[DEBUG EXTRACT] Manager password set to: {repr(manager.safe_stego.password)}")
        extraction_result = manager.extract_data(stego_file_path)
        
        # DEBUG: Log extraction result details
        print(f"[DEBUG EXTRACT] extraction_result type: {type(extraction_result)}")
        print(f"[DEBUG EXTRACT] extraction_result: {repr(extraction_result)[:200]}")
        
        if extraction_result is None or (isinstance(extraction_result, tuple) and extraction_result[0] is None):
            raise Exception("Extraction failed - wrong password or no hidden data")
        
        # Handle tuple return (data, filename) from managers
        if isinstance(extraction_result, tuple):
            extracted_data, original_filename = extraction_result
            print(f"[DEBUG EXTRACT] Tuple unpacked - data type: {type(extracted_data)}, filename: {original_filename}")
        else:
            extracted_data = extraction_result
            original_filename = None
            print(f"[DEBUG EXTRACT] Non-tuple result - data type: {type(extracted_data)}")
        
        update_job_status(operation_id, "processing", 70, "Checking for layered data")
        
        # Check if extracted data is a layered container
        is_layered_data = False
        if isinstance(extracted_data, str):
            is_layered_data = is_layered_container(extracted_data)
            print(f"[DEBUG EXTRACT] String data - layered: {is_layered_data}")
        elif isinstance(extracted_data, bytes):
            try:
                decoded_data = extracted_data.decode('utf-8')
                is_layered_data = is_layered_container(decoded_data)
                if is_layered_data:
                    extracted_data = decoded_data
                    print(f"[DEBUG EXTRACT] Converted bytes to string for layered container")
            except UnicodeDecodeError:
                is_layered_data = False
                print(f"[DEBUG EXTRACT] Bytes data - not UTF-8 decodable, not layered")
        
        if is_layered_data:
            update_job_status(operation_id, "processing", 75, "Extracting multiple layers")
            print(f"[EXTRACT] Detected layered container, extracting layers...")
            
            # Extract all layers from the container
            layers = extract_layered_data_container(extracted_data)
            print(f"[EXTRACT] Extracted {len(layers)} layers")
            
            # Create a ZIP file containing all layers
            import zipfile
            zip_filename = f"extracted_layers_{int(time.time())}.zip"
            zip_path = OUTPUT_DIR / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, (layer_content, layer_filename) in enumerate(layers):
                    # Use the actual filename from the layer, or generate one
                    if not layer_filename or layer_filename == "extracted_data.bin":
                        if isinstance(layer_content, str):
                            layer_filename = f"layer_{i+1}.txt"
                        else:
                            # Try to detect file format for binary content
                            detected_extension = detect_file_format_from_binary(layer_content)
                            if detected_extension:
                                layer_filename = f"layer_{i+1}{detected_extension}"
                                print(f"[EXTRACT] Detected format for layer {i+1}: {detected_extension}")
                            else:
                                layer_filename = f"layer_{i+1}.bin"
                    
                    # If filename still ends with .bin, try to detect format
                    elif layer_filename.endswith('.bin') and isinstance(layer_content, bytes):
                        detected_extension = detect_file_format_from_binary(layer_content)
                        if detected_extension:
                            # Replace .bin with detected extension
                            layer_filename = layer_filename[:-4] + detected_extension
                            print(f"[EXTRACT] Fixed .bin filename to: {layer_filename}")
                    
                    # Ensure filename is safe for ZIP
                    import re
                    layer_filename = re.sub(r'[<>:"/\\|?*]', '_', layer_filename)
                    
                    print(f"[EXTRACT] Adding layer {i+1}: {layer_filename} ({len(layer_content)} bytes, type: {type(layer_content)})")
                    
                    # Write content to ZIP with proper format preservation
                    if isinstance(layer_content, str):
                        zipf.writestr(layer_filename, layer_content.encode('utf-8'))
                    elif isinstance(layer_content, bytes):
                        zipf.writestr(layer_filename, layer_content)
                    else:
                        # Fallback for other types
                        zipf.writestr(layer_filename, str(layer_content).encode('utf-8'))
            
            print(f"[EXTRACT] Created ZIP file: {zip_filename}")
            
            # Set the output path to the ZIP file
            output_path = zip_path
            output_filename = zip_filename
            
        else:
            # Single layer extraction - proceed with normal logic
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
                
                # Ensure we have a valid filename with proper extension
                if not output_filename or output_filename.startswith('.') or len(output_filename.strip()) == 0:
                    # Extract extension from original filename if possible
                    original_ext = Path(original_filename).suffix if original_filename else ".bin"
                    output_filename = f"extracted_file_{int(time.time())}{original_ext}"
                elif '.' not in output_filename:
                    # If filename has no extension, add .txt for text or .bin for binary
                    if isinstance(extracted_data, str):
                        output_filename = f"{output_filename}.txt"
                    else:
                        output_filename = f"{output_filename}.bin"
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
        if db and user_id and db_operation_id:
            if isinstance(extracted_data, str):
                preview = extracted_data[:100]
            elif isinstance(extracted_data, bytes):
                preview = f"Binary file ({len(extracted_data)} bytes)"
            else:
                preview = f"Unknown data type: {type(extracted_data)}"
            
            db.log_operation_complete(
                db_operation_id,
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
        if db and user_id and db_operation_id:
            db.log_operation_complete(
                db_operation_id,
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
# DIRECT FILE DOWNLOAD ENDPOINT
# ============================================================================

@app.get("/api/download/{filename}")
async def download_file_by_name(filename: str):
    """Download a file by filename from outputs directory"""
    
    # Security check - prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Check outputs directory first
    output_file = OUTPUT_DIR / filename
    if not output_file.exists():
        # Fallback to uploads directory (for testing)
        output_file = UPLOAD_DIR / filename
        if not output_file.exists():
            raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on file extension
    file_ext = Path(filename).suffix.lower()
    media_type_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg', 
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.webm': 'video/webm',
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.flac': 'audio/flac',
        '.ogg': 'audio/ogg',
        '.aac': 'audio/aac',
        '.m4a': 'audio/mp4',
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.txt': 'text/plain',
        '.rtf': 'application/rtf',
        '.doc': 'application/msword'
    }
    
    media_type = media_type_map.get(file_ext, 'application/octet-stream')
    
    return FileResponse(
        path=str(output_file),
        filename=filename,
        media_type=media_type
    )

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
            "operation_type": job.get("operation_type", "hide")
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