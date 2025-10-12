#!/usr/bin/env python3
"""
Standalone MP3 Extraction Tool
Works directly with steganography modules without backend
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from enhanced_web_video_stego import EnhancedWebVideoStego
    print("✅ Video steganography module loaded")
except ImportError as e:
    print(f"❌ Failed to load video steganography: {e}")
    sys.exit(1)

def extract_mp3_from_video(stego_video_path, password, output_path=None):
    """
    Extract MP3 file from steganographic video
    
    Args:
        stego_video_path: Path to video with hidden MP3
        password: Password used for extraction
        output_path: Optional output path for extracted file
    
    Returns:
        dict: Extraction results
    """
    try:
        print(f"🔍 Extracting from: {stego_video_path}")
        
        # Initialize steganography module
        stego = EnhancedWebVideoStego()
        
        # Extract data
        result = stego.extract_data_from_video(stego_video_path, password)
        
        if not result['success']:
            return {'success': False, 'error': result.get('message', 'Extraction failed')}
        
        extracted_data = result['data']
        filename = result['filename']
        
        # Determine output filename
        if output_path:
            output_file = output_path
        else:
            # Use original filename or default to .mp3
            if filename and filename != 'extracted_data':
                output_file = filename
            else:
                output_file = 'extracted_audio.mp3'
        
        # Ensure .mp3 extension for audio files
        if isinstance(extracted_data, bytes) and extracted_data.startswith(b'ID3'):
            if not output_file.endswith('.mp3'):
                output_file = os.path.splitext(output_file)[0] + '.mp3'
        
        # Save extracted file
        with open(output_file, 'wb') as f:
            if isinstance(extracted_data, bytes):
                f.write(extracted_data)
            else:
                f.write(extracted_data.encode() if isinstance(extracted_data, str) else str(extracted_data).encode())
        
        file_size = os.path.getsize(output_file)
        
        # Verify it's a valid MP3
        is_mp3 = False
        with open(output_file, 'rb') as f:
            header = f.read(10)
            is_mp3 = header.startswith(b'ID3') or header[0:2] == b'\xff\xfb'
        
        return {
            'success': True,
            'output_file': output_file,
            'file_size': file_size,
            'is_mp3': is_mp3,
            'original_filename': filename
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    if len(sys.argv) < 3:
        print("Usage: python standalone_mp3_extractor.py <stego_video> <password> [output_file]")
        print("Example: python standalone_mp3_extractor.py debug_video_with_mp3.mp4 test123")
        sys.exit(1)
    
    stego_video = sys.argv[1]
    password = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(stego_video):
        print(f"❌ Error: File not found: {stego_video}")
        sys.exit(1)
    
    print("🎵 Standalone MP3 Extractor")
    print("=" * 50)
    
    result = extract_mp3_from_video(stego_video, password, output_file)
    
    if result['success']:
        print(f"✅ Extraction successful!")
        print(f"   Output file: {result['output_file']}")
        print(f"   File size: {result['file_size']} bytes")
        print(f"   Valid MP3: {'Yes' if result['is_mp3'] else 'No'}")
        print(f"   Original filename: {result['original_filename']}")
        
        if result['is_mp3']:
            print(f"🎶 Your MP3 file is ready: {result['output_file']}")
        else:
            print(f"⚠️  Warning: Extracted file may not be a valid MP3")
    else:
        print(f"❌ Extraction failed: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()