#!/usr/bin/env python3
"""
Simple demo file creator without status checking
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api"

def create_demo_simple():
    """Create demo file with direct download"""
    
    print("=== CREATING SIMPLE COPYRIGHT DEMO ===\n")
    
    # Copyright data
    copyright_data = {
        "author_name": "John Doe",
        "copyright_alias": "JohnDoe@2025", 
        "timestamp": "2025-11-03T10:30:00.000Z"
    }
    
    try:
        # Use existing image as carrier
        with open("debug_embedded.png", 'rb') as carrier_file:
            files = {'carrier_file': carrier_file}
            data = {
                'password': 'demo123',
                'carrier_type': 'image',
                'content_type': 'text',
                'text_content': json.dumps(copyright_data)
            }
            
            embed_response = requests.post(f"{API_BASE}/embed", files=files, data=data, timeout=30)
            
            if embed_response.status_code == 200:
                embed_result = embed_response.json()
                embed_operation_id = embed_result.get('operation_id')
                print(f"✓ Embed Operation ID: {embed_operation_id}")
                
                # Wait a bit then try to download
                print("Waiting 5 seconds then downloading...")
                time.sleep(5)
                
                # Try direct download
                try:
                    download_response = requests.get(f"{API_BASE}/operations/{embed_operation_id}/download", timeout=30)
                    
                    if download_response.status_code == 200:
                        demo_filename = "copyright_demo_file.png"
                        with open(demo_filename, 'wb') as f:
                            f.write(download_response.content)
                        print(f"✓ Created demo file: {demo_filename}")
                        print("\n=== TEST INSTRUCTIONS ===")
                        print("1. Go to http://localhost:8082")
                        print("2. Click on Extract tab")
                        print("3. Upload: copyright_demo_file.png")
                        print("4. Enter password: demo123")
                        print("5. Click Extract")
                        print("6. You should see copyright info above the download button!")
                        return True
                    else:
                        print(f"✗ Download failed: {download_response.status_code}")
                except Exception as e:
                    print(f"✗ Download error: {e}")
                    
            else:
                print(f"✗ Embed failed: {embed_response.status_code}")
                
    except Exception as e:
        print(f"✗ Error: {e}")
        
    return False

if __name__ == "__main__":
    create_demo_simple()