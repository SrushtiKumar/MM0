import sys
import os
sys.path.append(os.getcwd())

from universal_file_audio import UniversalFileAudio

def test_updated_audio_directly():
    """Test the updated audio steganography directly"""
    print("Testing updated UniversalFileAudio class...")
    
    audio_path = 'test_audio_carrier.wav'
    if not os.path.exists(audio_path):
        print(f"Audio file {audio_path} not found")
        return
    
    # Test with the updated class
    stego = UniversalFileAudio(password="test123")
    
    # Test hide_data method
    result = stego.hide_data(
        carrier_file_path=audio_path,
        content_to_hide="Hi",
        output_path="test_updated_audio.wav",
        is_file=False
    )
    
    print(f"Hide result: {result}")
    
    if result.get('success'):
        # Test extract_data method
        extract_result = stego.extract_data("test_updated_audio.wav")
        
        if extract_result:
            text, filename = extract_result
            print(f"Extracted: '{text}' (filename: {filename})")
            
            if text == "Hi":
                print("✅ Updated audio steganography test PASSED")
            else:
                print(f"❌ Content mismatch - Expected: 'Hi', Got: '{text}'")
        else:
            print("❌ Extraction returned None")
    else:
        print(f"❌ Hide failed: {result.get('error')}")

if __name__ == "__main__":
    test_updated_audio_directly()