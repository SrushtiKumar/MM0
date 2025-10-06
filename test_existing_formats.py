#!/usr/bin/env python3
"""
Test MP3 format preservation with existing files
"""

import os
from final_audio_stego import FinalAudioSteganographyManager

def test_format_preservation_with_existing_files():
    """Test format preservation with files that actually exist."""
    print("=== Testing Format Preservation ===")
    
    # Find existing audio files
    audio_files = []
    for ext in ['.mp3', '.wav']:
        files = [f for f in os.listdir('.') if f.lower().endswith(ext)]
        audio_files.extend([(f, ext.lstrip('.')) for f in files])
    
    print(f"Found {len(audio_files)} audio files:")
    for filename, format_type in audio_files:
        print(f"  {filename} ({format_type.upper()})")
    
    if not audio_files:
        print("❌ No audio files found for testing")
        return False
    
    # Test with each file type
    manager = FinalAudioSteganographyManager("test123")
    test_message = "Testing format preservation! 🎵"
    
    results = []
    
    for filename, format_type in audio_files[:2]:  # Test first 2 files
        try:
            print(f"\n--- Testing {filename} ({format_type.upper()}) ---")
            
            output_file = f"test_preserve_{format_type}.{format_type}"
            
            # Embed
            result = manager.hide_data(filename, test_message, output_file)
            actual_output = result.get('output_path', output_file)
            actual_ext = os.path.splitext(actual_output)[1].lower().lstrip('.')
            
            print(f"Input format: {format_type.upper()}")
            print(f"Expected output format: {format_type.upper()}")
            print(f"Actual output: {actual_output}")
            print(f"Actual format: {actual_ext.upper()}")
            
            format_preserved = actual_ext == format_type
            print(f"Format preserved: {'✅ YES' if format_preserved else '❌ NO'}")
            
            # Test extraction if file exists
            if os.path.exists(actual_output):
                try:
                    extracted_data, extracted_filename = manager.extract_data(actual_output)
                    extracted_text = extracted_data.decode('utf-8')
                    content_match = extracted_text == test_message
                    print(f"Content match: {'✅ YES' if content_match else '❌ NO'}")
                    
                    # Cleanup
                    os.unlink(actual_output)
                    
                    results.append((filename, format_type, format_preserved, content_match))
                except Exception as e:
                    print(f"❌ Extraction failed: {e}")
                    results.append((filename, format_type, format_preserved, False))
            else:
                print(f"❌ Output file not found: {actual_output}")
                results.append((filename, format_type, False, False))
                
        except Exception as e:
            print(f"❌ Test failed for {filename}: {e}")
            results.append((filename, format_type, False, False))
    
    # Summary
    print(f"\n=== Results Summary ===")
    for filename, format_type, format_preserved, content_match in results:
        status = "✅ PASS" if (format_preserved and content_match) else "❌ FAIL"
        print(f"{filename} ({format_type.upper()}): {status}")
        if not format_preserved:
            print(f"  - Format not preserved")
        if not content_match:
            print(f"  - Content extraction failed")
    
    all_passed = all(fp and cm for _, _, fp, cm in results)
    return all_passed

if __name__ == "__main__":
    success = test_format_preservation_with_existing_files()
    print(f"\n🎉 Overall test {'PASSED' if success else 'FAILED'}!")