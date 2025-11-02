#!/usr/bin/env python3
"""
Test document steganography to identify corruption issues
"""

import os
from universal_file_steganography import UniversalFileSteganography

def test_document_corruption():
    """Test document steganography with various document types"""
    
    print("🧪 TESTING DOCUMENT STEGANOGRAPHY CORRUPTION")
    print("=" * 60)
    
    # Create test documents of different types
    test_documents = {
        "simple_text.txt": "This is a simple text document.\nIt has multiple lines.\nThis should remain readable after steganography.",
        "structured_doc.txt": """Document Title
==================

Section 1: Introduction
This is a structured document with formatting.
- Bullet point 1
- Bullet point 2  
- Bullet point 3

Section 2: Content
More content here with special characters: àáâãäå
Numbers: 123456789
Symbols: !@#$%^&*()

Section 3: Conclusion
This document should remain fully readable.
""",
        "code_file.py": '''#!/usr/bin/env python3
"""
Sample Python code file for testing
"""

def hello_world():
    """Print hello world"""
    print("Hello, World!")
    
if __name__ == "__main__":
    hello_world()
'''
    }
    
    # Secret content to hide
    secret_content = "This is secret data hidden in the document using steganography!"
    
    results = {}
    
    for doc_name, doc_content in test_documents.items():
        print(f"\n📄 Testing: {doc_name}")
        print("-" * 40)
        
        # Create test document
        with open(doc_name, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"✅ Created document: {len(doc_content)} characters")
        
        # Create secret file
        secret_file = f"secret_for_{doc_name.replace('.', '_')}.txt"
        with open(secret_file, 'w', encoding='utf-8') as f:
            f.write(secret_content)
        
        try:
            # Test steganography
            stego = UniversalFileSteganography("test123")
            output_file = f"processed_{doc_name}"
            
            print(f"🔐 Embedding secret...")
            result = stego.hide_file_in_file(doc_name, secret_file, output_file)
            
            if not result.get('success'):
                print(f"❌ Embedding failed: {result}")
                results[doc_name] = "EMBED_FAILED"
                continue
            
            print(f"✅ Embedding successful using {result.get('method', 'unknown')} method")
            
            # Test if processed document is readable
            print(f"📖 Testing processed document...")
            
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    processed_content = f.read()
                
                # Check readability
                if len(processed_content) > 0:
                    print(f"✅ Processed document is readable ({len(processed_content)} chars)")
                    
                    # For text files, check if original content is preserved
                    if doc_name.endswith('.txt') or doc_name.endswith('.py'):
                        if doc_content in processed_content:
                            print(f"✅ Original content preserved in processed file")
                        else:
                            print(f"⚠️ Original content modified (expected for steganography)")
                    
                    # Test extraction
                    print(f"🔍 Testing extraction...")
                    extraction_result = stego.extract_data(output_file)
                    
                    if extraction_result and isinstance(extraction_result, tuple):
                        extracted_content, filename = extraction_result
                        
                        if isinstance(extracted_content, bytes):
                            extracted_text = extracted_content.decode('utf-8')
                        else:
                            extracted_text = extracted_content
                        
                        if secret_content.strip() == extracted_text.strip():
                            print(f"✅ Extraction successful - data preserved!")
                            results[doc_name] = "SUCCESS"
                        else:
                            print(f"❌ Extraction data mismatch")
                            results[doc_name] = "EXTRACT_MISMATCH"
                    else:
                        print(f"❌ Extraction failed")
                        results[doc_name] = "EXTRACT_FAILED"
                else:
                    print(f"❌ Processed document is empty/corrupted")
                    results[doc_name] = "CORRUPTED"
                    
            except Exception as e:
                print(f"❌ Cannot read processed document: {e}")
                results[doc_name] = "UNREADABLE"
                
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            results[doc_name] = "ERROR"
            
        finally:
            # Cleanup
            for file in [doc_name, secret_file, f"processed_{doc_name}"]:
                if os.path.exists(file):
                    os.remove(file)
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📊 DOCUMENT STEGANOGRAPHY TEST RESULTS")
    print(f"=" * 60)
    
    for doc_name, status in results.items():
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"{status_icon} {doc_name:<20} {status}")
    
    success_count = sum(1 for status in results.values() if status == "SUCCESS")
    total_count = len(results)
    
    print(f"\n📈 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print(f"🎉 ALL DOCUMENT TESTS PASSED!")
        return True
    else:
        print(f"⚠️ DOCUMENT CORRUPTION ISSUES REMAIN")
        return False

if __name__ == "__main__":
    test_document_corruption()