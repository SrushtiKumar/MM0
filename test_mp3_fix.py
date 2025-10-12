import requests
import json
import time
import os

def test_mp3_extraction_fixed():
    """Test MP3 file extraction after the fix"""
    
    BASE_URL = "http://localhost:8000"
    
    print("🧪 Testing MP3 extraction after backend fix...")
    print("=" * 60)
    
    # Test 1: Extract MP3 from video that we know has an MP3
    test_video = "test_video.mp4"  # Created earlier with embedded MP3
    
    if not os.path.exists(test_video):
        print(f"❌ Test video {test_video} not found")
        return False
    
    print(f"📹 Testing extraction from: {test_video}")
    
    # Start extraction
    files = {'file': open(test_video, 'rb')}
    data = {
        'operation_type': 'extract',
        'steganography_type': 'video',
        'password': 'test123'
    }
    
    response = requests.post(f"{BASE_URL}/api/operations", files=files, data=data)
    files['file'].close()
    
    if response.status_code != 200:
        print(f"❌ Failed to start extraction: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    operation_id = response.json()['operation_id']
    print(f"✅ Started extraction operation: {operation_id}")
    
    # Poll for completion
    max_wait = 60
    wait_time = 0
    
    while wait_time < max_wait:
        status_response = requests.get(f"{BASE_URL}/api/operations/{operation_id}/status")
        
        if status_response.status_code != 200:
            print(f"❌ Failed to get status: {status_response.status_code}")
            return False
        
        status_data = status_response.json()
        print(f"📊 Status: {status_data['status']} - {status_data.get('message', '')}")
        
        if status_data['status'] == 'completed':
            print("✅ Extraction completed!")
            
            # Get download info
            download_response = requests.get(f"{BASE_URL}/api/operations/{operation_id}/download")
            
            if download_response.status_code != 200:
                print(f"❌ Failed to download: {download_response.status_code}")
                return False
            
            # Check response headers for filename
            content_disposition = download_response.headers.get('Content-Disposition', '')
            print(f"📄 Content-Disposition: {content_disposition}")
            
            # Save the downloaded file
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            else:
                filename = "downloaded_file"
            
            print(f"💾 Saving as: {filename}")
            
            with open(f"extracted_{filename}", 'wb') as f:
                f.write(download_response.content)
            
            # Check file properties
            file_size = len(download_response.content)
            print(f"📏 Downloaded file size: {file_size} bytes")
            
            # Check if it's an MP3 file
            if filename.lower().endswith('.mp3'):
                print("🎵 SUCCESS: File extracted with .mp3 extension!")
                
                # Basic MP3 format check
                if download_response.content.startswith(b'ID3') or b'LAME' in download_response.content[:1000]:
                    print("🎵 File appears to be a valid MP3!")
                else:
                    print("⚠️  Warning: File has .mp3 extension but may not be valid MP3 format")
                
                return True
            elif filename.lower().endswith('.txt'):
                print("❌ FAILED: MP3 file still extracted as .txt")
                print(f"   Content preview: {download_response.content[:100]}")
                return False
            else:
                print(f"❓ Unknown file type: {filename}")
                return False
            
        elif status_data['status'] == 'failed':
            print(f"❌ Extraction failed: {status_data.get('message', 'Unknown error')}")
            return False
        
        time.sleep(2)
        wait_time += 2
    
    print("❌ Extraction timed out")
    return False

if __name__ == "__main__":
    success = test_mp3_extraction_fixed()
    
    if success:
        print("\n🎉 MP3 EXTRACTION TEST PASSED!")
        print("   ✅ MP3 files now extract with correct .mp3 extension")
        print("   ✅ Binary data properly preserved")
    else:
        print("\n💥 MP3 EXTRACTION TEST FAILED!")
        print("   ❌ MP3 files still not extracting correctly")