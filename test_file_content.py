#!/usr/bin/env python3
"""
Test file download to check actual content
"""

import requests
import time

API_BASE = "http://localhost:8000/api"

def test_file_content():
    """Test what's actually in the extracted file"""
    
    print("=== FILE CONTENT TEST ===\n")
    
    test_content = "Test message for verification"
    
    try:
        # Quick embed
        with open("debug_embedded.png", 'rb') as carrier_file:
            files = {'carrier_file': carrier_file}
            data = {
                'password': 'test123',
                'carrier_type': 'image',
                'content_type': 'text',
                'text_content': test_content
            }
            
            embed_response = requests.post(f"{API_BASE}/embed", files=files, data=data)
            if embed_response.status_code == 200:
                embed_result = embed_response.json()
                output_filename = embed_result.get('output_filename')
                
                # Download and extract
                download_response = requests.get(f"{API_BASE}/download/{output_filename}")
                if download_response.status_code == 200:
                    temp_file = "temp_content_test.png"
                    with open(temp_file, 'wb') as f:
                        f.write(download_response.content)
                    
                    # Extract
                    with open(temp_file, 'rb') as stego_file:
                        extract_files = {'stego_file': stego_file}
                        extract_data = {'password': 'test123', 'carrier_type': 'image', 'output_format': 'preserve'}
                        
                        extract_response = requests.post(f"{API_BASE}/extract", files=extract_files, data=extract_data)
                        if extract_response.status_code == 200:
                            extract_result = extract_response.json()
                            extract_op_id = extract_result.get('operation_id')
                            
                            time.sleep(2)
                            
                            # Get extracted filename
                            status_response = requests.get(f"{API_BASE}/operations/{extract_op_id}/status")
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                result = status_data.get('result', {})
                                extracted_filename = result.get('filename')
                                
                                print(f"Extracted filename: {extracted_filename}")
                                
                                # Download the extracted file
                                if extracted_filename:
                                    file_response = requests.get(f"{API_BASE}/download/{extracted_filename}")
                                    if file_response.status_code == 200:
                                        print(f"Original content: {repr(test_content)}")
                                        print(f"File content (text): {repr(file_response.text)}")
                                        print(f"File content (bytes): {repr(file_response.content)}")
                                        
                                        # Check if bytes are valid UTF-8
                                        try:
                                            decoded = file_response.content.decode('utf-8')
                                            print(f"Decoded UTF-8: {repr(decoded)}")
                                            
                                            if decoded == test_content:
                                                print("✅ Content matches after decoding!")
                                            else:
                                                print("❌ Content does not match")
                                        except UnicodeDecodeError as e:
                                            print(f"❌ Cannot decode as UTF-8: {e}")
                                            
                                        # Check printable ratio
                                        content = file_response.content
                                        try:
                                            text = content.decode('utf-8')
                                            printable_chars = sum(1 for c in text if c.isprintable() or c.isspace())
                                            ratio = printable_chars / len(text) if len(text) > 0 else 0
                                            null_bytes = b'\x00' in content[:100]
                                            print(f"Printable ratio: {ratio:.2f}")
                                            print(f"Has null bytes in first 100: {null_bytes}")
                                            print(f"Should be detected as text: {ratio > 0.8 and not null_bytes}")
                                        except:
                                            print("Cannot analyze text characteristics")
                    
                    import os
                    try:
                        os.remove(temp_file)
                    except:
                        pass
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_file_content()