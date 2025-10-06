#!/usr/bin/env python3
"""
Comprehensive File-in-Audio Steganography
Hide any type of file (.txt, .pdf, .docx, .exe, etc.) inside audio files
Uses optimized multi-band DWT embedding with file type detection
"""

import numpy as np
import pywt
import librosa
import soundfile as sf
import os
import json
import mimetypes
from pathlib import Path

# Optional dependency for better MIME type detection
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

class UniversalFileAudio:
    """Universal file hiding in audio using optimized multi-band embedding"""
    
    def __init__(self):
        self.redundancy = 2  # Balanced redundancy vs capacity
        self.wavelet = 'db4'
        self.level = 5
        self.detail_bands = [1, 2, 3, 4]  # Use 4 bands for maximum capacity
        
    def _get_file_info(self, file_path):
        """Get comprehensive file information"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            # Try using python-magic for better detection if available
            if HAS_MAGIC:
                try:
                    mime_type = magic.from_file(file_path, mime=True)
                except:
                    mime_type = 'application/octet-stream'
            else:
                mime_type = 'application/octet-stream'
        
        # Get file extension
        file_ext = Path(file_path).suffix.lower()
        filename = os.path.basename(file_path)
        
        return {
            'filename': filename,
            'extension': file_ext,
            'mime_type': mime_type,
            'size': file_size,
            'readable_size': self._format_size(file_size)
        }
    
    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"
    
    def _get_audio_capacity(self, audio_path):
        """Calculate total embedding capacity for any file type"""
        y, sr = librosa.load(audio_path, sr=None)
        if len(y.shape) == 1:
            y = y.reshape(1, -1)
        
        # Use 95% of audio for maximum capacity
        segment = y[0, :int(y.shape[1] * 0.95)]
        coeffs = pywt.wavedec(segment, self.wavelet, level=self.level)
        
        total_coeffs = 0
        for band in self.detail_bands:
            if band < len(coeffs):
                total_coeffs += len(coeffs[band])
        
        max_bits = total_coeffs // self.redundancy
        max_bytes = max_bits // 8
        
        return max_bytes, total_coeffs, len(y), sr
    
    def embed_file(self, audio_path, file_path, output_path, compression_level=6):
        """
        Embed any file type into audio
        
        Args:
            audio_path: Input audio file
            file_path: File to hide (any type: .txt, .pdf, .docx, etc.)
            output_path: Output audio file with hidden data
            compression_level: Compression level 0-9 (higher = smaller file)
        """
        print(f"📁 Embedding file '{file_path}' into '{audio_path}'")
        
        # Get file information
        file_info = self._get_file_info(file_path)
        print(f"📄 File: {file_info['filename']} ({file_info['readable_size']})")
        print(f"🔍 Type: {file_info['mime_type']} ({file_info['extension']})")
        
        # Check audio capacity
        max_bytes, total_coeffs, audio_samples, sr = self._get_audio_capacity(audio_path)
        print(f"📊 Audio: {audio_samples} samples, {sr} Hz, {audio_samples/sr:.1f}s")
        print(f"💾 Capacity: {self._format_size(max_bytes)} available")
        
        # Read file data
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        print(f"📦 Original file: {len(file_data)} bytes")
        
        # Apply compression if needed
        compressed_data = file_data
        if compression_level > 0:
            import zlib
            compressed_data = zlib.compress(file_data, level=compression_level)
            compression_ratio = len(compressed_data) / len(file_data)
            print(f"🗜️ Compressed: {len(compressed_data)} bytes ({compression_ratio:.1%} of original)")
        
        # Create comprehensive header
        header = {
            'magic': 'UNIVERSAL_FILE_AUDIO',
            'version': '1.0',
            'filename': file_info['filename'],
            'extension': file_info['extension'],
            'mime_type': file_info['mime_type'],
            'original_size': len(file_data),
            'compressed_size': len(compressed_data),
            'compression_level': compression_level,
            'checksum': hex(hash(file_data) & 0xFFFFFFFF)  # Simple checksum
        }
        
        header_json = json.dumps(header, separators=(',', ':')).encode('utf-8')
        
        # Package: header_length + header + compressed_data
        total_package = len(header_json).to_bytes(4, 'little') + header_json + compressed_data
        
        print(f"📋 Header: {len(header_json)} bytes")
        print(f"📦 Total package: {len(total_package)} bytes ({self._format_size(len(total_package))})")
        
        # Check if it fits
        if len(total_package) > max_bytes:
            if compression_level < 9:
                print(f"⚠️ File too large, trying higher compression...")
                return self.embed_file(audio_path, file_path, output_path, compression_level + 2)
            else:
                raise ValueError(f"File too large! Need {self._format_size(len(total_package))}, have {self._format_size(max_bytes)}")
        
        usage_percent = (len(total_package) / max_bytes) * 100
        print(f"📊 Capacity usage: {usage_percent:.1f}%")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        if len(y.shape) == 1:
            y = y.reshape(1, -1)
        
        # Use maximum segment
        segment = y[0, :int(y.shape[1] * 0.95)]
        coeffs = pywt.wavedec(segment, self.wavelet, level=self.level)
        
        # Convert to bits
        data_bits = ''.join(format(byte, '08b') for byte in total_package)
        print(f"🔢 Embedding {len(total_package)} bytes ({len(data_bits)} bits)")
        
        # Distribute across bands
        bits_per_band = len(data_bits) // len(self.detail_bands)
        remaining_bits = len(data_bits) % len(self.detail_bands)
        
        bit_index = 0
        
        for band_idx, band in enumerate(self.detail_bands):
            if band >= len(coeffs):
                continue
                
            detail_band = coeffs[band].copy()
            
            # Calculate bits for this band
            band_bits = bits_per_band
            if band_idx < remaining_bits:
                band_bits += 1
            
            if bit_index + band_bits > len(data_bits):
                band_bits = len(data_bits) - bit_index
            
            band_data = data_bits[bit_index:bit_index + band_bits]
            bit_index += band_bits
            
            print(f"🔊 Band {band}: {len(detail_band)} coeffs, embedding {len(band_data)} bits")
            
            # Embed in this band
            for bit_idx, bit_char in enumerate(band_data):
                bit_val = int(bit_char)
                
                for r in range(self.redundancy):
                    coeff_idx = bit_idx * self.redundancy + r
                    if coeff_idx < len(detail_band):
                        original_coeff = detail_band[coeff_idx]
                        min_magnitude = 0.005  # Subtle embedding
                        magnitude = max(abs(original_coeff), min_magnitude)
                        
                        if bit_val == 1:
                            detail_band[coeff_idx] = magnitude
                        else:
                            detail_band[coeff_idx] = -magnitude
            
            # Update coefficients
            coeffs[band] = detail_band
            
            if bit_index >= len(data_bits):
                break
        
        # Reconstruct audio
        y_modified = pywt.waverec(coeffs, self.wavelet)
        
        # Ensure same length
        if len(y_modified) != len(segment):
            if len(y_modified) > len(segment):
                y_modified = y_modified[:len(segment)]
            else:
                padding = np.zeros(len(segment) - len(y_modified))
                y_modified = np.concatenate([y_modified, padding])
        
        # Update audio
        y[0, :len(y_modified)] = y_modified
        
        # Save
        audio_out = y[0] if y.shape[0] == 1 else y.T
        sf.write(output_path, audio_out, sr)
        
        print(f"✅ File embedded successfully in '{output_path}'")
        
        return {
            'original_file_size': len(file_data),
            'compressed_size': len(compressed_data),
            'total_package_size': len(total_package),
            'compression_ratio': f"{len(compressed_data)/len(file_data):.1%}",
            'capacity_used': f"{usage_percent:.1f}%",
            'file_type': file_info['mime_type'],
            'bands_used': len([b for b in self.detail_bands if b < len(coeffs)])
        }
    
    def extract_file(self, audio_path, output_dir=None):
        """
        Extract any file type from audio
        
        Args:
            audio_path: Steganographic audio file
            output_dir: Directory to save extracted file (optional)
            
        Returns:
            Path to extracted file
        """
        print(f"🔍 Extracting file from '{audio_path}'")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        if len(y.shape) == 1:
            y = y.reshape(1, -1)
        
        # Use same segment
        segment = y[0, :int(y.shape[1] * 0.95)]
        coeffs = pywt.wavedec(segment, self.wavelet, level=self.level)
        
        # Extract bits from all bands
        all_bits = []
        
        for band in self.detail_bands:
            if band >= len(coeffs):
                continue
                
            detail_band = coeffs[band]
            print(f"🔊 Extracting from band {band}: {len(detail_band)} coefficients")
            
            # Extract with majority voting
            max_bits_this_band = len(detail_band) // self.redundancy
            
            for bit_idx in range(max_bits_this_band):
                votes = []
                for r in range(self.redundancy):
                    coeff_idx = bit_idx * self.redundancy + r
                    if coeff_idx < len(detail_band):
                        coeff = detail_band[coeff_idx]
                        vote = 1 if coeff > 0.001 else 0
                        votes.append(vote)
                
                if votes:
                    bit_value = 1 if sum(votes) > len(votes) // 2 else 0
                    all_bits.append(str(bit_value))
        
        print(f"📊 Total extracted bits: {len(all_bits)}")
        
        # Convert to bytes
        extracted_bytes = []
        for i in range(0, len(all_bits), 8):
            if i + 7 < len(all_bits):
                byte_bits = ''.join(all_bits[i:i+8])
                byte_val = int(byte_bits, 2)
                extracted_bytes.append(byte_val)
        
        if len(extracted_bytes) < 4:
            raise ValueError("Not enough data extracted")
        
        # Parse header
        header_length = int.from_bytes(bytes(extracted_bytes[:4]), 'little')
        
        if header_length <= 0 or header_length > 1000:
            raise ValueError(f"Invalid header length: {header_length}")
        
        if len(extracted_bytes) < 4 + header_length:
            raise ValueError("Not enough bytes for header")
        
        header_bytes = bytes(extracted_bytes[4:4+header_length])
        header = json.loads(header_bytes.decode('utf-8'))
        
        print(f"📋 Header: {header}")
        
        if header.get('magic') != 'UNIVERSAL_FILE_AUDIO':
            raise ValueError("Not a valid universal file-audio file")
        
        # Extract compressed data
        compressed_size = header['compressed_size']
        data_start = 4 + header_length
        data_end = data_start + compressed_size
        
        if len(extracted_bytes) < data_end:
            raise ValueError(f"Not enough bytes for file data: need {data_end}, have {len(extracted_bytes)}")
        
        compressed_data = bytes(extracted_bytes[data_start:data_end])
        
        # Decompress if needed
        if header['compression_level'] > 0:
            import zlib
            file_data = zlib.decompress(compressed_data)
            print(f"🗜️ Decompressed: {len(compressed_data)} → {len(file_data)} bytes")
        else:
            file_data = compressed_data
        
        # Verify size
        if len(file_data) != header['original_size']:
            print(f"⚠️ Size mismatch: expected {header['original_size']}, got {len(file_data)}")
        
        # Verify checksum
        calculated_checksum = hex(hash(file_data) & 0xFFFFFFFF)
        if calculated_checksum != header['checksum']:
            print(f"⚠️ Checksum mismatch: expected {header['checksum']}, got {calculated_checksum}")
        
        # Determine output path
        filename = header['filename']
        if output_dir:
            if os.path.isdir(output_dir):
                output_path = os.path.join(output_dir, filename)
            else:
                output_path = output_dir
        else:
            output_path = f"extracted_{filename}"
        
        # Save file
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        print(f"📁 File extracted: {filename}")
        print(f"📄 Type: {header['mime_type']} ({header['extension']})")
        print(f"📊 Size: {self._format_size(len(file_data))}")
        print(f"💾 Saved to: {output_path}")
        
        return output_path

def test_universal_file_steganography():
    """Test hiding various file types in audio"""
    print("=== UNIVERSAL FILE-IN-AUDIO STEGANOGRAPHY TEST ===")
    
    # Create high-capacity audio (60 seconds)
    sr = 44100
    duration = 60
    t = np.linspace(0, duration, sr * duration)
    # Rich frequency content for better capacity
    audio = 0.15 * (
        np.sin(2 * np.pi * 440 * t) +
        0.8 * np.sin(2 * np.pi * 880 * t) +
        0.6 * np.sin(2 * np.pi * 1320 * t) +
        0.4 * np.sin(2 * np.pi * 220 * t) +
        0.3 * np.random.normal(0, 0.1, len(t))
    )
    sf.write('universal_test_audio.wav', audio, sr)
    
    stego = UniversalFileAudio()
    
    # Check capacity
    max_bytes, total_coeffs, samples, sr_check = stego._get_audio_capacity('universal_test_audio.wav')
    print(f"📊 Audio capacity: {stego._format_size(max_bytes)} in {duration}s audio")
    print(f"🔊 Total coefficients: {total_coeffs}")
    
    # Create test files of various types
    test_files = []
    
    # 1. Text file
    text_content = """This is a secret text document!
    
