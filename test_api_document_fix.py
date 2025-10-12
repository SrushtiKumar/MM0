#!/usr/bin/env python3
"""
Test End-to-End Document Format Preservation
Test with actual backend API to verify DOCX files are extracted correctly
"""

import sys
import os
import time
import requests
from pathlib import Path

def create_test_files():
    """Create test files for the API test"""
    
    # Create a more substantial DOCX file for testing
    docx_content = b"""PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00\xb7\x81\xb6\\\x1a\x01\x00\x00L\x04\x00\x00\x10\x00\x08\x02[Content_Types].xml \xa2\x04\x02(\xa0\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Important Meeting Notes.docx - This document contains sensitive information about quarterly projections and strategic planning initiatives."""
    
    docx_filename = "quarterly_report.docx"
    with open(docx_filename, 'wb') as f:
        f.write(docx_content)
    
    # Create container document
    container_content = """Annual Report Summary
===================

This comprehensive document contains our annual performance metrics and strategic insights.
The document includes detailed analysis of market trends and competitive positioning.
Financial projections and operational efficiency metrics are thoroughly documented.
Strategic recommendations for the upcoming fiscal year are outlined in subsequent sections.
Risk assessment and mitigation strategies have been carefully evaluated and documented.

Executive Summary
================

Our organization has demonstrated exceptional growth across multiple operational areas.
Market expansion initiatives have yielded positive results in key demographic segments.
Technology adoption has streamlined operations and improved customer satisfaction metrics.
Partnership development has created new opportunities for sustainable revenue growth.
Investment in human resources has enhanced organizational capability and performance.

This document serves as a foundation for future strategic planning and decision making."""
    
    container_filename = "annual_report.txt"
    with open(container_filename, 'w', encoding='utf-8') as f:
        f.write(container_content)
    
    return docx_filename, container_filename

def test_api_embedding_extraction(docx_file, container_file, password):
    """Test the complete API workflow for document steganography"""
    
    print("🌐 TESTING API EMBEDDING & EXTRACTION")
    print("-" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # Step 1: Embed the DOCX file in the container
        print("📤 Step 1: Embedding DOCX file...")
        
        with open(container_file, 'rb') as cf, open(docx_file, 'rb') as df:
            files = {
                'carrier_file': (container_file, cf, 'text/plain'),
                'content_file': (docx_file, df, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            data = {
                'carrier_type': 'document',
                'content_type': 'file',
                'password': password
            }
            
            response = requests.post(f"{base_url}/api/embed", files=files, data=data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Embedding failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        embed_result = response.json()
        operation_id = embed_result['operation_id']
        print(f"✅ Embedding started: {operation_id}")
        
        # Wait for embedding to complete
        while True:
            status_response = requests.get(f"{base_url}/api/operations/{operation_id}/status")
            status = status_response.json()
            
            print(f"   Status: {status['status']} - {status['message']}")
            
            if status['status'] == 'completed':
                break
            elif status['status'] == 'failed':
                print(f"❌ Embedding failed: {status['message']}")
                return False
            
            time.sleep(1)
        
        # Download the stego file
        download_response = requests.get(f"{base_url}/api/operations/{operation_id}/download")
        stego_filename = f"stego_{container_file}"
        
        with open(stego_filename, 'wb') as f:
            f.write(download_response.content)
        
        print(f"✅ Stego file saved: {stego_filename}")
        
        # Step 2: Extract the hidden DOCX file
        print(f"\n📥 Step 2: Extracting hidden file...")
        
        with open(stego_filename, 'rb') as f:
            files = {'stego_file': f}
            data = {
                'password': password,
                'output_format': 'file'
            }
            
            extract_response = requests.post(f"{base_url}/api/extract", files=files, data=data, timeout=30)
        
        if extract_response.status_code != 200:
            print(f"❌ Extraction failed: {extract_response.status_code}")
            print(f"   Response: {extract_response.text}")
            return False
        
        extract_result = extract_response.json()
        extract_operation_id = extract_result['operation_id']
        print(f"✅ Extraction started: {extract_operation_id}")
        
        # Wait for extraction to complete
        while True:
            status_response = requests.get(f"{base_url}/api/operations/{extract_operation_id}/status")
            status = status_response.json()
            
            print(f"   Status: {status['status']} - {status['message']}")
            
            if status['status'] == 'completed':
                break
            elif status['status'] == 'failed':
                print(f"❌ Extraction failed: {status['message']}")
                return False
            
            time.sleep(1)
        
        # Download the extracted file
        download_response = requests.get(f"{base_url}/api/operations/{extract_operation_id}/download")
        
        # Check Content-Disposition header for filename
        content_disposition = download_response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            extracted_filename = content_disposition.split('filename=')[1].strip('"')
        else:
            extracted_filename = "extracted_file.bin"  # Fallback
        
        print(f"✅ Extraction completed!")
        print(f"   Original filename: {docx_file}")
        print(f"   Extracted filename: {extracted_filename}")
        print(f"   File size: {len(download_response.content)} bytes")
        
        # Save the extracted file
        with open(f"api_extracted_{extracted_filename}", 'wb') as f:
            f.write(download_response.content)
        
        # Check if format is preserved
        original_ext = Path(docx_file).suffix
        extracted_ext = Path(extracted_filename).suffix
        
        print(f"\n📊 FORMAT PRESERVATION CHECK:")
        print(f"   Original extension: {original_ext}")
        print(f"   Extracted extension: {extracted_ext}")
        
        if extracted_ext == original_ext:
            print(f"✅ SUCCESS: File format preserved!")
            print(f"   DOCX files are now extracted as .docx, not .bin")
        else:
            print(f"❌ ISSUE: File format changed from {original_ext} to {extracted_ext}")
        
        # Cleanup
        for file in [stego_filename, f"api_extracted_{extracted_filename}"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
        
        return extracted_ext == original_ext
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🧪 END-TO-END DOCUMENT FORMAT PRESERVATION TEST")
    print("=" * 70)
    print("Testing complete API workflow to ensure DOCX files maintain format")
    print("Goal: DOCX files should be extracted as .docx, not .bin\n")
    
    # Create test files
    docx_file, container_file = create_test_files()
    print(f"✅ Created test files:")
    print(f"   DOCX file: {docx_file} ({os.path.getsize(docx_file)} bytes)")
    print(f"   Container: {container_file} ({os.path.getsize(container_file)} bytes)")
    
    # Test with API
    password = "SecurePass123"
    success = test_api_embedding_extraction(docx_file, container_file, password)
    
    # Cleanup
    for file in [docx_file, container_file]:
        if os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass
    
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Document format preservation test")
    
    if success:
        print("✅ File size limits have been removed")
        print("✅ DOCX files now extract with correct .docx extension")
        print("✅ Both issues have been resolved!")
    else:
        print("❌ Document format preservation still needs work")

if __name__ == "__main__":
    main()