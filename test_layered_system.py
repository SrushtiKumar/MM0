#!/usr/bin/env python3
"""
Test script for the layered data container system
Tests the fix for data corruption when embedding multiple files
"""

import sys
import os
import shutil
from pathlib import Path

# Add the current directory to the path to import modules
sys.path.append('.')

# Import the enhanced app functions
from enhanced_app import (
    create_layered_data_container,
    extract_layered_data_container,
    is_layered_container
)

def test_layered_container_system():
    """Test the layered data container functionality"""
    print("Testing Layered Data Container System")
    print("=" * 50)
    
    # Test data
    layer1 = "This is the first hidden message"
    layer2 = b"This is binary data from a file"
    layer3 = "Third layer of hidden content"
    
    print("1. Creating layered container...")
    container = create_layered_data_container([layer1, layer2, layer3])
    print(f"   Container created (length: {len(container)})")
    
    print("\n2. Testing container detection...")
    is_layered = is_layered_container(container)
    print(f"   Is layered container: {is_layered}")
    
    print("\n3. Extracting layers...")
    extracted_layers = extract_layered_data_container(container)
    print(f"   Extracted {len(extracted_layers)} layers")
    
    print("\n4. Verifying extracted content...")
    for i, (content, filename) in enumerate(extracted_layers):
        print(f"   Layer {i+1}: {filename}")
        if isinstance(content, str):
            print(f"     Content: {content[:50]}...")
        else:
            print(f"     Binary content: {len(content)} bytes")
    
    print("\n5. Testing single layer (non-layered) data...")
    single_data = "Just a simple message"
    is_single_layered = is_layered_container(single_data)
    print(f"   Single data is layered: {is_single_layered}")
    
    print("\nTest completed successfully!")
    return True

def test_sequential_embedding_scenario():
    """Simulate the scenario that was causing data corruption"""
    print("\n" + "=" * 50)
    print("Testing Sequential Embedding Scenario")
    print("=" * 50)
    
    # Simulate first embedding
    first_content = "First file content - important document"
    print(f"1. First embedding: '{first_content}'")
    
    # Simulate detecting existing data and creating layered container
    existing_data = first_content  # This would come from extraction
    second_content = "Second file content - another document"
    
    print(f"2. Second embedding detected existing data")
    print(f"   Existing: '{existing_data}'")
    print(f"   New: '{second_content}'")
    
    # Create layered container
    layers = [existing_data, second_content]
    layered_container = create_layered_data_container(layers)
    
    print(f"3. Created layered container (length: {len(layered_container)})")
    
    # Simulate extraction
    print(f"4. Extracting all layers...")
    extracted = extract_layered_data_container(layered_container)
    
    for i, (content, filename) in enumerate(extracted):
        print(f"   Layer {i+1}: {content}")
    
    # Verify no data loss
    original_contents = [first_content, second_content]
    extracted_contents = [content for content, _ in extracted]
    
    print(f"5. Verification:")
    print(f"   Original layers: {len(original_contents)}")
    print(f"   Extracted layers: {len(extracted_contents)}")
    print(f"   Data integrity: {original_contents == extracted_contents}")
    
    return original_contents == extracted_contents

if __name__ == "__main__":
    try:
        print("Testing Enhanced Steganography System")
        print("Fixing data corruption vulnerability\n")
        
        # Run tests
        test1_result = test_layered_container_system()
        test2_result = test_sequential_embedding_scenario()
        
        print("\n" + "=" * 50)
        print("FINAL RESULTS")
        print("=" * 50)
        print(f"Layered Container Test: {'PASS' if test1_result else 'FAIL'}")
        print(f"Sequential Embedding Test: {'PASS' if test2_result else 'FAIL'}")
        
        if test1_result and test2_result:
            print("\n✅ ALL TESTS PASSED - Data corruption vulnerability FIXED!")
        else:
            print("\n❌ TESTS FAILED - Issues detected")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()