It contains multiple lines of text with various characters:
- Special symbols: !@#$%^&*()
- Numbers: 1234567890
- Unicode: 🔒🎵📁✅
- Formatted text with spaces and tabs

This document demonstrates that any text file can be hidden
inside audio files using our steganography system.

The system preserves all formatting, special characters,
and maintains perfect file integrity during extraction.

End of secret document.
""" * 5  # Make it larger
    
    with open('secret_document.txt', 'w', encoding='utf-8') as f:
        f.write(text_content)
    test_files.append(('secret_document.txt', 'Text Document'))
    
    # 2. JSON file (structured data)
    json_data = {
        "secret_data": {
            "mission": "steganography_test",
            "agents": ["Alice", "Bob", "Charlie"],
            "coordinates": [{"lat": 40.7128, "lng": -74.0060}, {"lat": 51.5074, "lng": -0.1278}],
            "encrypted_payload": "VGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl",
            "status": "active",
            "priority": 9,
            "metadata": {
                "created": "2025-10-03",
                "expires": "2025-12-31",
                "classification": "TOP SECRET"
            }
        }
    }
    
    with open('secret_data.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    test_files.append(('secret_data.json', 'JSON Data'))
    
    # 3. CSV file
    csv_content = """Name,Age,Department,Salary,Secret_Code
