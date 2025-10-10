#!/usr/bin/env python3
"""
Test password security in document steganography
This test should demonstrate that wrong passwords fail to extract data
"""

from enhanced_web_document_stego import EnhancedWebDocumentSteganographyManager
import os

def create_test_pdf():
    """Create a simple test PDF"""
    test_content = """This is a test PDF document for steganography testing.
It contains some text content that will be used as a carrier for hidden data.
The document has multiple lines to provide enough space for embedding data.
"""
    with open("test_security_document.txt", "w") as f:
        f.write(test_content)
    return "test_security_document.txt"

def test_document_password_security():
    """Test that wrong passwords fail to extract data from documents"""
    print("🔐 Testing document password security...")
    
    # Create test document
    test_doc = create_test_pdf()
    
    # Test with correct password
    correct_password = "correct_doc_password_123"
    secret_message = "This is a secret message hidden in the document!"
    
    print(f"\n1. Hiding data in document with password: '{correct_password}'")
    manager_hide = EnhancedWebDocumentSteganographyManager(correct_password)
    
    try:
        result = manager_hide.hide_data(test_doc, secret_message, "stego_document.txt", False)
        print(f"✅ Hide operation successful: {result}")
    except Exception as e:
        print(f"❌ Hide operation failed: {e}")
        return
    
    # Test extraction with CORRECT password
    print(f"\n2. Extracting with CORRECT password: '{correct_password}'")
    manager_correct = EnhancedWebDocumentSteganographyManager(correct_password)
    
    try:
        extracted_data, filename = manager_correct.extract_data("stego_document.txt")
        extracted_text = extracted_data.decode('utf-8')
        print(f"✅ Extraction with correct password successful!")
        print(f"   Extracted: {extracted_text}")
        if secret_message in extracted_text:
            print("✅ Correct message extracted!")
        else:
            print("❌ Wrong message extracted!")
    except Exception as e:
        print(f"❌ Extraction with correct password failed: {e}")
    
    # Test extraction with WRONG passwords
    wrong_passwords = ["wrong_password", "123456", "", "different_password", "hacker_attempt"]
    
    for wrong_password in wrong_passwords:
        print(f"\n3. Testing extraction with WRONG password: '{wrong_password}'")
        manager_wrong = EnhancedWebDocumentSteganographyManager(wrong_password)
        
        try:
            extracted_data, filename = manager_wrong.extract_data("stego_document.txt")
            extracted_text = extracted_data.decode('utf-8')
            print(f"❌ SECURITY ISSUE: Wrong password '{wrong_password}' successfully extracted data!")
            print(f"   This should NOT happen! Extracted: {extracted_text[:50]}...")
        except Exception as e:
            print(f"✅ Correct behavior: Wrong password '{wrong_password}' failed to extract: {e}")
    
    # Cleanup
    for file in ["test_security_document.txt", "stego_document.txt"]:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    test_document_password_security()