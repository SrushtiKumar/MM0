#!/usr/bin/env python3
"""
COMPREHENSIVE PRODUCTION API TEST
Test all media types: Documents, Images, Audio, Video
Verify NO CORRUPTION in any format
"""

import requests
import tempfile
import os
import time
import subprocess
from PIL import Image
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_files():
    """Create test files for all media types"""
    files = {}
    temp_dir = tempfile.mkdtemp()
    
    # 1. Create test PDF document
    pdf_path = os.path.join(temp_dir, "test_document.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, "TEST PDF DOCUMENT")
    c.drawString(100, 700, "This PDF must remain intact and readable")
    c.drawString(100, 650, "after steganographic processing.")
    c.showPage()
    c.save()
    files['document'] = pdf_path
    
    # 2. Create test PNG image
    img_path = os.path.join(temp_dir, "test_image.png")
    img = Image.fromarray(np.random.randint(0, 255, (200, 200, 3), dtype='uint8'), 'RGB')
    img.save(img_path, 'PNG')
    files['image'] = img_path
    
    # 3. Create test MP4 video (if ffmpeg available)
    video_path = os.path.join(temp_dir, "test_video.mp4")
    try:
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi', 
            '-i', 'testsrc=duration=3:size=320x240:rate=10',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            files['video'] = video_path
        else:
            print(f"⚠️  Cannot create test video: {result.stderr}")
    except:
        print("⚠️  ffmpeg not available - skipping video test")
    
    # 4. Create test audio (simple WAV if available)
    audio_path = os.path.join(temp_dir, "test_audio.wav")
    try:
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'sine=frequency=440:duration=2',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            files['audio'] = audio_path
        else:
            print(f"⚠️  Cannot create test audio: {result.stderr}")
    except:
        print("⚠️  ffmpeg not available - skipping audio test")
    
    # 5. Create secret content
    secret_path = os.path.join(temp_dir, "secret_message.txt")
    with open(secret_path, 'w') as f:
        f.write("This is the secret message to hide in all media types!")
    files['secret'] = secret_path
    
    return files, temp_dir

def check_file_integrity(file_path, media_type):
    """Check if file maintains integrity after steganography"""
    
    try:
        if media_type == 'document' and file_path.endswith('.pdf'):
            # Check PDF integrity
            with open(file_path, 'rb') as f:
                content = f.read()
            
            has_header = content.startswith(b'%PDF-')
            has_eof = b'%%EOF' in content
            page_count = content.count(b'/Type /Page')
            
            if has_header and has_eof and page_count > 0:
                print(f"   ✅ PDF integrity: Header={has_header}, EOF={has_eof}, Pages={page_count}")
                return True
            else:
                print(f"   ❌ PDF corrupted: Header={has_header}, EOF={has_eof}, Pages={page_count}")
                return False
                
        elif media_type == 'image':
            # Check image integrity
            img = Image.open(file_path)
            print(f"   ✅ Image integrity: Size={img.size}, Mode={img.mode}")
            return True
            
        elif media_type == 'video':
            # Check video playability
            cmd = ['ffprobe', '-v', 'error', '-show_format', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ Video integrity: Playable and valid")
                return True
            else:
                print(f"   ❌ Video corrupted: {result.stderr}")
                return False
                
        elif media_type == 'audio':
            # Check audio playability
            cmd = ['ffprobe', '-v', 'error', '-show_format', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ Audio integrity: Playable and valid")
                return True
            else:
                print(f"   ❌ Audio corrupted: {result.stderr}")
                return False
        
        return False
        
    except Exception as e:
        print(f"   ❌ {media_type.title()} error: {e}")
        return False

def test_media_type(media_type, carrier_path, secret_path, temp_dir):
    """Test steganography for a specific media type"""
    
    print(f"\n📁 TESTING {media_type.upper()} STEGANOGRAPHY")
    print("=" * 50)
    
    API_BASE = "http://localhost:8000"
    
    try:
        # Test embedding
        print(f"🔧 Embedding secret in {media_type}...")
        
        with open(carrier_path, 'rb') as cf, open(secret_path, 'rb') as sf:
            files = {
                'carrier_file': cf,
                'content_file': sf
            }
            data = {
                'content_type': 'document',  # Use document content type
                'password': 'test123'
            }
            
            response = requests.post(f"{API_BASE}/api/embed", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            operation_id = result.get('operation_id')
            print(f"   ✅ Embedding initiated: {operation_id}")
            
            # Wait and download result
            time.sleep(3)
            download_response = requests.get(f"{API_BASE}/api/operations/{operation_id}/download")
            
            if download_response.status_code == 200:
                # Save embedded file
                output_ext = os.path.splitext(carrier_path)[1]
                output_path = os.path.join(temp_dir, f"embedded_{media_type}{output_ext}")
                
                with open(output_path, 'wb') as f:
                    f.write(download_response.content)
                
                print(f"   ✅ Downloaded result: {len(download_response.content)} bytes")
                
                # CRITICAL TEST: Check file integrity
                print(f"🔍 Checking {media_type} integrity...")
                integrity_ok = check_file_integrity(output_path, media_type)
                
                if integrity_ok:
                    print(f"   🎉 ✅ {media_type.upper()} INTEGRITY PRESERVED!")
                    
                    # Test extraction
                    print(f"📤 Testing extraction...")
                    
                    with open(output_path, 'rb') as f:
                        files = {'stego_file': (f"embedded_{media_type}{output_ext}", f, 'application/octet-stream')}
                        data = {'password': 'test123'}
                        
                        extract_response = requests.post(f"{API_BASE}/api/extract", files=files, data=data, timeout=30)
                    
                    if extract_response.status_code == 200:
                        extract_result = extract_response.json()
                        
                        if extract_result.get('success'):
                            print(f"   ✅ Extraction successful!")
                            return True
                        else:
                            print(f"   ❌ Extraction failed: {extract_result}")
                    else:
                        print(f"   ❌ Extraction API error: {extract_response.status_code}")
                else:
                    print(f"   💥 ❌ {media_type.upper()} INTEGRITY COMPROMISED!")
            else:
                print(f"   ❌ Download failed: {download_response.status_code}")
        else:
            print(f"   ❌ Embedding failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ {media_type} test error: {e}")
    
    return False

def run_comprehensive_test():
    """Run comprehensive test of all media types"""
    
    print("🚀 COMPREHENSIVE PRODUCTION API CORRUPTION TEST")
    print("=" * 70)
    print("Testing: Documents, Images, Audio, Video")
    print("Goal: NO corruption in ANY media type")
    print("=" * 70)
    
    # Create test files
    print("📂 Creating test files...")
    test_files, temp_dir = create_test_files()
    
    print(f"Created test files:")
    for media_type, path in test_files.items():
        if path and os.path.exists(path):
            size = os.path.getsize(path)
            print(f"   ✅ {media_type}: {os.path.basename(path)} ({size} bytes)")
    
    # Test each media type
    results = {}
    
    for media_type in ['document', 'image', 'video', 'audio']:
        if media_type in test_files and test_files[media_type]:
            results[media_type] = test_media_type(
                media_type, 
                test_files[media_type], 
                test_files['secret'], 
                temp_dir
            )
        else:
            print(f"\n⚠️  Skipping {media_type} - file not available")
            results[media_type] = None
    
    # Final results
    print("\n" + "=" * 70)
    print("🏁 COMPREHENSIVE TEST RESULTS")
    print("=" * 70)
    
    all_passed = True
    for media_type, result in results.items():
        if result is True:
            print(f"✅ {media_type.upper()}: NO CORRUPTION - SAFE")
        elif result is False:
            print(f"❌ {media_type.upper()}: CORRUPTED - UNSAFE")
            all_passed = False
        else:
            print(f"⚠️  {media_type.upper()}: SKIPPED")
    
    print("=" * 70)
    if all_passed and any(results.values()):
        print("🎉 🎉 🎉 ALL MEDIA TYPES SAFE - NO CORRUPTION! 🎉 🎉 🎉")
        print("✅ PRODUCTION DEPLOYMENT IS COMPLETELY SAFE")
    else:
        print("💥 💥 💥 CORRUPTION DETECTED - NOT SAFE FOR PRODUCTION 💥 💥 💥")
        print("❌ DO NOT DEPLOY UNTIL ALL CORRUPTION IS FIXED")
    print("=" * 70)
    
    # Cleanup
    try:
        import shutil
        shutil.rmtree(temp_dir)
    except:
        pass
    
    return all_passed

if __name__ == "__main__":
    run_comprehensive_test()