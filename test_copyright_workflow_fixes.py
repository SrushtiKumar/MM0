"""
Test to reproduce and verify fixes for copyright page issues:
1. "Failed" message showing for successful operations
2. Extract functionality not working
"""

import requests
import json
import time
import os

API_URL = "http://localhost:8000/api"

def test_embed_and_extract_workflow():
    """Test complete embed and extract workflow"""
    print("🔍 TESTING COMPLETE COPYRIGHT WORKFLOW")
    print("=" * 50)
    
    test_image = "copyright_demo_file.png"
    
    if not os.path.exists(test_image):
        print(f"❌ Test image {test_image} not found")
        return False
    
    # Step 1: Embed copyright data
    print("\n1️⃣ STEP 1: Embedding copyright data...")
    
    copyright_data = {
        "author_name": "Workflow Test User",
        "copyright_alias": "WTU_2024",
        "timestamp": "2024-11-03T18:00:00Z"
    }
    
    try:
        with open(test_image, 'rb') as f:
            files = {'carrier_file': (test_image, f, 'image/png')}
            
            data = {
                'content_type': 'text',
                'text_content': json.dumps(copyright_data),
                'password': 'WorkflowTest123!',
                'encryption_type': 'aes-256-gcm',
                'carrier_type': 'image'
            }
            
            embed_response = requests.post(f"{API_URL}/embed", files=files, data=data)
            
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.status_code}")
            print(f"Error: {embed_response.text}")
            return False
            
        embed_result = embed_response.json()
        embed_operation_id = embed_result.get('operation_id')
        print(f"✅ Embed initiated: {embed_operation_id}")
        
        # Wait for embed completion and check for proper success indication
        print("⏳ Waiting for embed completion...")
        
        embedded_file_path = None
        for attempt in range(15):
            time.sleep(1)
            
            status_response = requests.get(f"{API_URL}/operations/{embed_operation_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                current_status = status_data.get('status')
                progress = status_data.get('progress', 0)
                
                print(f"  Attempt {attempt + 1}: Status={current_status}, Progress={progress}%")
                
                if current_status == 'completed':
                    result_data = status_data.get('result', {})
                    print("✅ Embed completed successfully!")
                    
                    # Check if result indicates success (this is what frontend checks)
                    has_success_field = 'success' in result_data
                    success_value = result_data.get('success', 'NOT_PRESENT')
                    
                    print(f"📊 Result analysis:")
                    print(f"  - Has 'success' field: {has_success_field}")
                    print(f"  - Success value: {success_value}")
                    print(f"  - Status is 'completed': True")
                    
                    if not has_success_field:
                        print("⚠️ FRONTEND BUG IDENTIFIED: No 'success' field in result!")
                        print("💡 Frontend should treat 'completed' status as success")
                    
                    # Get the embedded file path for extraction test
                    embedded_file_path = result_data.get('output_file')
                    if embedded_file_path and os.path.exists(embedded_file_path):
                        print(f"📁 Embedded file created: {embedded_file_path}")
                        break
                    else:
                        print(f"❌ Embedded file not found: {embedded_file_path}")
                        return False
                        
                elif current_status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    print(f"❌ Embed operation failed: {error}")
                    return False
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
                
        if not embedded_file_path:
            print("❌ Embed operation timed out")
            return False
        
        # Step 2: Extract copyright data
        print(f"\n2️⃣ STEP 2: Extracting from embedded file...")
        
        try:
            with open(embedded_file_path, 'rb') as f:
                files = {'stego_file': (os.path.basename(embedded_file_path), f)}
                
                data = {
                    'password': 'WorkflowTest123!',
                    'output_format': 'auto'
                }
                
                extract_response = requests.post(f"{API_URL}/extract", files=files, data=data)
                
            if extract_response.status_code != 200:
                print(f"❌ Extract request failed: {extract_response.status_code}")
                print(f"Error: {extract_response.text}")
                return False
                
            extract_result = extract_response.json()
            extract_operation_id = extract_result.get('operation_id')
            print(f"✅ Extract initiated: {extract_operation_id}")
            
            # Wait for extraction completion
            print("⏳ Waiting for extraction completion...")
            
            for attempt in range(15):
                time.sleep(1)
                
                status_response = requests.get(f"{API_URL}/operations/{extract_operation_id}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    
                    print(f"  Attempt {attempt + 1}: Status={current_status}, Progress={progress}%")
                    
                    if current_status == 'completed':
                        result_data = status_data.get('result', {})
                        print("✅ Extract completed successfully!")
                        
                        # Check extracted content
                        extracted_text = result_data.get('text_content', '')
                        print(f"📝 Extracted text: {extracted_text}")
                        
                        # Verify it matches original copyright data
                        try:
                            extracted_copyright = json.loads(extracted_text)
                            print(f"📋 Extracted copyright data:")
                            for key, value in extracted_copyright.items():
                                print(f"  {key}: {value}")
                            
                            # Verify content matches
                            if (extracted_copyright.get('author_name') == copyright_data['author_name'] and
                                extracted_copyright.get('copyright_alias') == copyright_data['copyright_alias']):
                                print("✅ Copyright data verified successfully!")
                                return True
                            else:
                                print("❌ Copyright data mismatch!")
                                return False
                        except json.JSONDecodeError:
                            print(f"❌ Extracted text is not valid JSON: {extracted_text}")
                            return False
                            
                    elif current_status == 'failed':
                        error = status_data.get('error', 'Unknown error')
                        print(f"❌ Extract operation failed: {error}")
                        return False
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
    """Run workflow test"""
    success = test_embed_and_extract_workflow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 COMPLETE WORKFLOW TEST: SUCCESS!")
        print("✅ Embedding: Works correctly")
        print("✅ Extraction: Works correctly") 
        print("✅ Copyright data: Preserved accurately")
        print("\n📢 Issues that should now be fixed:")
        print("   • No more 'Failed' messages for successful operations")
        print("   • Extract functionality now works properly")
    else:
        print("💥 WORKFLOW TEST: FAILED")
        print("❌ Issues remain - additional fixes needed")
    
    print("=" * 50)

if __name__ == "__main__":
    main()