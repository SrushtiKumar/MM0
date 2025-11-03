"""
Final verification test for copyright page issues resolution
Tests both database error handling and download filename fixes
"""

import requests
import json
import time
import os

API_URL = "http://localhost:8000/api"

def test_copyright_fixes():
    """Test that all copyright page issues have been resolved"""
    print("🔍 FINAL COPYRIGHT ISSUES VERIFICATION TEST")
    print("=" * 60)
    
    test_image = "copyright_demo_file.png"
    
    if not os.path.exists(test_image):
        print(f"❌ Test image {test_image} not found")
        return False
    
    # Test 1: Supported formats loading
    print("\n1️⃣ Testing supported formats loading...")
    try:
        formats_response = requests.get(f"{API_URL}/supported-formats")
        if formats_response.status_code == 200:
            formats = formats_response.json()
            if 'image' in formats and 'carrier_formats' in formats['image']:
                print("✅ Supported formats load correctly")
            else:
                print("❌ Supported formats structure incorrect")
                return False
        else:
            print(f"❌ Supported formats request failed: {formats_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Supported formats test error: {e}")
        return False
    
    # Test 2: Copyright embedding with proper error handling
    print("\n2️⃣ Testing copyright embedding (with database error handling)...")
    
    copyright_data = {
        "author_name": "Final Verification Test",
        "copyright_alias": "FVT_2024",
        "timestamp": "2024-11-03T17:00:00Z"
    }
    
    try:
        with open(test_image, 'rb') as f:
            files = {'carrier_file': (test_image, f, 'image/png')}
            
            data = {
                'content_type': 'text',
                'text_content': json.dumps(copyright_data),
                'password': 'FinalTest123!',
                'encryption_type': 'aes-256-gcm',
                'carrier_type': 'image',
                'user_id': 'nonexistent_user_id_12345'  # This will trigger database error
            }
            
            embed_response = requests.post(f"{API_URL}/embed", files=files, data=data)
            
        if embed_response.status_code == 200:
            print("✅ Embedding successful despite database error")
            
            embed_result = embed_response.json()
            operation_id = embed_result.get('operation_id')
            
            if operation_id:
                print(f"✅ Got operation ID: {operation_id}")
                
                # Wait for completion
                for attempt in range(10):
                    time.sleep(1)
                    
                    status_response = requests.get(f"{API_URL}/operations/{operation_id}/status")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        current_status = status_data.get('status')
                        
                        if current_status == 'completed':
                            result_data = status_data.get('result', {})
                            print("✅ Operation completed successfully")
                            
                            # Test 3: Download with correct filename
                            print("\n3️⃣ Testing download with correct filename...")
                            
                            filename = result_data.get('filename', 'unknown')
                            print(f"📁 Result filename: {filename}")
                            
                            if filename.lower().endswith('.png'):
                                print("✅ Filename has correct .png extension")
                                
                                # Test actual download
                                download_response = requests.get(f"{API_URL}/operations/{operation_id}/download")
                                
                                if download_response.status_code == 200:
                                    content_disposition = download_response.headers.get('Content-Disposition', '')
                                    content_type = download_response.headers.get('Content-Type', '')
                                    
                                    print(f"📥 Content-Type: {content_type}")
                                    
                                    if 'filename=' in content_disposition:
                                        server_filename = content_disposition.split('filename=')[1].strip('"')
                                        print(f"🏷️ Server filename: {server_filename}")
                                        
                                        if server_filename.lower().endswith('.png'):
                                            print("✅ Download filename has correct extension")
                                            
                                            if content_type == 'image/png':
                                                print("✅ Download content-type is correct")
                                                return True
                                            else:
                                                print(f"❌ Wrong content-type: {content_type}")
                                                return False
                                        else:
                                            print(f"❌ Download filename has wrong extension: {server_filename}")
                                            return False
                                    else:
                                        print("❌ No filename in Content-Disposition")
                                        return False
                                else:
                                    print(f"❌ Download failed: {download_response.status_code}")
                                    return False
                            else:
                                print(f"❌ Wrong filename extension: {filename}")
                                return False
                                
                        elif current_status == 'failed':
                            error = status_data.get('error', 'Unknown error')
                            print(f"❌ Operation failed: {error}")
                            return False
                    else:
                        print(f"❌ Status check failed: {status_response.status_code}")
                        return False
                        
                print("⏰ Operation timed out")
                return False
            else:
                print("❌ No operation ID received")
                return False
        else:
            print(f"❌ Embedding failed: {embed_response.status_code}")
            print(f"Error: {embed_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Run final verification"""
    success = test_copyright_fixes()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL COPYRIGHT ISSUES RESOLVED!")
        print("✅ Database error handling: Working")
        print("✅ Supported formats loading: Working")
        print("✅ Copyright embedding: Working")
        print("✅ Download filename: Correct (.png)")
        print("✅ Download content-type: Correct")
        print("\n📢 Users will no longer see:")
        print("   • 'Supported formats not loaded' errors")
        print("   • Database constraint violation messages")
        print("   • .xip file downloads")
        print("   • 'Failed' status for successful operations")
    else:
        print("💥 SOME ISSUES REMAIN")
        print("❌ Additional fixes may be needed")
    
    print("=" * 60)

if __name__ == "__main__":
    main()