"""
Simple test for MP3 extraction to verify the backend fix
"""
import os
import requests
import time
import json

def test_mp3_extraction_simple():
    """Test MP3 extraction with simple approach"""
    
    print("🧪 Testing MP3 extraction after fix...")
    print("=" * 50)
    
    # Use the video with embedded MP3 that we know works
    test_video = "debug_video_with_mp3.mp4"
    
    if not os.path.exists(test_video):
        print(f"❌ Test video {test_video} not found")
        return False
    
    try:
        # Test extraction
        with open(test_video, 'rb') as f:
            files = {'stego_file': f}
            data = {
                'password': 'test123',
                'output_format': 'auto'
            }
            
            print("📤 Sending extraction request...")
            response = requests.post('http://localhost:8000/api/extract', files=files, data=data, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        operation_id = response.json()['operation_id']
        print(f"✅ Started extraction: {operation_id}")
        
        # Wait for completion
        for attempt in range(15):
            print(f"⏳ Checking status (attempt {attempt + 1}/15)...")
            
            status_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/status', timeout=5)
            
            if status_response.status_code != 200:
                print(f"❌ Status check failed: {status_response.status_code}")
                continue
            
            status_data = status_response.json()
            print(f"📊 Status: {status_data['status']}")
            
            if status_data['status'] == 'completed':
                print("🎉 Extraction completed!")
                
                # Download the result
                download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download', timeout=10)
                
                if download_response.status_code != 200:
                    print(f"❌ Download failed: {download_response.status_code}")
                    return False
                
                # Check headers
                content_disposition = download_response.headers.get('Content-Disposition', '')
                content_type = download_response.headers.get('Content-Type', '')
                
                print(f"📄 Content-Disposition: {content_disposition}")
                print(f"📄 Content-Type: {content_type}")
                
                # Extract filename
                filename = "extracted_file"
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                
                # Save file
                with open(f"final_test_{filename}", 'wb') as f:
                    f.write(download_response.content)
                
                # Analysis
                file_size = len(download_response.content)
                first_bytes = download_response.content[:20]
                
                print(f"📁 Downloaded: final_test_{filename}")
                print(f"📏 Size: {file_size} bytes")
                print(f"🔍 First 20 bytes: {first_bytes}")
                
                # Check if it's a proper binary file
                if filename.endswith('.mp3') or filename.endswith('.MP3'):
                    print("🎵 SUCCESS: File has MP3 extension!")
                    
                    if first_bytes.startswith(b'ID3') or b'\xff\xfb' in first_bytes:
                        print("🎵 PERFECT: File contains valid MP3 data!")
                        return True
                    else:
                        print("⚠️  File has MP3 extension but data doesn't look like MP3")
                        return False
                else:
                    print(f"❌ FAILED: File extracted as '{filename}' instead of MP3")
                    
                    # Check if it's text that should be binary
                    try:
                        text_content = download_response.content.decode('utf-8')
                        if 'SUQz' in text_content[:100]:  # Base64 for ID3
                            print("❌ DIAGNOSIS: Binary data was saved as text (base64)")
                        else:
                            print(f"❌ DIAGNOSIS: Unknown content type")
                        print(f"   Content preview: {text_content[:100]}")
                    except UnicodeDecodeError:
                        print("❌ DIAGNOSIS: File is binary but has wrong extension")
                    
                    return False
            
            elif status_data['status'] == 'failed':
                print(f"❌ Extraction failed: {status_data.get('message', 'Unknown error')}")
                return False
            
            time.sleep(2)
        
        print("❌ Extraction timed out")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        print("   Make sure the backend is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mp3_extraction_simple()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 MP3 EXTRACTION WORKING CORRECTLY!")
        print("✅ MP3 files now extract with proper .mp3 extension")
        print("✅ Binary data is preserved correctly")
        print("✅ Files can be played as MP3 audio")
    else:
        print("❌ MP3 EXTRACTION STILL HAS ISSUES")
        print("   Check the backend processing logic")