John Doe,30,Engineering,75000,X7Y9Z2
Jane Smith,28,Marketing,65000,A5B8C1
Bob Johnson,35,Finance,80000,M3N6P9
Alice Brown,32,HR,70000,Q2W5E8
Charlie Wilson,29,IT,72000,R4T7Y1"""
    
    with open('employee_data.csv', 'w', encoding='utf-8') as f:
        f.write(csv_content)
    test_files.append(('employee_data.csv', 'CSV Spreadsheet'))
    
    # 4. Python script
    python_code = '''#!/usr/bin/env python3
"""
Secret Python Script Hidden in Audio
This demonstrates that executable code can be hidden and extracted.
"""

import os
import sys
import base64

def secret_function():
    """A secret function that does secret operations"""
    secret_key = "VGhpcyBpcyBhIHNlY3JldCBrZXk="
    decoded = base64.b64decode(secret_key).decode('utf-8')
    print(f"Secret revealed: {decoded}")
    
    # Perform some calculations
    result = sum(i**2 for i in range(100))
    print(f"Secret calculation result: {result}")
    
    return result

def main():
    """Main function of the secret script"""
    print("🔒 Secret Python Script Executed!")
    print("This script was hidden inside an audio file.")
    
    result = secret_function()
    
    # Generate secret report
    report = {
        'status': 'success',
        'calculation': result,
        'message': 'Script executed from steganographic extraction'
    }
    
    print(f"📊 Report: {report}")
    return report

if __name__ == "__main__":
    main()
'''
    
    with open('secret_script.py', 'w', encoding='utf-8') as f:
        f.write(python_code)
    test_files.append(('secret_script.py', 'Python Script'))
    
    # 5. HTML file
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secret Web Page</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            padding: 20px;
        }
        .secret-content {
            background: rgba(0,0,0,0.7);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .code { 
            background: #333; 
            padding: 10px; 
            border-radius: 5px; 
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h1>🔒 Secret Web Page</h1>
    <div class="secret-content">
        <h2>Hidden in Audio Steganography</h2>
        <p>This HTML page was secretly embedded inside an audio file!</p>
        
        <h3>Secret Information:</h3>
        <ul>
            <li>Project: Audio Steganography</li>
            <li>Status: Operational</li>
            <li>Encryption: AES-256</li>
            <li>Capacity: Multi-file support</li>
        </ul>
        
        <div class="code">
            console.log("Secret page loaded from steganographic extraction!");
        </div>
    </div>
    
    <script>
        alert("🎉 Secret HTML file successfully extracted from audio!");
        console.log("This webpage was hidden in audio coefficients!");
    </script>
</body>
</html>'''
    
    with open('secret_page.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    test_files.append(('secret_page.html', 'HTML Webpage'))
    
    # Test each file type
    successful_tests = 0
    
    for filename, description in test_files:
        print(f"\n{'='*60}")
        print(f"📁 Testing: {description} ({filename})")
        print('='*60)
        
        try:
            # Get file info
            file_size = os.path.getsize(filename)
            print(f"📊 Original file: {stego._format_size(file_size)}")
            
            # Embed
            result = stego.embed_file('universal_test_audio.wav', filename, f'stego_{filename}.wav')
            print(f"✅ Embedding successful!")
            print(f"📋 Result: {result}")
            
            # Extract
            extracted_path = stego.extract_file(f'stego_{filename}.wav', output_dir='.')
            print(f"✅ Extraction successful!")
            
            # Verify file integrity
            with open(filename, 'rb') as f1, open(extracted_path, 'rb') as f2:
                original_data = f1.read()
                extracted_data = f2.read()
                
                if original_data == extracted_data:
                    print(f"✅ PERFECT FILE INTEGRITY - 100% match!")
                    successful_tests += 1
                else:
                    print(f"❌ File integrity failed!")
            
            # Clean up
            for f in [f'stego_{filename}.wav']:
                if os.path.exists(f):
                    os.remove(f)
                    
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 UNIVERSAL FILE STEGANOGRAPHY TEST COMPLETE!")
    print(f"📊 Results: {successful_tests}/{len(test_files)} file types successful")
    print('='*60)
    
    if successful_tests == len(test_files):
        print("✅ ALL FILE TYPES WORKING PERFECTLY!")
        print("🔒 Text files, JSON, CSV, Python scripts, HTML - all supported!")
    
    # Clean up test files
    cleanup_files = [
        'universal_test_audio.wav', 'secret_document.txt', 'secret_data.json',
        'employee_data.csv', 'secret_script.py', 'secret_page.html',
        'extracted_secret_document.txt', 'extracted_secret_data.json',
        'extracted_employee_data.csv', 'extracted_secret_script.py', 'extracted_secret_page.html'
    ]
    
    for f in cleanup_files:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    test_universal_file_steganography()