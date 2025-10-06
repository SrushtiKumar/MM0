#!/usr/bin/env python3

import requests
import json
import time
import os

def test_web_upload():
    """Test uploading files through the web API to reproduce the issue."""
    
    base_url = "http://localhost:8000"
    
    # Create test files
    print("Creating test files...")
    
    # Create a test PDF (412KB)
    test_pdf_content = b"PDF test content " * 24000  # ~400KB
    pdf_filename = "test_document.pdf"
    with open(pdf_filename, "wb") as f:
        f.write(test_pdf_content)
    
    print(f"Created test PDF: {pdf_filename} ({len(test_pdf_content):,} bytes)")
    
    # Use existing test image
    image_filename = "test_11mb_image.png"
    if not os.path.exists(image_filename):
        print(f"Error: {image_filename} not found")
        return
    
    image_size = os.path.getsize(image_filename)
    print(f"Container image: {image_filename} ({image_size:,} bytes)")
    
    try:
        # Test the hide operation
        print("\n--- Testing Hide Operation ---")
        
        # Prepare files for upload
        with open(image_filename, "rb") as container_file, open(pdf_filename, "rb") as secret_file:
            
            files = {
                "container_file": (image_filename, container_file, "image/png"),
                "secret_file": (pdf_filename, secret_file, "application/pdf")
            }
            
            data = {
                "request_data": json.dumps({
                    "password": "test123",
                    "is_enhanced": False
                })
            }
            
            print("Sending hide request...")
            response = requests.post(f"{base_url}/api/hide", files=files, data=data)
            
            print(f"Hide request status: {response.status_code}")
            print(f"Hide response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get("job_id")
                
                if job_id:
                    print(f"Job ID: {job_id}")
                    
                    # Poll for job completion
                    print("Waiting for job completion...")
                    for i in range(30):  # Wait up to 30 seconds
                        time.sleep(1)
                        
                        status_response = requests.get(f"{base_url}/api/job/{job_id}")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            print(f"Status: {status_data.get('status')} - {status_data.get('message')}")
                            
                            if status_data.get('status') == 'completed':
                                print("✅ Hide operation completed successfully!")
                                print(f"Result: {status_data.get('result')}")
                                break
                            elif status_data.get('status') == 'failed':
                                print("❌ Hide operation failed!")
                                print(f"Error: {status_data.get('message')}")
                                break
                        else:
                            print(f"Status check failed: {status_response.status_code}")
                            break
                    else:
                        print("❌ Timeout waiting for job completion")
                else:
                    print("❌ No job ID received")
            else:
                print("❌ Hide request failed")
                
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if os.path.exists(pdf_filename):
            os.unlink(pdf_filename)
            print(f"Cleaned up {pdf_filename}")

if __name__ == "__main__":
    test_web_upload()