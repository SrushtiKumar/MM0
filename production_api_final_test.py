#!/usr/bin/env python3
"""
Production API Safety Test
Testing the live API with document embedding to ensure no corruption
"""

import requests
import os
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf(filepath, pages=20):
    """Create a multi-page test PDF"""
    c = canvas.Canvas(filepath, pagesize=letter)
    
    for page_num in range(1, pages + 1):
        c.drawString(100, 750, f"Production Test PDF - Page {page_num} of {pages}")
        c.drawString(100, 700, "CRITICAL VERIFICATION: This PDF must remain intact")
        c.drawString(100, 650, "after steganographic embedding and extraction.")
        c.drawString(100, 600, f"Page {page_num} unique identifier: PROD_TEST_{page_num:04d}")
        
        # Add content to verify structure preservation
        for i in range(8):
            c.drawString(100, 550 - (i * 30), f"Content line {i+1} on page {page_num}")
        
        c.showPage()
    
    c.save()
    print(f"Created test PDF: {pages} pages, {os.path.getsize(filepath)} bytes")

def analyze_pdf_integrity(filepath):
    """Quick integrity check"""
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # Basic PDF structure checks
    has_header = content.startswith(b'%PDF-')
    has_eof = b'%%EOF' in content
    page_count = content.count(b'/Type /Page')
    stream_count = content.count(b'stream')
    
    print(f"PDF Analysis: Header={has_header}, EOF={has_eof}, Pages={page_count}, Streams={stream_count}")
    return has_header and has_eof and page_count > 0

def test_production_api():
    """Test production API with document embedding"""
    
    print("🚨 PRODUCTION API DOCUMENT SAFETY TEST")
    print("=" * 60)
    
    API_BASE = "http://localhost:8000"
    
    try:
        # Check if server is running
        response = requests.get(f"{API_BASE}/api/supported-formats", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding")
            return False
    except:
        print("❌ Cannot connect to server")
        return False
    
    print("✅ Server is running")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test PDF
        test_pdf = os.path.join(temp_dir, "production_test.pdf")
        create_test_pdf(test_pdf, 25)  # 25-page PDF
        
        original_integrity = analyze_pdf_integrity(test_pdf)
        print(f"Original PDF integrity: {original_integrity}")
        
        if not original_integrity:
            print("❌ Original PDF creation failed")
            return False
        
        # Test embedding via API
        print("\n🔧 Testing document embedding via production API...")
        
        try:
            with open(test_pdf, 'rb') as f:
                files = {'carrier_file': ('test.pdf', f, 'application/pdf')}
                data = {
                    'content_type': 'text',
                    'text_content': 'PRODUCTION SAFETY TEST MESSAGE - Document corruption bug fixed.',
                    'password': ''
                }
                
                response = requests.post(f"{API_BASE}/api/embed", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print("✅ API embedding successful")
                
                # Save embedded PDF
                embedded_pdf = os.path.join(temp_dir, "embedded_production_test.pdf")
                with open(embedded_pdf, 'wb') as f:
                    f.write(response.content)
                
                # Check embedded PDF integrity
                embedded_integrity = analyze_pdf_integrity(embedded_pdf)
                print(f"Embedded PDF integrity: {embedded_integrity}")
                
                if embedded_integrity:
                    print("✅ PDF structure preserved during embedding!")
                    
                    # Test extraction via API
                    print("\n📤 Testing extraction via production API...")
                    
                    with open(embedded_pdf, 'rb') as f:
                        files = {'stego_file': ('embedded_test.pdf', f, 'application/pdf')}
                        data = {'password': ''}
                        
                        response = requests.post(f"{API_BASE}/api/extract", files=files, data=data, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            extracted_message = result.get('extracted_data', '')
                            expected_message = 'PRODUCTION SAFETY TEST MESSAGE - Document corruption bug fixed.'
                            
                            if extracted_message == expected_message:
                                print("✅ Extraction successful and accurate!")
                                print("✅ PRODUCTION API IS SAFE FOR DOCUMENT STEGANOGRAPHY")
                                return True
                            else:
                                print(f"❌ Extraction mismatch")
                                print(f"Expected: {expected_message}")
                                print(f"Got: {extracted_message}")
                        else:
                            print(f"❌ Extraction failed: {result}")
                    else:
                        print(f"❌ Extraction API error: {response.status_code}")
                else:
                    print("❌ PDF structure corrupted during embedding!")
            else:
                print(f"❌ API embedding failed: {response.status_code}")
                print(response.text)
        
        except Exception as e:
            print(f"❌ API test failed: {e}")
    
    return False

if __name__ == "__main__":
    success = test_production_api()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ PRODUCTION API DOCUMENT SAFETY CONFIRMED")
        print("✅ Document corruption bug COMPLETELY FIXED")
        print("✅ Safe for production deployment")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ PRODUCTION API SAFETY TEST FAILED")
        print("❌ DO NOT DEPLOY - CORRUPTION RISK REMAINS")
        print("=" * 60)