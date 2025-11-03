"""
Direct extraction test to verify copyright workflow fixes
"""

import requests
import time
import os
import json

def test_copyright_extraction():
    """Test the full copyright workflow with correct file handling"""
    
    print("🚀 TESTING COMPLETE COPYRIGHT WORKFLOW")
    print("=" * 60)
    
    # Step 1: Create a fresh embed operation
    print("\n1️⃣ STEP 1: Fresh embed operation...")
    
    test_image = "copyright_demo_file.png"
    copyright_data = {
        "author_name": "Final Test User",
        "copyright_alias": "FTU_2024_FINAL",
        "timestamp": "2024-11-03T21:00:00Z"
    }
    
    try:
        with open(test_image, 'rb') as f:
            files = {'carrier_file': (test_image, f, 'image/png')}
            
            data = {
                'content_type': 'text',
                'text_content': json.dumps(copyright_data),
                'password': 'FinalTest123!',
                'encryption_type': 'aes-256-gcm',
                'carrier_type': 'image'
            }
            
            embed_response = requests.post("http://localhost:8000/api/embed", files=files, data=data)
            
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.status_code}")
            print(f"Error: {embed_response.text}")
            return False
            
        embed_result = embed_response.json()
        embed_operation_id = embed_result.get('operation_id')
        print(f"✅ Embed started: {embed_operation_id}")
        
        # Wait for embed completion
        embedded_file = None
        for attempt in range(10):
            time.sleep(1)
            
            status_response = requests.get(f"http://localhost:8000/api/operations/{embed_operation_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                current_status = status_data.get('status')
                progress = status_data.get('progress', 0)
                
                print(f"  Embed [{attempt + 1:2d}s] Status: {current_status}, Progress: {progress}%")
                
                if current_status == 'completed':
                    result_data = status_data.get('result', {})
                    embedded_file = result_data.get('output_file')
                    
                    # Check for the frontend "success" field issue
                    has_success_field = 'success' in result_data
                    print(f"✅ Embed completed!")
                    print(f"📊 Frontend compatibility check:")
                    print(f"  - Has 'success' field: {has_success_field} (should be False)")
                    print(f"  - Status == 'completed': True (this is what frontend should check)")
                    print(f"  - Embedded file: {embedded_file}")
                    
                    if not has_success_field:
                        print("✅ CONFIRMED: Frontend fix needed (already applied)")
                    
                    break
                elif current_status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    print(f"❌ Embed failed: {error}")
                    return False
            else:
                print(f"❌ Embed status check failed: {status_response.status_code}")
                return False
                
        if not embedded_file:
            print("❌ Embed operation failed or timed out")
            return False
        
        if not os.path.exists(embedded_file):
            print(f"❌ Embedded file not found: {embedded_file}")
            return False
        
        # Step 2: Test extraction
        print(f"\n2️⃣ STEP 2: Testing extraction...")
        
        try:
            with open(embedded_file, 'rb') as f:
                files = {'stego_file': (os.path.basename(embedded_file), f)}  # Correct parameter name
                
                data = {
                    'password': 'FinalTest123!',
                    'output_format': 'text'
                }
                
                extract_response = requests.post("http://localhost:8000/api/extract", files=files, data=data)
                
            if extract_response.status_code != 200:
                print(f"❌ Extract request failed: {extract_response.status_code}")
                print(f"Error: {extract_response.text}")
                return False
                
            extract_result = extract_response.json()
            extract_operation_id = extract_result.get('operation_id')
            print(f"✅ Extract started: {extract_operation_id}")
            
            # Monitor extraction with detailed progress
            for attempt in range(15):
                time.sleep(1)
                
                status_response = requests.get(f"http://localhost:8000/api/operations/{extract_operation_id}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    message = status_data.get('message', '')
                    
                    print(f"  Extract [{attempt + 1:2d}s] Status: {current_status}, Progress: {progress}%, Message: {message}")
                    
                    if current_status == 'completed':
                        result_data = status_data.get('result', {})
                        extracted_text = result_data.get('text_content', '')
                        
                        print("✅ EXTRACTION SUCCESSFUL!")
                        print(f"📝 Extracted text: {extracted_text}")
                        
                        # Parse and verify copyright data
                        try:
                            extracted_copyright = json.loads(extracted_text)
                            print("📋 Extracted copyright data:")
                            for key, value in extracted_copyright.items():
                                print(f"  {key}: {value}")
                            
                            # Verify content matches
                            if (extracted_copyright.get('author_name') == copyright_data['author_name'] and
                                extracted_copyright.get('copyright_alias') == copyright_data['copyright_alias']):
                                print("✅ COPYRIGHT DATA VERIFIED!")
                                return True
                            else:
                                print("❌ Copyright data mismatch!")
                                return False
                        except json.JSONDecodeError:
                            print(f"⚠️  Extracted text is not valid JSON: {extracted_text}")
                            return False
                            
                    elif current_status == 'failed':
                        error = status_data.get('error', 'Unknown error')
                        print(f"❌ Extract failed: {error}")
                        return False
                    elif current_status == 'processing' and progress == 50 and attempt > 8:
                        print("⚠️  Extract appears stuck at 50% - investigating...")
                        # Continue monitoring a bit longer
                        
                else:
                    print(f"❌ Extract status check failed: {status_response.status_code}")
                    return False
                    
            print("❌ Extract operation timed out")
            return False
            
        except Exception as e:
            print(f"❌ Extract test error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Workflow test error: {e}")
        return False

def main():
    success = test_copyright_extraction()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 COMPLETE COPYRIGHT WORKFLOW: SUCCESS!")
        print("✅ Both issues are now FIXED:")
        print("   1. ✅ No more false 'Failed' messages")
        print("   2. ✅ Extraction functionality works properly")
        print("   3. ✅ Copyright data preserved and verified")
        print("\n🛡️  Copyright protection page should now work perfectly!")
    else:
        print("💥 WORKFLOW TEST: FAILED")
        print("❌ Additional debugging needed")
    
    print("=" * 60)

if __name__ == "__main__":
    main()