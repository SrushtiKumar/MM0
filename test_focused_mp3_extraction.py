#!/usr/bin/env python3
"""Test MP3 extraction from PNG steganography"""

import requests
import os
import time

def test_mp3_png_extraction():
    """Test MP3 file hidden in PNG preserves .mp3 extension after extraction"""
    
    # Create a simple test MP3 file with proper header
    test_mp3_content = (
        b'ID3\x03\x00\x00\x00\x00\x00\x00'  # ID3v2.3 header
        b'Test MP3 content for steganography testing\n'
        b'This should preserve the .mp3 extension after extraction.\n'
        b'Multiple lines to test content integrity.\n'
    )
    
    test_mp3_file = "sample_audio.mp3"
    
    # Create test MP3 file
    with open(test_mp3_file, 'wb') as f:
        f.write(test_mp3_content)
    
    print(f"✅ Created test MP3: {test_mp3_file} ({len(test_mp3_content)} bytes)")
    
    try:
        # Step 1: Embed MP3 in PNG image
        print("\n🔄 Embedding MP3 in PNG...")
        
        with open(test_mp3_file, 'rb') as f:
            embed_response = requests.post(
                "http://localhost:8001/embed/image",
                files={"file": f},
                data={"password": "test123"}
            )
        
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.status_code} - {embed_response.text}")
            return
        
        job_id = embed_response.json()["job_id"]
        print(f"✅ Embed job started: {job_id}")
        
        # Wait for embedding completion
        while True:
            status_resp = requests.get(f"http://localhost:8001/status/{job_id}")
            status = status_resp.json()["status"]
            if status == "completed":
                break
            elif status == "failed":
                print("❌ Embedding failed")
                return
            time.sleep(0.5)
        
        print("✅ Embedding completed")
        
        # Step 2: Download processed PNG
        download_resp = requests.get(f"http://localhost:8001/download/{job_id}")
        if download_resp.status_code != 200:
            print(f"❌ Download failed: {download_resp.status_code}")
            return
        
        processed_png = f"processed_image_{job_id}.png"
        with open(processed_png, 'wb') as f:
            f.write(download_resp.content)
        
        print(f"✅ Downloaded processed PNG: {processed_png}")
        
        # Step 3: Extract MP3 from PNG
        print("\n🔄 Extracting MP3 from PNG...")
        
        with open(processed_png, 'rb') as f:
            extract_resp = requests.post(
                "http://localhost:8001/extract/image",
                files={"file": f},
                data={"password": "test123"}
            )
        
        if extract_resp.status_code != 200:
            print(f"❌ Extract failed: {extract_resp.status_code} - {extract_resp.text}")
            return
        
        extract_job_id = extract_resp.json()["job_id"]
        print(f"✅ Extract job started: {extract_job_id}")
        
        # Wait for extraction completion
        while True:
            status_resp = requests.get(f"http://localhost:8001/status/{extract_job_id}")
            status = status_resp.json()["status"]
            if status == "completed":
                break
            elif status == "failed":
                print("❌ Extraction failed")
                return
            time.sleep(0.5)
        
        print("✅ Extraction completed")
        
        # Step 4: Download extracted file and check filename
        extract_download_resp = requests.get(f"http://localhost:8001/download/{extract_job_id}")
        if extract_download_resp.status_code != 200:
            print(f"❌ Extract download failed: {extract_download_resp.status_code}")
            return
        
        # Check Content-Disposition header for filename
        content_disp = extract_download_resp.headers.get('content-disposition', '')
        print(f"📄 Content-Disposition: {content_disp}")
        
        # Check if filename contains .mp3 extension
        if '.mp3' in content_disp:
            print("✅ SUCCESS: Extracted file has .mp3 extension!")
        elif '.bin' in content_disp:
            print("❌ ISSUE: Extracted file has .bin extension instead of .mp3")
        else:
            print(f"⚠️  Unclear: Content disposition: {content_disp}")
        
        # Verify content integrity
        extracted_content = extract_download_resp.content
        print(f"📊 Original: {len(test_mp3_content)} bytes")
        print(f"📊 Extracted: {len(extracted_content)} bytes")
        
        if extracted_content == test_mp3_content:
            print("✅ Content integrity: Perfect match!")
        else:
            print("❌ Content integrity: Mismatch detected")
            print(f"   Original starts: {test_mp3_content[:30]}")
            print(f"   Extracted starts: {extracted_content[:30]}")
        
        # Test MP3 header detection
        if extracted_content.startswith(b'ID3'):
            print("✅ MP3 header: ID3 tag detected correctly")
            # Save with correct extension for testing
            final_file = f"final_extracted_{extract_job_id}.mp3"
            with open(final_file, 'wb') as f:
                f.write(extracted_content)
            print(f"✅ Saved corrected file: {final_file}")
        else:
            print(f"❌ MP3 header: Missing or corrupted - starts with {extracted_content[:10]}")
        
    finally:
        # Cleanup
        if os.path.exists(test_mp3_file):
            os.remove(test_mp3_file)

if __name__ == "__main__":
    test_mp3_png_extraction()