#!/usr/bin/env python3
"""Fixed Video Steganography Implementation"""

import cv2
import numpy as np
import struct
import hashlib
import os
from stego_cli import CryptoHandler, StegoError

class FixedVideoSteganography:
    """Simple but reliable video steganography"""
    
    def __init__(self, password=None):
        self.password = password
    
    def embed_file_in_video(self, video_path, file_path, output_path):
        """Embed a file in video using reliable technique"""
        
        print(f"🎬 Fixed Video Steganography - Embedding")
        print(f"📹 Input video: {video_path}")
        print(f"📄 File to hide: {file_path}")
        print(f"💾 Output: {output_path}")
        
        # Read the file to hide
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        filename = os.path.basename(file_path)
        print(f"📄 Filename: {filename}")
        print(f"📊 File size: {len(file_data)} bytes")
        
        # Prepare data for embedding (encrypt if password available)
        if self.password:
            print(f"🔐 Encrypting file data...")
            crypto = CryptoHandler(self.password)
            ciphertext, nonce = crypto.encrypt(file_data)
            # Include salt and nonce for decryption - use 32-byte salt as in CryptoHandler
            payload_data = crypto.salt + nonce + ciphertext
        else:
            payload_data = file_data
        
        # Create simple binary header for reliability - store actual payload size
        magic = b"FIXED024"  # 8 bytes magic number
        size_bytes = struct.pack('<I', len(payload_data))  # 4 bytes payload size (encrypted or original)
        checksum = hashlib.md5(file_data).digest()[:4]  # 4 bytes MD5 checksum (of original data)
        filename_len = struct.pack('<H', len(filename.encode()))  # 2 bytes filename length
        filename_bytes = filename.encode()  # Variable length filename
        
        header = magic + size_bytes + checksum + filename_len + filename_bytes
        full_payload = header + payload_data
        
        print(f"📦 Total payload: {len(full_payload)} bytes")
        
        # Open input video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"Cannot open video: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"🎬 Video: {width}x{height}, {total_frames} frames, {fps:.1f} FPS")
        
        # Calculate capacity using improved sparse but reliable embedding
        # Use every 4th pixel for better capacity while maintaining compression resistance
        step_size = 4
        pixels_per_frame = (width // step_size) * (height // step_size)
        bytes_per_frame = pixels_per_frame // 8  # 8 bits per byte
        
        print(f"💾 Capacity: {bytes_per_frame} bytes per frame")
        
        if bytes_per_frame == 0:
            raise Exception("Video frame too small for embedding")
        
        frames_needed = (len(full_payload) // bytes_per_frame) + 1
        if frames_needed > total_frames:
            raise Exception(f"Payload too large: need {frames_needed} frames, only have {total_frames}")
        
        print(f"📊 Will use {frames_needed} frames")
        
        # Use Motion JPEG for reasonable compression vs quality balance
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        output_fps = min(fps, 15.0)  # Limit FPS for better quality
        writer = cv2.VideoWriter(output_path, fourcc, output_fps, (width, height))
        
        if not writer.isOpened():
            raise Exception("Cannot create video writer")
        
        # Convert payload to bits
        data_bits = ''.join(format(byte, '08b') for byte in full_payload)
        bit_index = 0
        
        # Process frames
        frame_count = 0
        embedded_frames = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Embed data in first few frames
            if frame_count < frames_needed and bit_index < len(data_bits):
                modified_frame = frame.copy()
                
                # Embed using improved sparse grid with extreme values for compression resistance
                for y in range(0, height, step_size):  # Every 4th pixel
                    for x in range(0, width, step_size):
                        if bit_index >= len(data_bits):
                            break
                        
                        bit = int(data_bits[bit_index])
                        
                        # Use extreme color values for maximum reliability
                        if bit == 1:
                            modified_frame[y, x, :] = [255, 255, 255]  # Pure white
                        else:
                            modified_frame[y, x, :] = [0, 0, 0]        # Pure black
                        
                        bit_index += 1
                
                writer.write(modified_frame)
                embedded_frames += 1
                print(f"📝 Frame {frame_count}: embedded chunk {embedded_frames}")
            else:
                writer.write(frame)
            
            frame_count += 1
        
        cap.release()
        writer.release()
        
        print(f"✅ Successfully embedded {bit_index} bits in {embedded_frames} frames")
        
        return {
            'container_type': 'video',
            'data_size': len(file_data),
            'filename': filename,
            'frames_used': embedded_frames,
            'method': 'Fixed Video Steganography',
            'compression_resistant': True
        }
    
    def extract_file_from_video(self, video_path):
        """Extract a file from video using reliable technique"""
        
        print(f"📤 Fixed Video Steganography - Extracting")
        print(f"📹 Input video: {video_path}")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"Cannot open video: {video_path}")
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"🎬 Video: {width}x{height}, {total_frames} frames")
        
        # Extract bits from frames using same sparse pattern as embedding
        all_bits = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Extract from every 4th pixel (same as embedding)
            frame_bits = []
            step_size = 4  # Must match embedding step size
            for y in range(0, height, step_size):
                for x in range(0, width, step_size):
                    # Read pixel intensity (average of RGB)
                    avg_value = np.mean(frame[y, x, :])
                    
                    # Simple threshold at 127.5
                    if avg_value > 127.5:
                        frame_bits.append(1)
                    else:
                        frame_bits.append(0)
            
            all_bits.extend(frame_bits)
            frame_count += 1
            
            print(f"📤 Frame {frame_count-1}: extracted {len(frame_bits)} bits")
            
            # Check if we have enough for basic header (18 bytes minimum)
            if len(all_bits) >= 144:  # 18 bytes * 8 bits = 144 bits for basic header
                # Try to parse header
                header_bits = all_bits[:144]
                header_bytes = self._bits_to_bytes(header_bits)
                
                if header_bytes[:8] == b'FIXED024':
                    # Found valid header
                    file_size = struct.unpack('<I', header_bytes[8:12])[0]
                    filename_len = struct.unpack('<H', header_bytes[16:18])[0]
                    header_size = 18 + filename_len  # magic + size + checksum + filename_len + filename
                    total_bits_needed = (header_size + file_size) * 8
                    
                    print(f"✅ Found valid header, file size: {file_size} bytes")
                    print(f"📄 Filename length: {filename_len} bytes")
                    print(f"📊 Total needed: {total_bits_needed} bits")
                    
                    # Extract until we have enough
                    while len(all_bits) < total_bits_needed and frame_count < total_frames:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        frame_bits = []
                        for y in range(0, height, step_size):
                            for x in range(0, width, step_size):
                                avg_value = np.mean(frame[y, x, :])
                                frame_bits.append(1 if avg_value > 127.5 else 0)
                        
                        all_bits.extend(frame_bits)
                        frame_count += 1
                        print(f"📤 Frame {frame_count-1}: extracted {len(frame_bits)} bits")
                    
                    break
        
        cap.release()
        
        if len(all_bits) < 144:
            raise Exception("Could not find valid header")
        
        # Parse the complete data
        total_bytes = self._bits_to_bytes(all_bits)
        
        if total_bytes[:8] != b'FIXED024':
            raise Exception("Invalid magic number")
        
        file_size = struct.unpack('<I', total_bytes[8:12])[0]
        stored_checksum = total_bytes[12:16]
        filename_len = struct.unpack('<H', total_bytes[16:18])[0]
        
        header_size = 18 + filename_len
        
        if len(total_bytes) < header_size + file_size:
            raise Exception(f"Insufficient data: need {header_size + file_size}, got {len(total_bytes)}")
        
        filename = total_bytes[18:18 + filename_len].decode('utf-8')
        file_data = total_bytes[header_size:header_size + file_size]
        
        # Note: file_size in header is now the PAYLOAD size (encrypted data if password used, original if not)
        
        # Decrypt if password was used
        if self.password:
            print(f"🔓 Decrypting file data...")
            try:
                # For encrypted data, file_data contains: salt + nonce + ciphertext
                # The encrypted payload is larger than the original file size
                print(f"🔍 Encrypted payload size: {len(file_data)} bytes (original file was {file_size} bytes)")
                
                if len(file_data) < 60:  # 32 (salt) + 12 (nonce) + 16 (min ciphertext)
                    raise Exception(f"Encrypted data too short: {len(file_data)} bytes")
                
                # Extract components - CryptoHandler uses 32-byte salt
                salt = file_data[:32]        # First 32 bytes: salt
                nonce = file_data[32:44]     # Next 12 bytes: nonce  
                ciphertext = file_data[44:]  # Rest: ciphertext
                
                print(f"🔍 Encryption details: salt={len(salt)}, nonce={len(nonce)}, cipher={len(ciphertext)}")
                
                # Create new crypto handler with same password
                crypto = CryptoHandler(self.password)
                # Manually set the extracted salt
                crypto.salt = salt
                
                # Re-derive key and recreate cipher with correct salt
                key = crypto._derive_key()
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                crypto.cipher = AESGCM(key)
                
                # Decrypt
                file_data = crypto.decrypt(ciphertext, nonce)
                print(f"✅ Decryption successful: {len(file_data)} bytes")
                
            except Exception as e:
                raise Exception(f"Decryption failed: {str(e)}")
        
        # Verify checksum
        calculated_checksum = hashlib.md5(file_data).digest()[:4]
        checksum_valid = calculated_checksum == stored_checksum
        
        if not checksum_valid:
            print(f"⚠️  Warning: Checksum mismatch")
        
        print(f"✅ Successfully extracted {len(file_data)} bytes")
        print(f"📄 Original filename: {filename}")
        
        return {
            'data': file_data,
            'filename': filename,
            'size': len(file_data),
            'checksum_valid': checksum_valid
        }
    
    def _bits_to_bytes(self, bits):
        """Convert bits to bytes"""
        # Pad to multiple of 8
        while len(bits) % 8 != 0:
            bits.append(0)
        
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            byte_value = 0
            for j, bit in enumerate(byte_bits):
                if bit:
                    byte_value |= (1 << (7-j))
            result.append(byte_value)
        
        return bytes(result)

