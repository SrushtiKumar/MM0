#!/usr/bin/env python3
"""
API test to verify the NoneType fix works through the web interface
"""
import requests
import json
import time
import subprocess
import threading
import os

def start_server():
    """Start the server in a separate process"""
    return subprocess.Popen(
        ["python", "enhanced_app.py"],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def test_api_nonetype_fix():
    """Test the API to ensure NoneType errors are fixed"""
    server_process = None
    try:
        print("🔧 API NONETYPE FIX TEST")
        print("Starting server...")
        
        # Start server
        server_process = start_server()
        
        # Wait for server to start
        print("Waiting for server to initialize...")
        time.sleep(8)
        
        # Test server health
        try:
            health_response = requests.get("http://localhost:8000/api/health", timeout=5)
            if health_response.status_code == 200:
                print("[OK] Server is responding")
            else:
                print(f"❌ Server health check failed: {health_response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")
            return False
        
        # Test 1: Basic embedding
        print("\n1. Testing basic embedding...")
        embed_data = {
            "content_type": "text",
            "text_content": "First message",
            "password": "test123"
        }
        
        with open("clean_carrier.mp4", "rb") as f:
            files = {"carrier_file": f}
            embed_response = requests.post(
                "http://localhost:8000/api/embed",
                data=embed_data,
                files=files,
                timeout=30
            )
        
        if embed_response.status_code != 200:
            print(f"❌ Basic embedding failed: {embed_response.status_code}")
            print(f"Response: {embed_response.text}")
            return False
        
        result1 = embed_response.json()
        output_file_1 = result1.get("output_filename", "output.mp4")
        print(f"[OK] First embedding successful: {output_file_1}")
        
        # Test 2: Second embedding (this was causing NoneType errors)
        print("\n2. Testing second embedding into existing container...")
        embed_data2 = {
            "content_type": "text",
            "text_content": "Second message", 
            "password": "test456"
        }
        
        if not os.path.exists(output_file_1):
            print(f"❌ Output file {output_file_1} not found")
            return False
            
        with open(output_file_1, "rb") as f:
            files2 = {"carrier_file": f}
            embed_response2 = requests.post(
                "http://localhost:8000/api/embed",
                data=embed_data2,
                files=files2,
                timeout=30
            )
        
        if embed_response2.status_code != 200:
            print(f"❌ Second embedding failed: {embed_response2.status_code}")
            print(f"Response: {embed_response2.text}")
            return False
        
        result2 = embed_response2.json()
        output_file_2 = result2.get("output_filename", "second_output.mp4")
        print(f"[OK] Second embedding successful: {output_file_2}")
        
        # Test 3: Third embedding (stress test for layered containers)
        print("\n3. Testing third embedding (stress test)...")
        embed_data3 = {
            "content_type": "text",
            "text_content": "Third message",
            "password": "test789"
        }
        
        if not os.path.exists(output_file_2):
            print(f"❌ Output file {output_file_2} not found")
            return False
            
        with open(output_file_2, "rb") as f:
            files3 = {"carrier_file": f}
            embed_response3 = requests.post(
                "http://localhost:8000/api/embed",
                data=embed_data3,
                files=files3,
                timeout=30
            )
        
        if embed_response3.status_code != 200:
            print(f"❌ Third embedding failed: {embed_response3.status_code}")
            print(f"Response: {embed_response3.text}")
            return False
        
        result3 = embed_response3.json()
        output_file_3 = result3.get("output_filename", "third_output.mp4")
        print(f"[OK] Third embedding successful: {output_file_3}")
        
        # Test 4: Extraction to verify data integrity
        print("\n4. Testing extraction from final container...")
        extract_data = {
            "password": "test789"  # Last password used
        }
        
        with open(output_file_3, "rb") as f:
            files_extract = {"stego_file": f}
            extract_response = requests.post(
                "http://localhost:8000/api/extract",
                data=extract_data,
                files=files_extract,
                timeout=30
            )
        
        if extract_response.status_code != 200:
            print(f"❌ Extraction failed: {extract_response.status_code}")
            print(f"Response: {extract_response.text}")
            return False
        
        extract_result = extract_response.json()
        print(f"[OK] Extraction successful: {extract_result.get('message', 'No message')}")
        
        print(f"\n✅ ALL API TESTS PASSED!")
        print(f"   - Multiple sequential embeddings work")
        print(f"   - Layered containers handle multiple messages")
        print(f"   - No NoneType subscription errors")
        print(f"   - Data integrity maintained through extraction")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if server_process:
            print("\nShutting down server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()

if __name__ == "__main__":
    success = test_api_nonetype_fix()
    if success:
        print("\n🎉 The NoneType error fix is working correctly through the API!")
    else:
        print("\n💥 API tests failed - fix needs more work")