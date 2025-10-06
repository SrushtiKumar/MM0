#!/usr/bin/env python3
"""
Test Large Image in Video - Web Application Scenario
"""

import os
from robust_video_stego import RobustVideoSteganographyManager
from pathlib import Path

def test_large_image_scenario():
    print("🧪 TEST: Large Image in Video (Web App Scenario)")
    
    # Create a larger test image (similar to the 15KB image that's failing)
    # This simulates a real JPEG header + some data
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
    test_data = jpeg_header + (b'A' * 15000)  # 15KB+ like the real scenario
    
    test_image_path = Path("large_test_image.jpg")
    with open(test_image_path, "wb") as f:
        f.write(test_data)
    
    print(f"✅ Created large test image: {test_image_path} ({len(test_data)} bytes)")
    
    # Use existing video files
    video_files = list(Path(".").glob("*.mp4")) + list(Path(".").glob("*.avi"))
    if not video_files:
        print("❌ No video files found for testing")
        return
    
    # Test with different video sizes
    for video_path in video_files[:2]:  # Test first 2 videos
        print(f"\n📹 Testing with: {video_path}")
        
        output_path = Path(f"test_output_{video_path.stem}.mp4")
        manager = RobustVideoSteganographyManager()
        
        print("\n🔴 EMBEDDING PHASE:")
        try:
            result = manager.hide_data(str(video_path), str(test_image_path), str(output_path), is_file=True)
            print(f"  Result: {result.get('success', False)}")
            
            if result.get('success'):
                frames_needed = result.get('bits_embedded', 0) // result.get('redundancy', 1) // 8 // 3000
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
                        # Check first few bytes
                        print(f"  Expected first 20 bytes: {test_data[:20]}")
                        print(f"  Extracted first 20 bytes: {extracted_data[:20]}")
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
            if output_path.exists():
                output_path.unlink()
    
    # Cleanup
    if test_image_path.exists():
        test_image_path.unlink()

if __name__ == "__main__":
    test_large_image_scenario()