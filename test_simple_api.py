"""
Simple Direct API Test - No Background Processing Wait
Test API endpoints directly to see what's happening
"""
import requests
import os
import json

def test_simple_api():
    print("🔧 SIMPLE API TEST")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Create simple test files
    print("📁 Creating test files...")
    
    # Test Python content
    python_content = "print('Hello from embedded Python file!')\n# This is a test"
    with open("simple_test.py", "w") as f:
        f.write(python_content)
    
    # Simple carrier
    with open("simple_carrier.txt", "w") as f:
        f.write("This is a simple text carrier file for testing.")
    
    print("✅ Test files created")
    
    # Test 1: Health check
    print("\n1. Testing server health...")
    try:
        health_response = requests.get(f"{base_url}/api/health")
        print(f"Health status: {health_response.status_code}")
        if health_response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print("❌ Server health issue")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Simple embed call
    print("\n2. Testing embed endpoint...")
    try:
        with open("simple_carrier.txt", "rb") as carrier, open("simple_test.py", "rb") as content:
            embed_response = requests.post(f"{base_url}/api/embed", 
                files={
                    "carrier_file": ("carrier.txt", carrier, "text/plain"),
                    "content_file": ("test.py", content, "text/plain")
                },
                data={
                    "carrier_type": "document",
                    "content_type": "file", 
                    "password": "test123"
                },
                timeout=30
            )
        
        print(f"Embed response status: {embed_response.status_code}")
        print(f"Embed response text: {embed_response.text[:500]}")
        
        if embed_response.status_code == 200:
            result = embed_response.json()
            operation_id = result.get('operation_id')
            print(f"✅ Embed started, operation ID: {operation_id}")
            
            # Check operation status immediately
            if operation_id:
                status_response = requests.get(f"{base_url}/api/status/{operation_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Initial status: {status_data}")
                else:
                    print(f"Status check failed: {status_response.status_code}")
            
        else:
            print(f"❌ Embed failed: {embed_response.status_code}")
            
    except Exception as e:
        print(f"❌ Embed request failed: {e}")
    
    # Test 3: Try using universal steganography directly via Python
    print("\n3. Testing steganography modules directly...")
    try:
        import sys
        sys.path.append('.')
        from universal_file_steganography import UniversalFileSteganography
        
        stego = UniversalFileSteganography()
        
        # Direct embed
        print("📥 Direct embedding...")
        result = stego.hide_data(
            carrier_file_path="simple_carrier.txt",
            content_to_hide="simple_test.py",
            output_path="direct_output.txt",
            password="test123",
            is_file=True
        )
        
        print(f"✅ Direct embed result: {result}")
        
        # Direct extract  
        print("📤 Direct extraction...")
        extracted = stego.extract_data("direct_output.txt", password="test123")
        
        if extracted:
            extracted_data, extracted_filename = extracted
            print(f"✅ Direct extract successful!")
            print(f"📄 Filename: {extracted_filename}")
            print(f"📏 Data length: {len(extracted_data)}")
            print(f"📝 Data type: {type(extracted_data)}")
            
            # Save and verify
            with open(f"direct_extracted_{extracted_filename}", "wb") as f:
                f.write(extracted_data)
            
            # Try to read as text
            try:
                with open(f"direct_extracted_{extracted_filename}", "r", encoding='utf-8') as f:
                    extracted_text = f.read()
                
                print("📋 Extracted content:")
                print(extracted_text)
                
                if extracted_text.strip() == python_content.strip():
                    print("🎯 SUCCESS: Direct steganography preserves content perfectly!")
                else:
                    print("❌ Content differs in direct test")
            except Exception as e:
                print(f"❌ Could not read extracted file as text: {e}")
        else:
            print("❌ Direct extraction failed")
            
    except Exception as e:
        print(f"❌ Direct steganography test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 40)
    print("🏁 SIMPLE API TEST COMPLETE")
    print("=" * 40)

if __name__ == "__main__":
    test_simple_api()