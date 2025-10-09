#!/usr/bin/env python3
"""
Test video text steganography specifically
"""

import os
from final_video_steganography import FinalVideoSteganographyManager

def test_video_text_steganography():
    print("🎬 Testing Video Text Steganography")
    
    # Check if we have a video file
    video_files = ['demo_video.mp4', 'test.mp4', 'sample.mp4']
    input_file = None
    
    for video_file in video_files:
        if os.path.exists(video_file):
            input_file = video_file
            break
    
    if not input_file:
        print("❌ No video file found. Let's create a demo video")
        
        # Create demo video
        from final_video_steganography import create_demo_video
        input_file = create_demo_video('test_demo_video.mp4')
        print(f"✅ Created demo video: {input_file}")
    
    print(f"📄 Using video file: {input_file}")
    
    # Test message
    test_message = "Hello Video World! This is a test message for video steganography."
    print(f"📝 Test message: '{test_message}'")
    
    # Create steganography manager
    video_manager = FinalVideoSteganographyManager()
    
    # Create output directory
    os.makedirs('debug_outputs', exist_ok=True)
    output_path = os.path.join('debug_outputs', 'test_video_output.mp4')
    
    try:
        print("\n🔒 HIDING TEXT MESSAGE IN VIDEO...")
        result = video_manager.hide_data(input_file, test_message, output_path)
        
        if result.get('success'):
            print(f"✅ Successfully hidden message in: {result.get('output_path', output_path)}")
            
            print("\n🔓 EXTRACTING TEXT MESSAGE FROM VIDEO...")
            extracted_data, filename = video_manager.extract_data(output_path)
            
            if extracted_data:
                # Convert bytes to text for comparison
                if isinstance(extracted_data, bytes):
                    extracted_message = extracted_data.decode('utf-8')
                else:
                    extracted_message = str(extracted_data)
                    
                print(f"✅ Successfully extracted: '{extracted_message}'")
                
                if extracted_message == test_message:
                    print("🎉 PERFECT MATCH! Video text steganography working correctly.")
                else:
                    print("⚠️ Message extracted but doesn't match exactly")
                    print(f"Original: '{test_message}'")
                    print(f"Extracted: '{extracted_message}'")
                    
                    # Check if it's just truncated or has minor differences
                    if test_message.startswith(extracted_message) or extracted_message.startswith(test_message):
                        print("💡 Looks like partial match - video compression may have affected some data")
            else:
                print(f"❌ Extraction failed: No message returned")
        else:
            print(f"❌ Hiding failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_video_text_steganography()