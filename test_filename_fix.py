#!/usr/bin/env python3
"""
Test Document Filename Fix
Simple test to verify document filename preservation
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_document_filename_fix():
    """Test that document filename is preserved correctly"""
    
    print("🧪 DOCUMENT FILENAME PRESERVATION TEST")
    print("=" * 50)
    
    try:
        from enhanced_web_document_stego import EnhancedWebDocumentSteganographyManager
        
        # Create test files
        docx_content = b"Test DOCX content for steganography"
        docx_filename = "report.docx"
        
        with open(docx_filename, 'wb') as f:
            f.write(docx_content)
        
        container_content = "This is a container document with enough text for steganography."
        container_filename = "container.txt"
        
        with open(container_filename, 'w') as f:
            f.write(container_content)
        
        print(f"✅ Created test files")
        print(f"   DOCX file: {docx_filename}")
        print(f"   Container: {container_filename}")
        
        # Test 1: Using file path (old way - should work)
        print(f"\n🧪 Test 1: Using file path")
        manager1 = EnhancedWebDocumentSteganographyManager("test123")
        result1 = manager1.hide_data(container_filename, docx_filename, "test1_output.txt", is_file=True)
        print(f"   Result: {result1['success']}")
        
        if os.path.exists("test1_output.txt"):
            extracted1, filename1 = manager1.extract_data("test1_output.txt")
            print(f"   Extracted filename: '{filename1}'")
            print(f"   Expected filename: '{docx_filename}'")
            print(f"   Match: {filename1 == docx_filename}")
        
        # Test 2: Using file content + original filename (new way - backend style)
        print(f"\n🧪 Test 2: Using file content + original filename")
        manager2 = EnhancedWebDocumentSteganographyManager("test123")
        
        with open(docx_filename, 'rb') as f:
            file_content = f.read()
        
        result2 = manager2.hide_data(
            container_filename, 
            file_content,           # bytes content
            "test2_output.txt", 
            is_file=True,
            original_filename=docx_filename  # Pass original filename
        )
        print(f"   Result: {result2['success']}")
        
        if os.path.exists("test2_output.txt"):
            extracted2, filename2 = manager2.extract_data("test2_output.txt")
            print(f"   Extracted filename: '{filename2}'")
            print(f"   Expected filename: '{docx_filename}'")
            print(f"   Match: {filename2 == docx_filename}")
        
        # Cleanup
        for file in [docx_filename, container_filename, "test1_output.txt", "test2_output.txt"]:
            if os.path.exists(file):
                os.remove(file)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 TESTING DOCUMENT FILENAME FIX")
    print("=" * 50)
    print("Verifying that document files maintain original filename when extracted\n")
    
    success = test_document_filename_fix()
    
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Document filename preservation test")

if __name__ == "__main__":
    main()