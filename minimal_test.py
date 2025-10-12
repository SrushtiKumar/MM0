"""
Minimal test to verify MP3 extraction works
"""
import os
import requests
import time

def test_extraction():
    """Test extraction with proper error handling"""
    
    try:
        # Simple test
        test_video = "debug_video_with_mp3.mp4"
        
        if not os.path.exists(test_video):
            print("❌ Test video not found")
            return
        
        print("🧪 Testing MP3 extraction...")
        
        # Check if backend is responding
        try:
            health_response = requests.get('http://localhost:8000/health', timeout=5)
            print(f"✅ Backend health check: {health_response.status_code}")
        except:
            print("❌ Backend not responding")
            return
        
        # Test extraction
        with open(test_video, 'rb') as f:
            files = {'stego_file': f}
            data = {'password': 'test123', 'output_format': 'auto'}
            
            print("📤 Sending extraction request...")
            response = requests.post('http://localhost:8000/api/extract', files=files, data=data, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {response.headers}")
        print(f"📊 Response body: {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            operation_id = result.get('operation_id')
            print(f"✅ Extraction started: {operation_id}")
            
            # Wait for completion
            for i in range(10):
                status_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/status')
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"📊 Status {i+1}: {status['status']}")
                    
                    if status['status'] == 'completed':
                        print("🎉 Extraction completed!")
                        
                        # Download result
                        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
                        if download_response.status_code == 200:
                            content_disposition = download_response.headers.get('Content-Disposition', '')
                            print(f"📄 Content-Disposition: {content_disposition}")
                            
                            # Check if it's an MP3
                            if '.mp3' in content_disposition.lower():
                                print("🎵 SUCCESS: File has MP3 extension!")
                                
                                # Check binary content
                                if download_response.content.startswith(b'ID3') or b'\xff\xfb' in download_response.content[:50]:
                                    print("🎵 PERFECT: Valid MP3 binary data!")
                                    print(f"📏 File size: {len(download_response.content)} bytes")
                                    
                                    # Save file
                                    with open("final_extracted_mp3.mp3", 'wb') as f:
                                        f.write(download_response.content)
                                    print("💾 Saved as: final_extracted_mp3.mp3")
                                    return True
                                else:
                                    print("❌ File has MP3 extension but invalid data")
                            else:
                                print(f"❌ Wrong file extension: {content_disposition}")
                        else:
                            print(f"❌ Download failed: {download_response.status_code}")
                        break
                    elif status['status'] == 'failed':
                        print(f"❌ Extraction failed: {status.get('message')}")
                        break
                
                time.sleep(2)
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_extraction()