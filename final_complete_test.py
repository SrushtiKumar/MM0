"""
Final Complete Test - All File Types with User-Friendly Error Messages
Tests all fixes including user-friendly error messages
"""
import requests
import json
import time
import os

# Test configuration
base_url = "http://localhost:8000"
test_files_dir = "."

def test_file_steganography():
    print("🔧 FINAL COMPLETE STEGANOGRAPHY TEST")
    print("=" * 60)
    
    # Test 1: Python file in image (should work now)
    print("\n1. Testing Python file (.py) embedding in image...")
    try:
        with open("test_python_file.py", "w") as f:
            f.write("# Test Python File\nprint('Hello from embedded Python!')\n")
        
        with open("test_image.png", "rb") as img, open("test_python_file.py", "rb") as py_file:
            response = requests.post(f"{base_url}/api/embed", files={
                "carrier_file": img,
                "content_file": py_file
            }, data={
                "carrier_type": "image",
                "content_type": "file",
                "password": "test123"
            })
        
        if response.status_code == 200:
            print("✅ Python file embedding successful!")
            
            # Extract and verify
            result = response.json()
            if 'output_file' in result:
                with open(result['output_file'], 'rb') as stego_file:
                    extract_response = requests.post(f"{base_url}/api/extract", files={
                        "stego_file": stego_file
                    }, data={
                        "carrier_type": "image", 
                        "password": "test123"
                    })
                
                if extract_response.status_code == 200:
                    extract_result = extract_response.json()
                    extracted_filename = extract_result.get('filename', 'unknown')
                    print(f"✅ Extraction successful! Filename: {extracted_filename}")
                    
                    if extracted_filename.endswith('.py'):
                        print("✅ PYTHON FILE EXTENSION PRESERVED!")
                    else:
                        print(f"❌ Wrong extension: {extracted_filename}")
                else:
                    print(f"❌ Extraction failed: {extract_response.text}")
        else:
            print(f"❌ Embedding failed: {response.text}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Test 2: Audio file embedding with filename preservation
    print("\n2. Testing document (.docx) embedding in audio...")
    try:
        # Create a simple docx-like content
        with open("test_document.docx", "wb") as f:
            f.write(b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00")  # ZIP signature for docx
            f.write(b"This is test document content for steganography testing.")
        
        if os.path.exists("test_audio.wav"):
            with open("test_audio.wav", "rb") as audio, open("test_document.docx", "rb") as doc:
                response = requests.post(f"{base_url}/api/embed", files={
                    "carrier_file": audio,
                    "content_file": doc
                }, data={
                    "carrier_type": "audio",
                    "content_type": "file", 
                    "password": "test123"
                })
            
            if response.status_code == 200:
                print("✅ Document embedding successful!")
                
                # Extract and verify
                result = response.json()
                if 'output_file' in result:
                    with open(result['output_file'], 'rb') as stego_file:
                        extract_response = requests.post(f"{base_url}/api/extract", files={
                            "stego_file": stego_file
                        }, data={
                            "carrier_type": "audio",
                            "password": "test123"
                        })
                    
                    if extract_response.status_code == 200:
                        extract_result = extract_response.json()
                        extracted_filename = extract_result.get('filename', 'unknown')
                        print(f"✅ Extraction successful! Filename: {extracted_filename}")
                        
                        if extracted_filename.endswith('.docx'):
                            print("✅ DOCUMENT FILE EXTENSION PRESERVED!")
                        else:
                            print(f"❌ Wrong extension: {extracted_filename}")
                    else:
                        print(f"❌ Extraction failed: {extract_response.text}")
            else:
                print(f"❌ Embedding failed: {response.text}")
        else:
            print("❌ No test audio file available")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Test 3: Error message testing - try to embed oversized content
    print("\n3. Testing user-friendly error messages...")
    try:
        # Create a large file that won't fit in a small image
        large_content = "X" * 100000  # 100KB of data
        with open("large_test_file.txt", "w") as f:
            f.write(large_content)
        
        # Use small test image
        if os.path.exists("test_image.png"):
            with open("test_image.png", "rb") as img, open("large_test_file.txt", "rb") as large_file:
                response = requests.post(f"{base_url}/api/embed", files={
                    "carrier_file": img,
                    "content_file": large_file
                }, data={
                    "carrier_type": "image",
                    "content_type": "file",
                    "password": "test123"
                })
            
            if response.status_code != 200:
                error_msg = response.json().get('detail', 'Unknown error')
                print(f"Expected error received: {error_msg}")
                
                # Check if error message is user-friendly
                if any(phrase in error_msg.lower() for phrase in ['too large', 'not enough space', 'file is too small']):
                    print("✅ USER-FRIENDLY ERROR MESSAGE!")
                else:
                    print(f"❌ Technical error message: {error_msg}")
            else:
                print("❌ Expected error but embedding succeeded")
    except Exception as e:
        print(f"❌ Error test failed: {e}")
    
    # Test 4: Video steganography (should work perfectly)
    print("\n4. Testing video steganography...")
    try:
        video_files = ["test_video.mp4", "clean_carrier.mp4", "comprehensive_test_video.mp4"]
        video_file = None
        for vf in video_files:
            if os.path.exists(vf):
                video_file = vf
                break
        
        if video_file:
            with open("test_python_file.py", "w") as f:
                f.write("# Video Test Python File\nprint('Hello from video steganography!')\n")
            
            with open(video_file, "rb") as video, open("test_python_file.py", "rb") as py_file:
                response = requests.post(f"{base_url}/api/embed", files={
                    "carrier_file": video,
                    "content_file": py_file
                }, data={
                    "carrier_type": "video",
                    "content_type": "file",
                    "password": "test123"
                })
            
            if response.status_code == 200:
                print("✅ Video embedding successful!")
                
                result = response.json()
                if 'output_file' in result:
                    with open(result['output_file'], 'rb') as stego_file:
                        extract_response = requests.post(f"{base_url}/api/extract", files={
                            "stego_file": stego_file
                        }, data={
                            "carrier_type": "video",
                            "password": "test123"
                        })
                    
                    if extract_response.status_code == 200:
                        extract_result = extract_response.json()
                        extracted_filename = extract_result.get('filename', 'unknown')
                        print(f"✅ Video extraction successful! Filename: {extracted_filename}")
                        
                        if extracted_filename.endswith('.py'):
                            print("✅ VIDEO PYTHON FILE EXTENSION PRESERVED!")
                        else:
                            print(f"❌ Wrong extension: {extracted_filename}")
                    else:
                        print(f"❌ Video extraction failed: {extract_response.text}")
            else:
                print(f"❌ Video embedding failed: {response.text}")
        else:
            print("❌ No test video file available")
    except Exception as e:
        print(f"❌ Video test error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST SUMMARY:")
    print("- All file types should preserve original extensions")
    print("- Error messages should be user-friendly") 
    print("- No more 'bool' object encoding errors")
    print("- Documents should not become ZIP files")
    print("=" * 60)

if __name__ == "__main__":
    test_file_steganography()