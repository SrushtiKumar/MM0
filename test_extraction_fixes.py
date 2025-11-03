"""
Test extraction with fixed backend error handling to see the actual decryption issue
"""

import requests
import json
import time
import os

def test_extraction_with_fixed_backend():
    """Test extraction with the backend error fix"""
    
    print("🔧 TESTING EXTRACTION WITH BACKEND FIX")
    print("=" * 50)
    
    # Use the embedded file from our previous successful embed
    stego_file = "outputs/stego_carrier_copyright_demo_file_1762181841_825c0614_1762181841_c1032227.png"
    
    if not os.path.exists(stego_file):
        print(f"❌ Stego file not found: {stego_file}")
        return False
    
    try:
        print(f"📁 Using stego file: {stego_file}")
        print(f"📏 File size: {os.path.getsize(stego_file)} bytes")
        
        with open(stego_file, 'rb') as f:
            files = {'stego_file': (os.path.basename(stego_file), f)}
            
            # Try with the same password used for embedding
            data = {
                'password': 'WorkflowTest123!',
                'output_format': 'text'
            }
            
            response = requests.post("http://localhost:8000/api/extract", files=files, data=data)
            
        if response.status_code != 200:
            print(f"❌ Extract request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        result = response.json()
        operation_id = result.get('operation_id')
        print(f"✅ Extract operation started: {operation_id}")
        
        # Wait for completion and check for proper error handling
        for attempt in range(20):
            time.sleep(1)
            
            status_response = requests.get(f"http://localhost:8000/api/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                current_status = status_data.get('status')
                progress = status_data.get('progress', 0)
                message = status_data.get('message', '')
                error = status_data.get('error')
                
                print(f"  Attempt {attempt + 1}: Status={current_status}, Progress={progress}%, Message='{message}'")
                
                if current_status == 'completed':
                    print("✅ Extraction completed!")
                    result_data = status_data.get('result', {})
                    print("📄 Result:")
                    print(json.dumps(result_data, indent=2))
                    return True
                    
                elif current_status == 'failed':
                    print(f"❌ Extraction failed with proper error: {error}")
                    print("✅ Backend error handling now works properly!")
                    
                    # Let's try with different passwords to see if that's the issue
                    print("\n🔍 TESTING DIFFERENT PASSWORDS...")
                    
                    test_passwords = [
                        'WorkflowTest123!',  # Original
                        'FinalTest123!',     # Different test password
                        '',                  # Empty password
                        'password',          # Simple password
                    ]
                    
                    for test_pwd in test_passwords:
                        print(f"\n  Testing password: '{test_pwd}'")
                        try:
                            with open(stego_file, 'rb') as f:
                                files = {'stego_file': (os.path.basename(stego_file), f)}
                                data = {'password': test_pwd, 'output_format': 'text'}
                                test_response = requests.post("http://localhost:8000/api/extract", files=files, data=data)
                            
                            if test_response.status_code == 200:
                                test_result = test_response.json()
                                test_op_id = test_result.get('operation_id')
                                
                                # Quick check on this operation
                                time.sleep(3)
                                test_status_response = requests.get(f"http://localhost:8000/api/operations/{test_op_id}/status")
                                if test_status_response.status_code == 200:
                                    test_status_data = test_status_response.json()
                                    test_status = test_status_data.get('status')
                                    if test_status == 'completed':
                                        print(f"    ✅ SUCCESS with password: '{test_pwd}'!")
                                        extracted_data = test_status_data.get('result', {})
                                        print(f"    📄 Extracted: {json.dumps(extracted_data, indent=4)}")
                                        return True
                                    else:
                                        print(f"    ❌ Status: {test_status}")
                                        
                        except Exception as e:
                            print(f"    ❌ Error testing password '{test_pwd}': {e}")
                    
                    return False
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
        
        print("❌ Extraction timed out")
        return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_extraction_with_fixed_backend()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 EXTRACTION TEST: SUCCESS!")
        print("✅ Backend error handling works")
        print("✅ Extraction functionality works")
    else:
        print("💥 EXTRACTION TEST: ISSUES REMAIN")
        print("❌ Need to investigate decryption/password issue")
    print("=" * 50)