"""
Focused Verification Test - Core Fixes
Tests the main issues that were reported and fixed
"""
import requests
import json
import os

def verify_core_fixes():
    print("🔧 VERIFYING CORE FIXES")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Fix 1: Python files should preserve .py extension (not become .txt)
    print("\n✅ Fix 1: Python file extension preservation")
    print("-" * 40)
    
    # Create test python file
    with open("test_script.py", "w") as f:
        f.write("""#!/usr/bin/env python3
# Test Python Script for Steganography
import os
import sys

def main():
    print("This is a test Python script!")
    print("It should extract with .py extension, not .txt")
    
if __name__ == "__main__":
    main()
""")
    
    # Test with audio (where the issue was most prominent)
    try:
        with open("test_audio.wav", "rb") as audio, open("test_script.py", "rb") as py_file:
            embed_response = requests.post(f"{base_url}/api/embed", files={
                "carrier_file": audio,
                "content_file": py_file
            }, data={
                "carrier_type": "audio",
                "content_type": "file",
                "password": "test123"
            })
        
        if embed_response.status_code == 200:
            result = embed_response.json()
            print("✅ Python file embedded successfully in audio")
            
            # Extract and check filename
            stego_file = result.get('output_file')
            if stego_file and os.path.exists(stego_file):
                with open(stego_file, "rb") as f:
                    extract_response = requests.post(f"{base_url}/api/extract", files={
                        "stego_file": f
                    }, data={
                        "carrier_type": "audio",
                        "password": "test123"
                    })
                
                if extract_response.status_code == 200:
                    extract_result = extract_response.json()
                    extracted_filename = extract_result.get('filename', 'unknown')
                    print(f"📄 Extracted filename: {extracted_filename}")
                    
                    if extracted_filename.endswith('.py'):
                        print("🎯 SUCCESS: Python file keeps .py extension!")
                    elif extracted_filename.endswith('.txt'):
                        print("❌ FAILED: File became .txt (old bug)")
                    else:
                        print(f"❓ Unexpected extension: {extracted_filename}")
                else:
                    print(f"❌ Extraction failed: {extract_response.json()}")
            else:
                print("❌ No output file created")
        else:
            print(f"❌ Embedding failed: {embed_response.json()}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Fix 2: No more 'bool' object encoding errors
    print("\n✅ Fix 2: No 'bool' object encoding errors")
    print("-" * 40)
    
    try:
        with open("test_image.png", "rb") as img, open("test_script.py", "rb") as py_file:
            embed_response = requests.post(f"{base_url}/api/embed", files={
                "carrier_file": img,
                "content_file": py_file
            }, data={
                "carrier_type": "image",
                "content_type": "file",
                "password": "test123"
            })
        
        if embed_response.status_code == 200:
            print("🎯 SUCCESS: No 'bool' object encoding error!")
        else:
            error_msg = embed_response.json().get('detail', 'Unknown error')
            if "'bool' object has no attribute 'encode'" in error_msg:
                print("❌ FAILED: Still getting bool encoding error")
            else:
                print(f"❓ Different error: {error_msg}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Fix 3: Documents should not become ZIP files
    print("\n✅ Fix 3: Document files preserve correct format")
    print("-" * 40)
    
    # Create a simple document-like file
    doc_content = """
    This is a test document for steganography.
    It should maintain its original format when extracted.
    Document Type: Test Document
    Content: Sample text for testing purposes.
    """
    
    with open("test_doc.docx", "w", encoding='utf-8') as f:
        f.write(doc_content)
    
    try:
        with open("test_audio.wav", "rb") as audio, open("test_doc.docx", "rb") as doc:
            embed_response = requests.post(f"{base_url}/api/embed", files={
                "carrier_file": audio,
                "content_file": doc
            }, data={
                "carrier_type": "audio",
                "content_type": "file",
                "password": "test123"
            })
        
        if embed_response.status_code == 200:
            result = embed_response.json()
            print("✅ Document file embedded successfully")
            
            # Extract and check
            stego_file = result.get('output_file')
            if stego_file and os.path.exists(stego_file):
                with open(stego_file, "rb") as f:
                    extract_response = requests.post(f"{base_url}/api/extract", files={
                        "stego_file": f
                    }, data={
                        "carrier_type": "audio",
                        "password": "test123"
                    })
                
                if extract_response.status_code == 200:
                    extract_result = extract_response.json()
                    extracted_filename = extract_result.get('filename', 'unknown')
                    print(f"📄 Extracted filename: {extracted_filename}")
                    
                    if extracted_filename.endswith('.docx'):
                        print("🎯 SUCCESS: Document keeps .docx extension!")
                    elif extracted_filename.endswith('.zip'):
                        print("❌ FAILED: Document became .zip (old bug)")
                    else:
                        print(f"❓ Unexpected extension: {extracted_filename}")
                        
                    # Check if we can read the content
                    output_file = extract_result.get('output_file')
                    if output_file and os.path.exists(output_file):
                        try:
                            with open(output_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if "This is a test document" in content:
                                    print("🎯 SUCCESS: Document content preserved!")
                                else:
                                    print("❓ Content may have changed")
                        except:
                            print("❓ Could not read extracted content as text")
                else:
                    print(f"❌ Extraction failed: {extract_response.json()}")
        else:
            print(f"❌ Embedding failed: {embed_response.json()}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 40)
    print("🏁 CORE FIXES VERIFICATION COMPLETE")
    print("=" * 40)

if __name__ == "__main__":
    verify_core_fixes()