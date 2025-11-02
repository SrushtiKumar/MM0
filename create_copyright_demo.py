#!/usr/bin/env python3
"""
Create a demo file with copyright information for testing the UI
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api"

def create_copyright_demo():
    """Create a demo file with copyright information"""
    
    print("=== CREATING COPYRIGHT DEMO FILE ===\n")
    
    # Copyright data to embed
    copyright_data = {
        "author_name": "John Doe",
        "copyright_alias": "JohnDoe@2025",
        "timestamp": "2025-11-03T10:30:00.000Z"
    }
    
    print(f"Embedding copyright data: {json.dumps(copyright_data, indent=2)}")
    
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
            print(f"Embed Status: {embed_response.status_code}")
            
            if embed_response.status_code == 200:
                embed_result = embed_response.json()
                embed_operation_id = embed_result.get('operation_id')
                output_filename = embed_result.get('output_filename')
                print(f"✓ Embed Operation ID: {embed_operation_id}")
                print(f"✓ Output filename: {output_filename}")
                
                # Wait for completion
                print("Waiting for embed completion...")
                time.sleep(5)
                
                # Check status
                status_response = requests.get(f"{API_BASE}/operations/{embed_operation_id}/status", timeout=10)
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"Embed Status: {status['status']}")
                    
                    if status['status'] == 'completed':
                        # Download the embedded file
                        download_response = requests.get(f"{API_BASE}/operations/{embed_operation_id}/download", timeout=30)
                        
                        if download_response.status_code == 200:
                            demo_filename = "copyright_demo_file.png"
                            with open(demo_filename, 'wb') as f:
                                f.write(download_response.content)
                            print(f"✓ Created demo file: {demo_filename}")
                            print("\nYou can now test the copyright extraction display by:")
                            print(f"1. Go to http://localhost:8082")
                            print("2. Upload the file: copyright_demo_file.png")
                            print("3. Use password: demo123")
                            print("4. Click Extract to see the copyright information display")
                            return True
                        else:
                            print(f"✗ Download failed: {download_response.status_code}")
                    else:
                        print(f"✗ Embed not completed: {status['status']}")
                else:
                    print(f"✗ Status check failed: {status_response.status_code}")
            else:
                print(f"✗ Embed failed: {embed_response.status_code}")
                
    except Exception as e:
        print(f"✗ Error: {e}")
        
    return False

if __name__ == "__main__":
    create_copyright_demo()