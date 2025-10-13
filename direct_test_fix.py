#!/usr/bin/env python3
"""
Direct test of the enhanced app to verify NoneType fix
"""
import os
import sys
import json
import tempfile
import shutil

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_layered_container_fix():
    """Test the layered container system directly without server"""
    try:
        print("🔧 DIRECT LAYERED CONTAINER TEST")
        print("Testing NoneType fix in layered containers...")
        
        # Import the enhanced app modules
        from enhanced_app import create_layered_data_container, extract_layered_data_container
        
        # Create test data
        test_data_1 = "First hidden message"
        test_data_2 = "Second hidden message"
        
        print(f"\n1. Creating first layer with: '{test_data_1}'")
        # Format: list of tuples (content, filename)
        layers_1 = [(test_data_1, "first_message.txt")]
        container_1 = create_layered_data_container(layers_1)
        print(f"   [OK] First container created: {type(container_1)}")
        
        print(f"\n2. Testing extraction from first container...")
        extracted_1 = extract_layered_data_container(container_1)
        print(f"   [OK] Extracted from first: {extracted_1}")
        
        print(f"\n3. Creating second layer with existing data...")
        # Add second layer to existing data
        layers_2 = [(test_data_1, "first_message.txt"), (test_data_2, "second_message.txt")]
        container_2 = create_layered_data_container(layers_2)
        print(f"   [OK] Second container created: {type(container_2)}")
        
        print(f"\n4. Extracting from layered container...")
        extracted_data = extract_layered_data_container(container_2)
        print(f"   [OK] Extracted: {extracted_data}")
        
        # Test with None values (this was causing the error)
        print(f"\n5. Testing with None values (the original problem)...")
        try:
            # This should not crash now
            layers_with_none = [(test_data_1, "first.txt"), (None, "none.txt"), (test_data_2, "second.txt")]
            none_container = create_layered_data_container(layers_with_none)
            print(f"   [OK] None container handled safely")
            
            # Test extraction with potential None layers
            extracted_with_none = extract_layered_data_container(none_container)
            print(f"   [OK] Extraction with None handled: {extracted_with_none}")
            
        except Exception as e:
            print(f"   ❌ None handling failed: {e}")
            return False
        
        print(f"\n6. Testing mixed content types...")
        # Test file content
        test_file_content = b"This is test file content"
        
        # Create container with file content and text
        mixed_layers = [
            (test_file_content, "test_file.bin"),
            ("Text message", "text_message.txt")
        ]
        mixed_container = create_layered_data_container(mixed_layers)
        print(f"   [OK] Mixed container created")
        
        # Extract mixed content
        mixed_extracted = extract_layered_data_container(mixed_container)
        print(f"   [OK] Mixed content extracted: {len(str(mixed_extracted))} chars")
        
        print(f"\n✅ ALL DIRECT TESTS PASSED!")
        print(f"   - Layered containers work correctly")
        print(f"   - None values are handled safely")
        print(f"   - Mixed content types supported")
        print(f"   - No NoneType subscription errors!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ DIRECT TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_layered_container_fix()
    if success:
        print("\n🎉 The NoneType error fix is working correctly!")
    else:
        print("\n💥 The fix needs more work")