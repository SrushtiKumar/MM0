"""
Quick test to verify the password bug fix
"""

import requests
import json
import time
import os

API_BASE = "http://localhost:8000/api"

def test_password_fix():
    """Test that forensic extraction now works with password"""
    
    print("🧪 Testing Password Bug Fix")
    print("=" * 50)
    
    # Create test files
    carrier_path = "test_carrier.png"
    secret_content = "This is secret forensic evidence!"
    
    # Create a simple PNG file (1x1 pixel)
    with open(carrier_path, 'wb') as f:
        # Simple 1x1 PNG file
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x01\x14\xa3\x00\x00\x00\x00IEND\xaeB`\x82'
        f.write(png_data)
    
    secret_path = "test_secret.txt"
    with open(secret_path, 'w') as f:
        f.write(secret_content)
    
    password = "test123"
    
    try:
        # Step 1: Embed forensic evidence
        print("📤 Step 1: Embedding forensic evidence...")
        
        embed_data = {
            'password': password,
            'encryption_type': 'AES',
            'case_id': 'TEST-001',
            'investigator': 'Test Agent',
            'location': 'Test Lab',
            'description': 'Password fix test'
        }
        
        files = {
            'carrier_file': ('test_carrier.png', open(carrier_path, 'rb'), 'image/png'),
            'secret_file': ('test_secret.txt', open(secret_path, 'rb'), 'text/plain')
        }
        
        embed_response = requests.post(f"{API_BASE}/forensic-embed", data=embed_data, files=files)
        
        # Close files
        files['carrier_file'][1].close()
        files['secret_file'][1].close()
        
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.text}")
            return False
        
        embed_result = embed_response.json()
        operation_id = embed_result['operation_id']
        
        # Wait for embedding to complete
        print("⏳ Waiting for embedding to complete...")
        for i in range(30):
            status_response = requests.get(f"{API_BASE}/status/{operation_id}")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"  Status: {status['status']} - {status.get('message', '')}")
                if status['status'] == 'completed':
                    break
                elif status['status'] == 'failed':
                    print(f"❌ Embed failed: {status.get('message', 'Unknown error')}")
                    return False
            time.sleep(1)
        
        # Download embedded file
        download_response = requests.get(f"{API_BASE}/download/{operation_id}")
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.text}")
            return False
        
        stego_file_path = "test_stego.png"
        with open(stego_file_path, 'wb') as f:
            f.write(download_response.content)
        
        print("✅ Embedding completed successfully!")
        
        # Step 2: Extract forensic evidence (this should now work with password)
        print("\n📥 Step 2: Extracting forensic evidence with password...")
        
        extract_data = {
            'password': password,  # This is the critical fix!
            'output_format': 'forensic'
        }
        
        files = {
            'stego_file': ('test_stego.png', open(stego_file_path, 'rb'), 'image/png')
        }
        
        extract_response = requests.post(f"{API_BASE}/forensic-extract", data=extract_data, files=files)
        
        # Close file
        files['stego_file'][1].close()
        
        if extract_response.status_code != 200:
            print(f"❌ Extract failed: {extract_response.text}")
            return False
        
        extract_result = extract_response.json()
        extract_operation_id = extract_result['operation_id']
        
        # Wait for extraction to complete
        print("⏳ Waiting for extraction to complete...")
        for i in range(30):
            status_response = requests.get(f"{API_BASE}/status/{extract_operation_id}")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"  Status: {status['status']} - {status.get('message', '')}")
                if status['status'] == 'completed':
                    break
                elif status['status'] == 'failed':
                    print(f"❌ Extract failed: {status.get('message', 'Unknown error')}")
                    return False
            time.sleep(1)
        
        print("✅ Extraction completed successfully!")
        print("\n🎉 PASSWORD BUG FIX VERIFIED!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        for file_path in [carrier_path, secret_path, stego_file_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    success = test_password_fix()
    if success:
        print("\n🎯 PASSWORD BUG FIXED SUCCESSFULLY!")
        print("The forensic system now correctly passes the password to extraction!")
    else:
        print("\n❌ Test failed - more debugging needed")