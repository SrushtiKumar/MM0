"""
Simple test to check file corruption issue with debugging
"""

import requests
import time
import os
import base64
import json

API_BASE = "http://localhost:8000/api"

def test_file_corruption():
    """Test embedding and extracting a PDF to see debug output"""
    
    print("🔍 Testing File Corruption Issue with Debug Output")
    print("=" * 60)
    
    # Create a simple PDF file for testing
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF"""
    
    # Create a simple PNG for carrier
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x01\x14\xa3\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Write test files
    with open('test_secret.pdf', 'wb') as f:
        f.write(pdf_content)
    
    with open('test_carrier.png', 'wb') as f:
        f.write(png_data)
    
    try:
        print("📤 Step 1: Embedding PDF in PNG...")
        
        # Embed forensic evidence
        forensic_metadata = {
            'case_id': 'TEST-PDF-001',
            'investigator': 'Test Agent',
            'location': 'Test Lab',
            'description': 'Testing PDF corruption issue',
            'name': 'test_secret.pdf',
            'file_size': len(pdf_content),
            'file_type': 'application/pdf'
        }
        
        embed_data = {
            'password': 'test123',
            'encryption_type': 'AES',
            'forensic_metadata': json.dumps(forensic_metadata)
        }
        
        files = {
            'carrier_file': ('test_carrier.png', open('test_carrier.png', 'rb'), 'image/png'),
            'content_file': ('test_secret.pdf', open('test_secret.pdf', 'rb'), 'application/pdf')
        }
        
        embed_response = requests.post(f"{API_BASE}/forensic-embed", data=embed_data, files=files)
        
        # Close files
        files['carrier_file'][1].close()
        files['content_file'][1].close()
        
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.text}")
            return False
        
        embed_result = embed_response.json()
        operation_id = embed_result['operation_id']
        print(f"✅ Embed initiated: {operation_id}")
        
        # Wait for embedding to complete
        print("⏳ Waiting for embedding to complete...")
        for i in range(30):
            status_response = requests.get(f"{API_BASE}/status/{operation_id}")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"  Embed status: {status['status']} - {status.get('message', '')}")
                if status['status'] == 'completed':
                    break
                elif status['status'] == 'failed':
                    print(f"❌ Embed failed: {status.get('message', 'Unknown error')}")
                    return False
            time.sleep(1)
        
        # Download embedded file
        download_response = requests.get(f"{API_BASE}/download/{operation_id}")
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.text}")
            return False
        
        with open('test_stego.png', 'wb') as f:
            f.write(download_response.content)
        
        print("✅ Embedding completed and file downloaded!")
        
        # Step 2: Extract the PDF
        print("\n📥 Step 2: Extracting PDF from PNG...")
        
        extract_data = {
            'password': 'test123',
            'output_format': 'forensic'
        }
        
        files = {
            'stego_file': ('test_stego.png', open('test_stego.png', 'rb'), 'image/png')
        }
        
        extract_response = requests.post(f"{API_BASE}/forensic-extract", data=extract_data, files=files)
        files['stego_file'][1].close()
        
        if extract_response.status_code != 200:
            print(f"❌ Extract failed: {extract_response.text}")
            return False
        
        extract_result = extract_response.json()
        extract_operation_id = extract_result['operation_id']
        print(f"✅ Extract initiated: {extract_operation_id}")
        
        # Wait for extraction to complete
        print("⏳ Waiting for extraction to complete...")
        for i in range(30):
            status_response = requests.get(f"{API_BASE}/status/{extract_operation_id}")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"  Extract status: {status['status']} - {status.get('message', '')}")
                if status['status'] == 'completed':
                    break
                elif status['status'] == 'failed':
                    print(f"❌ Extract failed: {status.get('message', 'Unknown error')}")
                    return False
            time.sleep(1)
        
        # Download extracted ZIP
        download_response = requests.get(f"{API_BASE}/download/{extract_operation_id}")
        if download_response.status_code != 200:
            print(f"❌ ZIP download failed: {download_response.text}")
            return False
        
        with open('extracted_forensic_package.zip', 'wb') as f:
            f.write(download_response.content)
        
        print("✅ Extraction completed and ZIP downloaded!")
        
        # Step 3: Analyze the ZIP contents
        print("\n🔍 Step 3: Analyzing extracted ZIP contents...")
        
        import zipfile
        with zipfile.ZipFile('extracted_forensic_package.zip', 'r') as zip_file:
            file_list = zip_file.namelist()
            print(f"Files in ZIP: {file_list}")
            
            # Check if PDF is in the ZIP
            pdf_files = [f for f in file_list if f.endswith('.pdf')]
            if pdf_files:
                pdf_name = pdf_files[0]
                print(f"Found PDF: {pdf_name}")
                
                # Extract and compare the PDF
                extracted_pdf = zip_file.read(pdf_name)
                print(f"Original PDF size: {len(pdf_content)} bytes")
                print(f"Extracted PDF size: {len(extracted_pdf)} bytes")
                print(f"Original first 20 bytes: {pdf_content[:20]}")
                print(f"Extracted first 20 bytes: {extracted_pdf[:20]}")
                
                if extracted_pdf == pdf_content:
                    print("✅ PDF content matches exactly!")
                    return True
                else:
                    print("❌ PDF content differs - corruption confirmed")
                    
                    # Compare as base64 for detailed analysis
                    orig_b64 = base64.b64encode(pdf_content).decode()
                    extr_b64 = base64.b64encode(extracted_pdf).decode()
                    
                    print(f"Original base64 length: {len(orig_b64)}")
                    print(f"Extracted base64 length: {len(extr_b64)}")
                    print(f"Original base64 first 100: {orig_b64[:100]}")
                    print(f"Extracted base64 first 100: {extr_b64[:100]}")
                    
                    return False
            else:
                print("❌ No PDF found in ZIP")
                return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        for file_path in ['test_secret.pdf', 'test_carrier.png', 'test_stego.png', 'extracted_forensic_package.zip']:
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    print("🧪 Starting File Corruption Debug Test")
    print("This will help identify where the PDF corruption occurs")
    print("Check the backend server logs for detailed debug output!")
    print()
    
    success = test_file_corruption()
    
    if success:
        print("\n🎉 SUCCESS: PDF integrity maintained!")
    else:
        print("\n❌ ISSUE: PDF corruption detected - check debug logs")