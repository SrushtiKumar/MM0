#!/usr/bin/env python3
"""Test document steganography password security"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_web_document_stego import EnhancedWebDocumentSteganographyManager

def test_document_password_security():
    """Test if document steganography properly validates passwords"""
    print("Testing document steganography password security...")
    
    # Create test document path
    test_doc_path = "test_container.pdf"
    test_message = "Secret message for document test"
    correct_password = "correct123"
    wrong_password = "wrong456"
    
    try:
        # Create steganography manager with correct password
        manager = EnhancedWebDocumentSteganographyManager(correct_password)
        
        # Hide message
        print("Hiding message with correct password...")
        result = manager.hide_data(
            test_doc_path, 
            "test.pdf", 
            test_message
        )
        print(f"Hidden successfully. Result: {result}")
        
        # Get the output file path
        output_path = result["output_path"]
        
        # Read the steganographic file content
        with open(output_path, 'rb') as f:
            stego_content = f.read()
        
        # Try to extract with WRONG password
        print("\nTrying to extract with WRONG password...")
        wrong_manager = EnhancedWebDocumentSteganographyManager(wrong_password)
        
        try:
            extracted_content, filename = wrong_manager.extract_data(output_path)
            print(f"❌ SECURITY VULNERABILITY: Successfully extracted with wrong password!")
            print(f"   Extracted: {extracted_content[:100]}...")
            print(f"   Filename: {filename}")
            return False
        except Exception as e:
            print(f"✅ Good: Wrong password failed with error: {e}")
            
        # Now try with correct password to verify it works
        print("\nTrying to extract with CORRECT password...")
        correct_manager = EnhancedWebDocumentSteganographyManager(correct_password)
        
        try:
            extracted_content, filename = correct_manager.extract_data(output_path)
            print(f"✅ Good: Correct password worked!")
            print(f"   Extracted: {extracted_content[:100]}...")
            print(f"   Filename: {filename}")
            return True
        except Exception as e:
            print(f"❌ Problem: Correct password failed: {e}")
            return False
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_document_password_security()