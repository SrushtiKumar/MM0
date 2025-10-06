#!/usr/bin/env python3
"""
Test Large Image with Large Video
"""

import os
from robust_video_stego import RobustVideoSteganographyManager
from pathlib import Path

def test_with_large_video():
    print("🧪 TEST: Large Image with Large Video")
    
    # Create a test image similar to the failing one (15KB)
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
    test_data = jpeg_header + (b'X' * 15000)  # 15KB like the real scenario
    
    test_image_path = Path("large_test_image.jpg")
    with open(test_image_path, "wb") as f:
        f.write(test_data)
    
    print(f"✅ Created large test image: {test_image_path} ({len(test_data)} bytes)")
    
    # Use a large video from outputs
    large_video_path = Path("outputs/a8f990ac-9aa6-49c9-b3bc-b82ed49b1dd6_output_file_example_AVI_1920_2_3MG.avi")
    
    if not large_video_path.exists():
        print("❌ Large video not found")
        return
    
    print(f"📹 Using large video: {large_video_path}")
    
    output_path = Path("test_large_output.avi")
    manager = RobustVideoSteganographyManager()
    
    print("\n🔴 EMBEDDING PHASE:")
    try:
        result = manager.hide_data(str(large_video_path), str(test_image_path), str(output_path), is_file=True)
        print(f"  Embedding success: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"  Frames processed: {result.get('frames_processed')}")
            print(f"  Bits embedded: {result.get('bits_embedded')}")
            print(f"  Payload size: {result.get('payload_size')} bytes")
            print(f"  Redundancy: {result.get('redundancy')}x")
            
            print("\n🔵 EXTRACTION PHASE:")
            extracted_data, extracted_filename = manager.extract_data(str(output_path))
            
            if extracted_data is not None:
                print(f"✅ Extraction successful!")
                print(f"  Filename: {extracted_filename}")
                print(f"  Data size: {len(extracted_data)} bytes")
                
                # Verify data integrity
                if extracted_data == test_data:
                    print("✅ DATA INTEGRITY: Perfect match!")
                else:
                    print("❌ DATA INTEGRITY: Mismatch!")
                    print(f"  Expected size: {len(test_data)}")
                    print(f"  Extracted size: {len(extracted_data)}")
                    
                    # Check if it's a partial match
                    matching_bytes = 0
                    for i in range(min(len(test_data), len(extracted_data))):
                        if test_data[i] == extracted_data[i]:
                            matching_bytes += 1
                        else:
                            break
                    
                    print(f"  Matching bytes from start: {matching_bytes}")
                    
                    if matching_bytes > 100:
                        print("  → Partial success - data corruption during compression")
                    else:
                        print("  → Complete failure - data corruption")
            else:
                print("❌ Extraction failed!")
        else:
            print(f"❌ Embedding failed: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if test_image_path.exists():
            test_image_path.unlink()
        if output_path.exists():
            output_path.unlink()

if __name__ == "__main__":
    test_with_large_video()