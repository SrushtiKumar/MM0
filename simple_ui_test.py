"""
Simple direct test using the UI to trigger debug output
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

# Create simple test files
pdf_content = b"%PDF-1.4\n1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n%%EOF"
png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x01\x14\xa3\x00\x00\x00\x00IEND\xaeB`\x82'

# Write test files
with open('simple_test.pdf', 'wb') as f:
    f.write(pdf_content)

with open('simple_carrier.png', 'wb') as f:
    f.write(png_data)

print("🧪 Simple Forensic Test")
print("Files created - ready for UI testing")
print(f"PDF size: {len(pdf_content)} bytes")
print(f"PNG size: {len(png_data)} bytes")
print()
print("Now use the web interface:")
print("1. Navigate to http://localhost:8081/forensic-evidence")
print("2. Upload simple_carrier.png as carrier")
print("3. Upload simple_test.pdf as secret file") 
print("4. Use password: test123")
print("5. Fill in forensic metadata")
print("6. Check server terminal for debug output")
print()
print("The server debug logs will show:")
print("- [FORENSIC EMBED DEBUG] Original file size")
print("- [FORENSIC EMBED DEBUG] Base64 encoded length")
print("- [FORENSIC EXTRACT DEBUG] Extracted data details")
print("- Any corruption indicators")