#!/usr/bin/env python3
"""
Quick test to verify the NoneType fix works
"""
import requests
import json
import time

def test_server_and_fix():
    try:
        # Test 1: Check server health
        print("🔧 QUICK NONE TYPE FIX TEST")
        print("Testing server connection...")
        
        health_response = requests.get("http://localhost:8000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("[OK] Server is responding")
        else:
            print(f"❌ Server health check failed: {health_response.status_code}")
            return False
            
        # Test 2: Basic embed operation (this should work)
        print("\nTesting basic embedding...")
        
        embed_data = {
            "content_type": "text",
            "content": "Test message",
            "media_type": "video",
            "password": "test123"
        }
        
        with open("clean_carrier.mp4", "rb") as f:
            files = {"media_file": f}
            embed_response = requests.post(
                "http://localhost:8000/api/embed",
                data=embed_data,
                files=files,
                timeout=30
            )
        
        if embed_response.status_code == 200:
            print("[OK] Basic embedding works")
            
            # Get the output filename
            result = embed_response.json()
            output_file = result.get("output_filename", "output.mp4")
            print(f"[OK] Created: {output_file}")
            
            # Test 3: Embed into the same file again (this was causing NoneType error)
            print("\nTesting second embedding (this was causing NoneType errors)...")
            
            embed_data2 = {
                "content_type": "text", 
                "content": "Second message",
                "media_type": "video",
                "password": "test456"
            }
            
            try:
                with open(output_file, "rb") as f:
                    files2 = {"media_file": f}
                    embed_response2 = requests.post(
                        "http://localhost:8000/api/embed",
                        data=embed_data2,
                        files=files2,
                        timeout=30
                    )
                
                if embed_response2.status_code == 200:
                    print("[OK] Second embedding successful - NoneType error fixed!")
                    result2 = embed_response2.json()
                    print(f"[OK] Created: {result2.get('output_filename', 'second_output.mp4')}")
                    return True
                else:
                    print(f"❌ Second embedding failed: {embed_response2.status_code}")
                    print(f"Response: {embed_response2.text}")
                    return False
                    
            except FileNotFoundError:
                print(f"❌ Output file {output_file} not found")
                return False
                
        else:
            print(f"❌ Basic embedding failed: {embed_response.status_code}")
            print(f"Response: {embed_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_server_and_fix()
    if success:
        print("\n✅ ALL TESTS PASSED - NoneType error fix is working!")
    else:
        print("\n❌ TESTS FAILED - Fix needs more work")