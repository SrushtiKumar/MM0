"""
Direct Audio Module Test - Verify Audio Steganography Preserves Filenames
"""
from universal_file_audio import UniversalFileAudio
import os

def test_audio_module():
    print("🔧 DIRECT AUDIO MODULE TEST")
    print("=" * 35)
    
    try:
        manager = UniversalFileAudio(password='test123')
        
        # Create test Python file
        with open('direct_module_test.py', 'w') as f:
            f.write('#!/usr/bin/env python3\n')
            f.write('# This is a test Python script\n')
            f.write('print("Testing filename preservation!")\n')
            f.write('def main():\n')
            f.write('    return "Success!"\n')
        
        print("✅ Test Python file created")
        
        # Read carrier file
        with open('test_audio.wav', 'rb') as carrier:
            carrier_data = carrier.read()
            
        # Read content file  
        with open('direct_module_test.py', 'rb') as content:
            content_data = content.read()
        
        print("✅ Files loaded successfully")
        
        # Embed using module directly (with explicit filename)
        print("🔄 Embedding data with filename 'direct_module_test.py'...")
        result = manager.hide_data(carrier_data, content_data, 'direct_module_test.py')
        
        # Save result
        with open('direct_audio_result.wav', 'wb') as f:
            f.write(result)
        
        print("✅ Embedding completed, saved to direct_audio_result.wav")
        
        # Extract using module directly
        print("🔄 Extracting data...")
        with open('direct_audio_result.wav', 'rb') as f:
            stego_data = f.read()
        
        extracted_data, extracted_filename = manager.extract_data(stego_data)
        
        print(f"📄 Extracted filename: '{extracted_filename}'")
        print(f"📊 Extracted data size: {len(extracted_data) if extracted_data else 0} bytes")
        
        # Check results
        if extracted_filename:
            if extracted_filename == 'direct_module_test.py':
                print("🎯 PERFECT: Exact filename match!")
            elif extracted_filename.endswith('.py'):
                print(f"✅ GOOD: Python extension preserved ({extracted_filename})")
            elif extracted_filename.endswith('.txt'):
                print("❌ FAILED: Converted to .txt extension (old bug)")
            else:
                print(f"❓ UNEXPECTED: Different extension ({extracted_filename})")
        else:
            print("❌ FAILED: No filename returned")
        
        # Save extracted data to verify content
        if extracted_data:
            with open('extracted_direct_test.py', 'wb') as f:
                f.write(extracted_data)
            print("✅ Extracted data saved for verification")
            
            # Try to read and verify content
            try:
                with open('extracted_direct_test.py', 'r') as f:
                    content = f.read()
                    if 'Testing filename preservation!' in content:
                        print("🎯 CONTENT VERIFICATION: Data integrity preserved!")
                    else:
                        print("❓ Content may have been altered")
            except Exception as e:
                print(f"❓ Could not read extracted content: {e}")
        else:
            print("❌ FAILED: No data extracted")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 35)
    print("🏁 AUDIO MODULE TEST COMPLETE")
    print("=" * 35)

if __name__ == "__main__":
    test_audio_module()