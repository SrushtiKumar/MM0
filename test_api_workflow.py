"""
Test Complete API Workflow - Embedding and Extracting Files
Test to verify that files maintain their content through the complete API process
"""
import requests
import os
import tempfile
import time
import json

def test_complete_api_workflow():
    print("🔧 TESTING COMPLETE API WORKFLOW")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Python file through complete API workflow  
    print("\n1. Testing Python file through API...")
    
    # Create test Python file
    python_content = '''#!/usr/bin/env python3
"""
Test Python File for API Steganography Testing
This file tests whether Python files maintain their content
through the complete embedding and extraction process.
"""

import os
import sys

def main():
    print("Hello from the embedded Python file!")
    print("This file should maintain its exact content.")
    
    # Test various Python features
    data = {"key": "value", "number": 42}
    
    for i in range(3):
        print(f"Loop iteration: {i}")
    
    return "Success!"

if __name__ == "__main__":
    result = main()
    print(f"Result: {result}")
'''
    
    with open("api_test_python.py", "w", encoding='utf-8') as f:
        f.write(python_content)
    
    # Create test carrier image
    print("📁 Creating test carrier image...")
    with open("api_test_image.png", "wb") as f:
        # Simple PNG header and data
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10')
        f.write(b'\x08\x02\x00\x00\x00\x90wS\xde' + b'\\x00' * 100)
        f.write(b'\x00\x00\x00\x00IEND\xaeB`\x82')
    
    try:
        # Step 1: Embed using API
        print("📥 Step 1: Embedding Python file via API...")
        
        with open("api_test_image.png", "rb") as carrier, open("api_test_python.py", "rb") as content:
            embed_response = requests.post(f"{base_url}/api/embed", 
                files={
                    "carrier_file": carrier,
                    "content_file": content
                },
                data={
                    "carrier_type": "image",
                    "content_type": "file", 
                    "password": "test123"
                }
            )
        
        if embed_response.status_code == 200:
            embed_result = embed_response.json()
            print("✅ Embed API call successful")
            print(f"📋 Operation ID: {embed_result.get('operation_id')}")
            
            # Step 2: Wait for embedding to complete and get result
            operation_id = embed_result.get('operation_id')
            if operation_id:
                print("⏳ Waiting for embedding to complete...")
                
                for attempt in range(30):  # Wait up to 30 seconds
                    status_response = requests.get(f"{base_url}/api/status/{operation_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"📊 Status: {status_data.get('status')} - {status_data.get('message')}")
                        
                        if status_data.get('status') == 'completed':
                            result = status_data.get('result', {})
                            stego_file_path = result.get('output_file')
                            
                            if stego_file_path and os.path.exists(stego_file_path):
                                print(f"✅ Embedding completed! Stego file: {stego_file_path}")
                                
                                # Step 3: Extract using API
                                print("📤 Step 3: Extracting via API...")
                                
                                with open(stego_file_path, "rb") as stego_file:
                                    extract_response = requests.post(f"{base_url}/api/extract",
                                        files={
                                            "stego_file": stego_file
                                        },
                                        data={
                                            "password": "test123",
                                            "output_format": "auto"
                                        }
                                    )
                                
                                if extract_response.status_code == 200:
                                    extract_result = extract_response.json()
                                    extract_operation_id = extract_result.get('operation_id')
                                    print(f"✅ Extract API call successful: {extract_operation_id}")
                                    
                                    # Step 4: Wait for extraction to complete
                                    print("⏳ Waiting for extraction to complete...")
                                    
                                    for extract_attempt in range(20):
                                        extract_status_response = requests.get(f"{base_url}/api/status/{extract_operation_id}")
                                        if extract_status_response.status_code == 200:
                                            extract_status_data = extract_status_response.json()
                                            print(f"📊 Extract Status: {extract_status_data.get('status')} - {extract_status_data.get('message')}")
                                            
                                            if extract_status_data.get('status') == 'completed':
                                                extract_result_data = extract_status_data.get('result', {})
                                                extracted_file_path = extract_result_data.get('output_file')
                                                extracted_filename = extract_result_data.get('filename')
                                                
                                                print(f"✅ Extraction completed!")
                                                print(f"📄 Extracted file: {extracted_file_path}")
                                                print(f"📝 Extracted filename: {extracted_filename}")
                                                
                                                # Step 5: Verify content
                                                print("🔍 Step 5: Verifying content integrity...")
                                                
                                                if extracted_file_path and os.path.exists(extracted_file_path):
                                                    # Check filename preservation
                                                    if extracted_filename == "api_test_python.py":
                                                        print("✅ FILENAME PRESERVED CORRECTLY!")
                                                    else:
                                                        print(f"⚠️  Filename changed: {extracted_filename}")
                                                    
                                                    # Check content preservation
                                                    try:
                                                        with open(extracted_file_path, "r", encoding='utf-8') as f:
                                                            extracted_content = f.read()
                                                        
                                                        print(f"📏 Original content length: {len(python_content)}")
                                                        print(f"📏 Extracted content length: {len(extracted_content)}")
                                                        
                                                        # Show a preview of extracted content
                                                        print("📋 Extracted content preview:")
                                                        print("-" * 40)
                                                        print(extracted_content[:300] + "..." if len(extracted_content) > 300 else extracted_content)
                                                        print("-" * 40)
                                                        
                                                        # Compare content
                                                        if extracted_content.strip() == python_content.strip():
                                                            print("🎯 SUCCESS: CONTENT PERFECTLY PRESERVED!")
                                                        else:
                                                            print("❌ FAILED: Content differs!")
                                                            print("Checking for byte differences...")
                                                            
                                                            original_bytes = python_content.encode('utf-8')
                                                            extracted_bytes = extracted_content.encode('utf-8') 
                                                            
                                                            if original_bytes == extracted_bytes:
                                                                print("✅ Byte-level comparison successful!")
                                                            else:
                                                                print(f"❌ Byte differences found!")
                                                                print(f"Original first 100 bytes: {original_bytes[:100]}")
                                                                print(f"Extracted first 100 bytes: {extracted_bytes[:100]}")
                                                        
                                                    except Exception as e:
                                                        print(f"❌ Failed to read extracted file as text: {e}")
                                                        
                                                        # Try reading as binary
                                                        try:
                                                            with open(extracted_file_path, "rb") as f:
                                                                extracted_binary = f.read()
                                                            
                                                            print(f"📄 File contains {len(extracted_binary)} bytes of binary data")
                                                            print(f"🔍 First 100 bytes: {extracted_binary[:100]}")
                                                            
                                                            # Check if it's actually UTF-8 text
                                                            try:
                                                                decoded = extracted_binary.decode('utf-8')
                                                                print("📝 Binary data is valid UTF-8 text:")
                                                                print(decoded[:200] + "..." if len(decoded) > 200 else decoded)
                                                                
                                                                if decoded.strip() == python_content.strip():
                                                                    print("🎯 SUCCESS: Content preserved (was saved as binary)!")
                                                                else:
                                                                    print("❌ Content differs even after decoding")
                                                                    
                                                            except UnicodeDecodeError:
                                                                print("❌ Binary data is not valid UTF-8")
                                                                
                                                        except Exception as e2:
                                                            print(f"❌ Failed to read as binary: {e2}")
                                                else:
                                                    print(f"❌ Extracted file not found: {extracted_file_path}")
                                                
                                                break
                                                
                                            elif extract_status_data.get('status') == 'failed':
                                                print(f"❌ Extraction failed: {extract_status_data.get('message')}")
                                                break
                                        
                                        time.sleep(1)
                                    else:
                                        print("❌ Extraction timeout")
                                else:
                                    print(f"❌ Extract API call failed: {extract_response.status_code} - {extract_response.text}")
                                
                                break
                            else:
                                print(f"❌ Stego file not found: {stego_file_path}")
                                break
                                
                        elif status_data.get('status') == 'failed':
                            print(f"❌ Embedding failed: {status_data.get('message')}")
                            break
                    
                    time.sleep(1)
                else:
                    print("❌ Embedding timeout")
            else:
                print("❌ No operation ID returned")
        else:
            print(f"❌ Embed API call failed: {embed_response.status_code}")
            print(f"Response: {embed_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 COMPLETE API WORKFLOW TEST FINISHED")
    print("=" * 60)

if __name__ == "__main__":
    test_complete_api_workflow()