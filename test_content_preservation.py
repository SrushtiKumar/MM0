"""
Test Image/Document Steganography Content Preservation
Debug why extracted content is corrupted
"""
import os
import sys
sys.path.append('.')

from universal_file_steganography import UniversalFileSteganography

def test_content_preservation():
    print("🔧 TESTING CONTENT PRESERVATION")
    print("=" * 50)
    
    # Create test steganography instance
    stego = UniversalFileSteganography()
    
    # Test 1: Simple text content
    print("\n1. Testing simple text content...")
    test_text = "Hello World! This is a test message.\nLine 2: Testing newlines\nLine 3: Special chars: àáâã"
    
    try:
        # Create a simple carrier file
        with open("test_carrier.txt", "w", encoding='utf-8') as f:
            f.write("This is the carrier file content.\nCarrier line 2.")
        
        # Test direct hide_data method call
        print("📥 Hiding text data...")
        result = stego.hide_data(
            carrier_file_path="test_carrier.txt",
            content_to_hide=test_text,
            output_path="test_output_text.txt",
            password=None,
            is_file=False,
            original_filename="test_message.txt"
        )
        print(f"✅ Hide result: {result}")
        
        # Extract the data
        print("📤 Extracting text data...")
        extracted = stego.extract_data("test_output_text.txt", password=None)
        
        if extracted:
            extracted_data, extracted_filename = extracted
            print(f"📄 Extracted filename: {extracted_filename}")
            print(f"📏 Extracted data length: {len(extracted_data)} bytes")
            print(f"📝 Extracted data type: {type(extracted_data)}")
            
            # Try to decode as text
            if isinstance(extracted_data, bytes):
                try:
                    decoded_text = extracted_data.decode('utf-8')
                    print(f"✅ Decoded text: '{decoded_text}'")
                    
                    if decoded_text == test_text:
                        print("🎯 SUCCESS: Text content perfectly preserved!")
                    else:
                        print("❌ FAILED: Text content differs!")
                        print(f"Original: '{test_text}'")
                        print(f"Extracted: '{decoded_text}'")
                except Exception as e:
                    print(f"❌ Failed to decode as UTF-8: {e}")
                    print(f"Raw bytes: {extracted_data[:100]}...")
            else:
                print(f"❌ Expected bytes, got {type(extracted_data)}")
        else:
            print("❌ Extraction failed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Binary file content (Python file)
    print("\n2. Testing Python file content...")
    
    try:
        # Create a test Python file
        python_content = '''#!/usr/bin/env python3
"""
Test Python File for Steganography
"""

def hello_world():
    print("Hello from embedded Python file!")
    return "Success"

if __name__ == "__main__":
    hello_world()
'''
        
        with open("test_python_file.py", "w", encoding='utf-8') as f:
            f.write(python_content)
        
        print("📥 Hiding Python file...")
        result = stego.hide_data(
            carrier_file_path="test_carrier.txt",
            content_to_hide="test_python_file.py",
            output_path="test_output_python.txt", 
            password=None,
            is_file=True
        )
        print(f"✅ Hide result: {result}")
        
        # Extract the file
        print("📤 Extracting Python file...")
        extracted = stego.extract_data("test_output_python.txt", password=None)
        
        if extracted:
            extracted_data, extracted_filename = extracted
            print(f"📄 Extracted filename: {extracted_filename}")
            print(f"📏 Extracted data length: {len(extracted_data)} bytes")
            
            # Save extracted file
            with open(f"extracted_{extracted_filename}", "wb") as f:
                f.write(extracted_data)
            
            # Try to read as text file
            try:
                with open(f"extracted_{extracted_filename}", "r", encoding='utf-8') as f:
                    extracted_text = f.read()
                
                print(f"✅ Extracted Python content preview:")
                print(extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text)
                
                if extracted_text.strip() == python_content.strip():
                    print("🎯 SUCCESS: Python file content perfectly preserved!")
                else:
                    print("❌ FAILED: Python file content differs!")
                    print(f"Original length: {len(python_content)}")
                    print(f"Extracted length: {len(extracted_text)}")
                    
            except Exception as e:
                print(f"❌ Failed to read extracted file as text: {e}")
                
        else:
            print("❌ Extraction failed!")
            
    except Exception as e:
        print(f"❌ Python test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Using API-style call (simulating enhanced_app.py)
    print("\n3. Testing API-style call...")
    
    try:
        # Create test image file (fake)
        with open("test_image.png", "wb") as f:
            # Write PNG header and some dummy data
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01')
            f.write(b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01')
            f.write(b'\x00\x00\x02\x07\x11\xf2\x00\x00\x00\x00IEND\xaeB`\x82')
        
        # Read the image and Python file as API would
        with open("test_image.png", "rb") as img:
            carrier_data = img.read()
        with open("test_python_file.py", "rb") as py_file:
            file_data = py_file.read()
        
        print("📥 API-style hiding...")
        
        # Simulate how enhanced_app.py calls the steganography module
        # First, check if there's a different method signature
        import inspect
        sig = inspect.signature(stego.hide_data)
        print(f"🔍 hide_data signature: {sig}")
        
        # Try the call that enhanced_app.py would make
        result = stego.hide_data(
            carrier_file_path="test_image.png",
            content_to_hide=file_data,  # Pass bytes directly
            output_path="api_test_output.png",
            password=None,
            is_file=False,
            original_filename="test_python_file.py"
        )
        
        print(f"✅ API-style hide result: {result}")
        
        # Extract
        extracted = stego.extract_data("api_test_output.png", password=None)
        
        if extracted:
            extracted_data, extracted_filename = extracted
            print(f"📄 API extracted filename: {extracted_filename}")
            
            # Compare original and extracted bytes
            print(f"📏 Original bytes: {len(file_data)}")
            print(f"📏 Extracted bytes: {len(extracted_data)}")
            
            if file_data == extracted_data:
                print("🎯 SUCCESS: API-style content perfectly preserved!")
            else:
                print("❌ FAILED: API-style content differs!")
                print(f"First 50 bytes original: {file_data[:50]}")
                print(f"First 50 bytes extracted: {extracted_data[:50]}")
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 CONTENT PRESERVATION TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_content_preservation()