#!/usr/bin/env python3
"""
Direct test of the final video steganography implementation
"""

from final_web_video_text_stego import FinalWebVideoTextSteganographyManager
import cv2
import numpy as np


def test_final_implementation_directly():
    """Test the final implementation directly without web server"""
    print("🎬 Direct Test of Final Video Steganography Implementation")
    
    # Create test video
    test_video = 'direct_test_video.mp4'
    print(f"Creating test video: {test_video}")
    
    width, height = 320, 240
    fps = 10
    frames = 20
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video, fourcc, fps, (width, height))
    
    for i in range(frames):
        frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        # Add some structure
        cv2.rectangle(frame, (10, 10), (50, 50), (255, 255, 255), 2)
        cv2.putText(frame, f'F{i}', (60, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        out.write(frame)
    
    out.release()
    print("✅ Test video created")
    
    # Test messages
    test_messages = [
        "Hello World!",
        "This is a longer message to test the capability of the video steganography system.",
        "Special chars: !@#$%^&*()_+{}[]|\\:;'\"<>?,./"
    ]
    
    manager = FinalWebVideoTextSteganographyManager()
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*50}")
        print(f"Test {i}: {message[:30]}{'...' if len(message) > 30 else ''}")
        print(f"{'='*50}")
        
        output_file = f'direct_test_output_{i}.mp4'
        
        # Hide message
        print(f"🔒 Hiding message...")
        result = manager.hide_data(test_video, message, output_file)
        
        if result.get('success'):
            print(f"✅ Hide successful")
            
            # Extract message
            print(f"🔓 Extracting message...")
            extracted_bytes, filename = manager.extract_data(output_file)
            
            if extracted_bytes:
                extracted_text = extracted_bytes.decode('utf-8')
                print(f"✅ Extraction successful")
                print(f"   Original:  '{message}'")
                print(f"   Extracted: '{extracted_text}'")
                
                if extracted_text == message:
                    print("🎉 PERFECT MATCH!")
                else:
                    print("❌ MISMATCH!")
                    return False
            else:
                print("❌ Extraction failed")
                return False
        else:
            print(f"❌ Hide failed: {result.get('error')}")
            return False
    
    print(f"\n🎉 ALL TESTS PASSED! The final implementation works perfectly!")
    return True


if __name__ == "__main__":
    test_final_implementation_directly()