"""
Test extraction from the downloaded steganographic audio file
"""
import sys
import os
sys.path.append(os.getcwd())

from universal_file_audio import UniversalFileAudio

def test_extraction_downloaded():
    print("=== TESTING EXTRACTION FROM DOWNLOADED AUDIO ===")
    
    stego_file = "downloaded_stego_audio.wav"
    password = "test123"
    expected_content = "Secret message via API - audio steganography test!"
    
    if not os.path.exists(stego_file):
        print(f"❌ File not found: {stego_file}")
        return
        
    print(f"Testing extraction from: {stego_file}")
    print(f"Expected content: '{expected_content}'")
    
    try:
        # Create manager with same password
        manager = UniversalFileAudio(password=password)
        
        # Extract data
        result = manager.extract_data(stego_file)
        
        if result:
            extracted_text, filename = result
            print(f"Extracted text: '{extracted_text}'")
            print(f"Extracted filename: '{filename}'")
            
            if extracted_text == expected_content:
                print("\\n🎉 COMPLETE API AUDIO STEGANOGRAPHY TEST PASSED!")
                print("✅ Embedding: SUCCESS")
                print("✅ API workflow: SUCCESS")  
                print("✅ File download: SUCCESS")
                print("✅ Extraction: SUCCESS")
                print("✅ Content verification: SUCCESS")
                return True
            else:
                print("\\n❌ Content mismatch!")
                print(f"   Expected: '{expected_content}'")
                print(f"   Got: '{extracted_text}'")
                return False
        else:
            print("\\n❌ Extraction returned None")
            return False
            
    except Exception as e:
        print(f"\\n❌ Exception during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_extraction_downloaded()