def test_fixed_video_steganography():
    """Test the fixed video steganography"""
    
    print("🧪 TESTING FIXED VIDEO STEGANOGRAPHY")
    print("=" * 50)
    
    # Create test file
    test_content = "This is a test file for fixed video steganography. It should work perfectly without data loss!"
    test_file = "test_fixed_video.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    input_video = "debug_test.mp4"
    output_video = "fixed_stego_test.avi"
    extracted_file = "extracted_test_fixed_video.txt"
    
    try:
        # Test without password first
        print("\n=== TEST 1: NO PASSWORD ===")
        stego = FixedVideoSteganography()
        
        # Embed
        print("\n📥 EMBEDDING...")
        metadata = stego.embed_file_in_video(input_video, test_file, output_video)
        print(f"📊 Metadata: {metadata}")
        
        # Extract
        print("\n📤 EXTRACTING...")
        result = stego.extract_file_from_video(output_video)
        
        # Write extracted file
        with open(extracted_file, 'wb') as f:
            f.write(result['data'])
        
        # Compare
        print("\n🔍 COMPARISON:")
        with open(extracted_file, 'r') as f:
            extracted_content = f.read()
        
        print(f"Original:  '{test_content}'")
        print(f"Extracted: '{extracted_content}'")
        print(f"Filename: '{result['filename']}'")
        print(f"Checksum valid: {result['checksum_valid']}")
        
        if test_content == extracted_content:
            print("✅ TEST 1 PASSED: PERFECT MATCH!")
        else:
            print("❌ TEST 1 FAILED: MISMATCH!")
        
        # Clean up
        os.remove(output_video)
        os.remove(extracted_file)
        
        # Test with password
        print("\n=== TEST 2: WITH PASSWORD ===")
        stego_pwd = FixedVideoSteganography(password="test123")
        
        # Embed
        print("\n📥 EMBEDDING WITH PASSWORD...")
        metadata = stego_pwd.embed_file_in_video(input_video, test_file, output_video)
        print(f"📊 Metadata: {metadata}")
        
        # Extract
        print("\n📤 EXTRACTING WITH PASSWORD...")
        result = stego_pwd.extract_file_from_video(output_video)
        
        # Write extracted file
        with open(extracted_file, 'wb') as f:
            f.write(result['data'])
        
        # Compare
        print("\n🔍 COMPARISON:")
        with open(extracted_file, 'r') as f:
            extracted_content = f.read()
        
        print(f"Original:  '{test_content}'")
        print(f"Extracted: '{extracted_content}'")
        print(f"Filename: '{result['filename']}'")
        print(f"Checksum valid: {result['checksum_valid']}")
        
        if test_content == extracted_content:
            print("✅ TEST 2 PASSED: PERFECT MATCH WITH ENCRYPTION!")
        else:
            print("❌ TEST 2 FAILED: MISMATCH!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        for f in [test_file, output_video, extracted_file]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

if __name__ == "__main__":
    test_fixed_video_steganography()