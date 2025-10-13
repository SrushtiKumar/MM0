#!/usr/bin/env python3
"""
Final verification test for NoneType error fix
This test simulates the exact scenario that was causing the error
"""
import json
import tempfile
import os

def test_nonetype_error_scenario():
    """Test the exact scenario that was causing NoneType errors"""
    print("🔧 FINAL NONETYPE ERROR FIX VERIFICATION")
    print("Testing the specific scenario that was causing the error...\n")
    
    try:
        # Import the fixed functions
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from enhanced_app import create_layered_data_container, extract_layered_data_container
        
        # SCENARIO 1: Create initial container
        print("1. Creating initial layered container...")
        initial_layers = [("First message", "message1.txt")]
        container_1 = create_layered_data_container(initial_layers)
        print(f"   [OK] Container 1 created: {len(container_1)} chars")
        
        # SCENARIO 2: Extract data from container (to simulate existing data)
        print("\n2. Extracting data from container...")
        extracted_data = extract_layered_data_container(container_1)
        print(f"   [OK] Extracted: {extracted_data}")
        
        # SCENARIO 3: This is where the NoneType error occurred - adding new content to existing container
        print("\n3. Adding new content to existing container (critical test)...")
        
        # Simulate the process_embed_operation scenario
        existing_layers = extracted_data  # This comes from extraction
        new_content = "Second message"
        new_filename = "message2.txt"
        
        # Check if existing_layers contains valid data (this was the bug source)
        if existing_layers is None:
            print("   ❌ CRITICAL: existing_layers is None!")
            return False
            
        print(f"   [DEBUG] existing_layers type: {type(existing_layers)}")
        print(f"   [DEBUG] existing_layers content: {existing_layers}")
        
        # Create new layer info
        new_layer_info = (new_content, new_filename)
        
        # The critical operation - add new layer to existing layers
        if isinstance(existing_layers, list):
            all_layers = existing_layers + [new_layer_info]
        else:
            print("   ❌ CRITICAL: existing_layers is not a list!")
            return False
            
        print(f"   [DEBUG] all_layers: {all_layers}")
        
        # SCENARIO 4: Create new container with combined layers (this was failing)
        print("\n4. Creating combined layered container...")
        combined_container = create_layered_data_container(all_layers)
        print(f"   [OK] Combined container created: {len(combined_container)} chars")
        
        # SCENARIO 5: Extract from combined container 
        print("\n5. Extracting from combined container...")
        final_extracted = extract_layered_data_container(combined_container)
        print(f"   [OK] Final extracted: {final_extracted}")
        
        # SCENARIO 6: Verify data integrity
        print("\n6. Verifying data integrity...")
        if len(final_extracted) == 2:
            print(f"   [OK] Correct number of layers: {len(final_extracted)}")
            print(f"   [OK] Layer 1: {final_extracted[0]}")
            print(f"   [OK] Layer 2: {final_extracted[1]}")
        else:
            print(f"   ❌ Wrong number of layers: {len(final_extracted)}")
            return False
        
        # SCENARIO 7: Test with None values (edge case that was causing crashes)
        print("\n7. Testing None value handling...")
        layers_with_none = [
            ("Valid message", "valid.txt"),
            (None, "none.txt"),  # This should be skipped
            ("Another valid message", "valid2.txt")
        ]
        
        none_test_container = create_layered_data_container(layers_with_none)
        none_extracted = extract_layered_data_container(none_test_container)
        
        if len(none_extracted) == 2:  # Should skip the None layer
            print(f"   [OK] None values handled correctly: {len(none_extracted)} valid layers")
        else:
            print(f"   ❌ None value handling failed: {len(none_extracted)} layers")
            return False
        
        print(f"\n✅ ALL TESTS PASSED!")
        print(f"   - Initial container creation: ✅")
        print(f"   - Data extraction: ✅")
        print(f"   - Adding to existing container: ✅")
        print(f"   - Combined container creation: ✅")
        print(f"   - Final extraction: ✅") 
        print(f"   - Data integrity: ✅")
        print(f"   - None value handling: ✅")
        print(f"\n🎉 The NoneType error fix is working perfectly!")
        print(f"Users can now embed multiple files/messages without crashes!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_nonetype_error_scenario()
    if success:
        print("\n🏆 VERIFICATION COMPLETE - FIX IS WORKING!")
    else:
        print("\n💥 VERIFICATION FAILED - NEEDS MORE WORK")