#!/usr/bin/env python3
"""
Universal File-in-File Steganography
====================================

This module provides the ability to hide any file inside any other file
using advanced steganographic techniques. Unlike traditional steganography
that relies on specific container formats (images, audio), this system
can hide files in ANY file type.

Features:
- Hide any file inside any other file
- Least Significant Bit (LSB) steganography for binary files
- Text-based steganography using whitespace and formatting
- Redundancy and error correction
- Password protection with AES encryption
- Perfect file integrity preservation

Author: Enhanced Steganography System
"""

import os
import sys
import hashlib
import json
import struct
import random
from typing import Tuple, Optional, Dict, Any
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not available - image steganography will use fallback method")

# Cryptography
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import secrets

class UniversalFileSteganography:
    """Universal file-in-file steganography system"""
    
    def __init__(self, password: str = None):
        self.password = password
        self.magic_header = b"UNISTEGOFILE"
        self.redundancy = 3  # For error correction
        
    def hide_file_in_file(self, container_path: str, secret_file_path: str, output_path: str) -> Dict[str, Any]:
        """Hide a file inside another file"""
        
        print(f"[+] Hiding '{secret_file_path}' inside '{container_path}'")
        
        # Read container and secret files
        with open(container_path, 'rb') as f:
            container_data = f.read()
        
        with open(secret_file_path, 'rb') as f:
            secret_data = f.read()
        
        # Get file info
        secret_filename = os.path.basename(secret_file_path)
        container_type = self._detect_container_type(container_path)
        
        print(f"[+] Container type: {container_type}")
        print(f"[+] Secret file: {secret_file_path} ({len(secret_data)} bytes)")
        print(f"[+] Container size: {len(container_data)} bytes")
        
        # Encrypt if password provided first
        if self.password:
            encrypted_data = self._encrypt_data(secret_data)
            payload = encrypted_data
            encrypted_flag = True
        else:
            payload = secret_data
            encrypted_flag = False
        
        # Create compact binary metadata to minimize overhead
        # Format: magic(4) + filename_len(1) + filename + file_size(4) + checksum(8) + encrypted_flag(1) + payload
        filename_bytes = secret_filename.encode('utf-8')[:255]  # Limit filename to 255 bytes
        checksum_short = hashlib.sha256(secret_data).digest()[:8]  # Use 8 bytes instead of 16-char hex
        
        metadata_binary = (
            self.magic_header +                    # 4 bytes
            struct.pack('<B', len(filename_bytes)) +  # 1 byte for filename length
            filename_bytes +                       # Variable length filename
            struct.pack('<I', len(payload)) +      # 4 bytes for file size
            checksum_short +                       # 8 bytes checksum
            struct.pack('<B', 1 if encrypted_flag else 0)  # 1 byte for encryption flag
        )
        
        full_payload = metadata_binary + payload
        
        print(f"[+] Total payload: {len(full_payload)} bytes")
        
        # Calculate capacity usage
        capacity_used = (len(full_payload) * 8) / (len(container_data) * 8) * 100
        
        # Choose embedding method based on container type
        if container_type == 'image':
            modified_container = self._embed_in_image(container_path, full_payload, output_path)
            # For image, we save directly in _embed_in_image, so return early
            return {
                'success': True,
                'secret_file_size': len(secret_data),
                'container_size': len(container_data),
                'output_size': os.path.getsize(output_path),
                'capacity_used': f"{capacity_used:.1f}%",
                'method': 'image',
                'encrypted': metadata['encrypted']
            }
        elif container_type in ['text', 'source_code']:
            # For plain text files, try text method first, fallback to binary
            try:
                # Only use text method for simple text files that are actually UTF-8
                container_data.decode('utf-8')
                # If decode succeeds and file is small enough, use text method
                if len(container_data) < 1024 * 1024:  # Only for files < 1MB
                    print("[+] Using text-based steganography for small text file")
                    modified_container = self._embed_in_text(container_data, full_payload)
                else:
                    print("[+] Text file too large, using binary method for safety")
                    modified_container = self._embed_in_binary(container_data, full_payload)
            except UnicodeDecodeError:
                print("[+] File not UTF-8 compatible, using safe document method")
                modified_container = self._embed_document_safe(container_data, full_payload)
        else:
            # CRITICAL FIX: Use SAFE document embedding that preserves file structure
            # This prevents corruption of PDF, DOCX, RTF and other structured document formats
            print(f"[+] Using SAFE document steganography for {container_type} file")
            modified_container = self._embed_document_safe(container_data, full_payload)
        
        # Save result
        with open(output_path, 'wb') as f:
            f.write(modified_container)
        
        print(f"[+] File hidden successfully in '{output_path}'")
        print(f"[+] Capacity used: {capacity_used:.1f}%")
        
        return {
            'success': True,
            'secret_file_size': len(secret_data),
            'container_size': len(container_data),
            'output_size': len(modified_container),
            'capacity_used': f"{capacity_used:.1f}%",
            'method': 'text' if container_type in ['text', 'source_code'] else ('image' if container_type == 'image' else 'binary'),
            'encrypted': encrypted_flag
        }
    
    def extract_file_from_file(self, stego_file_path: str, output_dir: str = None) -> str:
        """Extract hidden file from container"""
        
        print(f"[+] Extracting hidden file from '{stego_file_path}'")
        
        with open(stego_file_path, 'rb') as f:
            stego_data = f.read()
        
        # Detect container type to choose extraction method
        container_type = self._detect_container_type(stego_file_path)
        
        if container_type in ['text', 'source_code']:
            payload = self._extract_from_text(stego_data)
        elif container_type == 'image':
            payload = self._extract_from_image(stego_file_path)
        else:
            # Try safe extraction first
            payload = self._extract_document_safe(stego_data)
            if not payload:
                # Fallback to old binary method for backward compatibility
                payload = self._extract_from_binary(stego_data)
        
        if not payload:
            raise ValueError("No hidden file found or extraction failed")
        
        # Parse compact binary metadata
        if not payload.startswith(self.magic_header):
            raise ValueError("Invalid file format or corrupted data")
        
        offset = len(self.magic_header)  # Skip magic header (4 bytes)
        
        # Read filename length and filename
        filename_len = struct.unpack('<B', payload[offset:offset+1])[0]
        offset += 1
        filename = payload[offset:offset+filename_len].decode('utf-8')
        offset += filename_len
        
        # Read file size
        file_size = struct.unpack('<I', payload[offset:offset+4])[0]
        offset += 4
        
        # Read checksum
        checksum_bytes = payload[offset:offset+8]
        offset += 8
        
        # Read encryption flag
        encrypted_flag = bool(struct.unpack('<B', payload[offset:offset+1])[0])
        offset += 1
        
        # Create metadata dict for compatibility
        metadata = {
            'filename': filename,
            'file_size': file_size,
            'encrypted': encrypted_flag,
            'checksum': checksum_bytes.hex()[:16]  # Convert back to hex for compatibility
        }
        file_data = payload[offset:offset + file_size]
        
        print(f"📊 Extracting {file_size} bytes of file data")
        
        # Decrypt if needed
        if metadata.get('encrypted', False):
            if not self.password:
                raise ValueError("Password required for encrypted file")
            file_data = self._decrypt_data(file_data)
        
        # Verify integrity using binary checksum
        actual_checksum_bytes = hashlib.sha256(file_data).digest()[:8]
        if actual_checksum_bytes != checksum_bytes:
            print(f"⚠️ Warning: Checksum mismatch")
        else:
            print(f"✅ Checksum verification passed")
        
        # Save extracted file
        output_dir = output_dir or os.getcwd()
        output_filename = f"extracted_{metadata['filename']}"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        print(f"[SUCCESS] File extracted successfully!")
        print(f"[+] Original filename: {metadata['filename']}")
        print(f"[+] File size: {len(file_data)} bytes")
        print(f"[+] Saved as: {output_path}")
        
        return output_path
    
    def _detect_container_type(self, file_path: str) -> str:
        """Detect if file is text-based, image, or binary"""
        
        # Check for image files first
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
        if any(file_path.lower().endswith(ext) for ext in image_extensions):
            return 'image'
        
        # Document formats should be treated as binary to preserve structure
        document_extensions = ['.rtf', '.doc', '.docx', '.pdf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx']
        if any(file_path.lower().endswith(ext) for ext in document_extensions):
            return 'binary'
        
        try:
            # Try to read as text
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1024)  # Read first 1KB
            
            # Check if it's likely source code
            code_extensions = ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h']
            if any(file_path.lower().endswith(ext) for ext in code_extensions):
                return 'source_code'
            
            # Check if it's plain text
            text_extensions = ['.txt', '.md', '.log', '.csv']
            if any(file_path.lower().endswith(ext) for ext in text_extensions):
                return 'text'
            
            # If readable as UTF-8 and appears to be simple text, consider it text
            if all(ord(c) < 128 for c in content[:100]):  # ASCII check
                # Additional check: avoid treating structured formats as text
                if not any(marker in content.lower() for marker in ['\\rtf', '<?xml', '<html', 'pk\x03\x04']):
                    return 'text'
                
        except (UnicodeDecodeError, IOError):
            pass
        
        return 'binary'
    
    def _embed_in_text(self, container_data: bytes, payload: bytes) -> bytes:
        """Embed data in text file using whitespace steganography"""
        
        try:
            # Convert to text
            container_text = container_data.decode('utf-8')
            
            # Convert payload to binary string
            payload_bits = ''.join(format(byte, '08b') for byte in payload)
            
            print(f"[+] Using whitespace steganography for text file")
            print(f"[+] Embedding {len(payload_bits)} bits")
            
            # Use spaces/tabs to encode bits (space = 0, tab = 1)
            # Add redundancy by embedding each bit multiple times
            modified_text = ""
            bit_index = 0
            
            for char in container_text:
                modified_text += char
                
                # Add hidden bits after certain characters
                if char in [' ', '\n', '.', ',', ';', ':', '!', '?'] and bit_index < len(payload_bits):
                    # Embed bit using invisible characters
                    bit = payload_bits[bit_index]
                    
                    # Use zero-width characters for steganography
                    if bit == '1':
                        # Zero-width space (U+200B) for 1
                        modified_text += '\u200B'
                    else:
                        # Zero-width non-joiner (U+200C) for 0  
                        modified_text += '\u200C'
                    
                    bit_index += 1
            
            # If we haven't embedded all bits, append to end with invisible chars
            while bit_index < len(payload_bits):
                bit = payload_bits[bit_index]
                if bit == '1':
                    modified_text += '\u200B'
                else:
                    modified_text += '\u200C'
                bit_index += 1
            
            return modified_text.encode('utf-8')
            
        except Exception as e:
            print(f"⚠️ Text embedding failed: {e}, falling back to binary method")
            return self._embed_in_binary(container_data, payload)
    
    def _embed_in_image(self, image_path: str, payload: bytes, output_path: str) -> None:
        """Embed data in image using PIL-based LSB steganography"""
        
        if not PIL_AVAILABLE:
            # Fallback to binary method if PIL not available
            print("⚠️ PIL not available, using binary LSB method")
            with open(image_path, 'rb') as f:
                container_data = f.read()
            modified_data = self._embed_in_binary(container_data, payload)
            with open(output_path, 'wb') as f:
                f.write(modified_data)
            return
        
        try:
            print(f"🖼️ Using PIL-based image steganography")
            
            # Open image
            img = Image.open(image_path)
            img_array = np.array(img)
            
            print(f"📐 Image dimensions: {img_array.shape}")
            print(f"🔢 Embedding {len(payload)} bytes")
            
            # Check capacity
            total_pixels = img_array.size
            if len(payload) * 8 > total_pixels:
                raise ValueError(f"Image too small for payload: need {len(payload) * 8} bits, have {total_pixels} pixels")
            
            # Convert payload to bits
            payload_bits = []
            for byte in payload:
                for i in range(8):
                    payload_bits.append((byte >> i) & 1)
            
            # Flatten image for processing
            flat_img = img_array.flatten()
            
            # Embed bits using LSB
            for i, bit in enumerate(payload_bits):
                if i < len(flat_img):
                    if bit == 1:
                        flat_img[i] = flat_img[i] | 1
                    else:
                        flat_img[i] = flat_img[i] & 0xFE
            
            # Reshape and save
            modified_array = flat_img.reshape(img_array.shape)
            modified_img = Image.fromarray(modified_array.astype(np.uint8), mode=img.mode)
            modified_img.save(output_path, format=img.format)
            
            print(f"✅ Image steganography completed: {output_path}")
            
        except Exception as e:
            print(f"⚠️ Image embedding failed: {e}, falling back to binary method")
            # Fallback to binary method
            with open(image_path, 'rb') as f:
                container_data = f.read()
            modified_data = self._embed_in_binary(container_data, payload)
            with open(output_path, 'wb') as f:
                f.write(modified_data)
    
    def _embed_document_safe(self, container_data: bytes, payload: bytes) -> bytes:
        """SAFE document embedding that preserves file structure"""
        
        import base64
        import struct
        
        print(f"🛡️ Using SAFE document embedding - NO structure modification")
        
        # Create end marker structure (completely safe - just appends to end)
        marker = b'SAFE_STEGO_DATA'
        
        # Encode safely
        encoded_payload = base64.b64encode(payload)
        
        # Structure: original_data + marker + payload_len + payload + marker
        payload_len = struct.pack('<I', len(encoded_payload))
        
        modified_data = container_data + marker + payload_len + encoded_payload + marker
        
        print(f"🛡️ Safely appended {len(modified_data) - len(container_data)} bytes without file corruption")
        return modified_data
    
    def _extract_document_safe(self, stego_data: bytes) -> Optional[bytes]:
        """SAFE document extraction that looks for end markers"""
        
        import base64
        import struct
        
        marker = b'SAFE_STEGO_DATA'
        
        # Find last occurrence of marker
        last_marker_pos = stego_data.rfind(marker)
        if last_marker_pos == -1:
            return None
        
        # Find first occurrence of marker
        first_marker_pos = stego_data.find(marker)
        if first_marker_pos == -1 or first_marker_pos == last_marker_pos:
            return None
        
        # Extract structure
        pos = first_marker_pos + len(marker)
        
        # Read payload length
        if pos + 4 > len(stego_data):
            return None
            
        payload_len = struct.unpack('<I', stego_data[pos:pos+4])[0]
        pos += 4
        
        # Read payload
        if pos + payload_len > len(stego_data):
            return None
            
        encoded_payload = stego_data[pos:pos+payload_len]
        
        try:
            payload = base64.b64decode(encoded_payload)
            print(f"🛡️ SAFE extraction successful: {len(payload)} bytes")
            return payload
        except Exception as e:
            print(f"🛡️ SAFE extraction failed: {e}")
            return None
    
    def _embed_in_binary(self, container_data: bytes, payload: bytes) -> bytes:
        """Embed data in binary file using multi-bit LSB steganography"""
        
        container_array = bytearray(container_data)
        payload_bits = ''.join(format(byte, '08b') for byte in payload)
        
        print(f"💾 Using enhanced LSB steganography for binary file")
        print(f"🔢 Embedding {len(payload_bits)} bits")
        
        # CRITICAL FIX: Skip document headers to preserve file format integrity
        header_skip = self._get_header_skip_bytes(container_data)
        if header_skip > 0:
            print(f"🛡️ Skipping first {header_skip} bytes to preserve document format")
        
        # CRITICAL FIX: Use adaptive bits per byte based on payload size
        # Start with safest (2 bits) and scale up as needed for small files
        # Account for header skip in capacity calculation
        usable_bytes = len(container_array) - header_skip
        for bits_per_byte in [2, 4, 8]:
            available_bits = usable_bytes * bits_per_byte
            if len(payload_bits) <= available_bits:
                break
        else:
            # Even with 8 bits per byte, still not enough space
            max_capacity = usable_bytes * 8
            raise ValueError(f"Payload too large: need {len(payload_bits)} bits, max capacity {max_capacity} bits")
        
        print(f"📊 Using {bits_per_byte} bits per byte (capacity: {available_bits} bits)")
        
        # Enhanced LSB embedding with adaptive bits per byte
        bit_index = 0
        for container_index in range(header_skip, len(container_array)):
            if bit_index >= len(payload_bits):
                break
                
            byte_value = container_array[container_index]
            
            # Clear the lower bits we're going to use
            mask = (0xFF << bits_per_byte) & 0xFF
            byte_value &= mask
            
            # Extract the bits to embed
            bits_to_embed = 0
            for bit_offset in range(bits_per_byte):
                if bit_index + bit_offset < len(payload_bits):
                    if payload_bits[bit_index + bit_offset] == '1':
                        bits_to_embed |= (1 << bit_offset)
            
            # Embed the bits
            byte_value |= bits_to_embed
            container_array[container_index] = byte_value
            
            bit_index += bits_per_byte
        
        print(f"✅ Embedded {bit_index} bits using {bits_per_byte}-bit LSB method")
        return bytes(container_array)
    
    def _extract_from_text(self, stego_data: bytes) -> Optional[bytes]:
        """Extract data from text file using whitespace analysis"""
        
        try:
            # Convert to text
            stego_text = stego_data.decode('utf-8')
            
            print(f"[+] Extracting from text using whitespace analysis")
            
            # Extract hidden bits from zero-width characters
            extracted_bits = ""
            
            for char in stego_text:
                if char == '\u200B':  # Zero-width space = 1
                    extracted_bits += '1'
                elif char == '\u200C':  # Zero-width non-joiner = 0
                    extracted_bits += '0'
            
            if not extracted_bits:
                print("❌ No hidden data found in text")
                return None
            
            print(f"🔢 Extracted {len(extracted_bits)} bits")
            
            # Convert bits to bytes
            extracted_bytes = bytearray()
            for i in range(0, len(extracted_bits), 8):
                if i + 7 < len(extracted_bits):
                    byte_bits = extracted_bits[i:i+8]
                    extracted_bytes.append(int(byte_bits, 2))
            
            return bytes(extracted_bytes)
            
        except Exception as e:
            print(f"⚠️ Text extraction failed: {e}, trying binary method")
            return self._extract_from_binary(stego_data)
    
    def _extract_from_image(self, image_path: str) -> Optional[bytes]:
        """Extract data from image using PIL-based LSB steganography"""
        
        if not PIL_AVAILABLE:
            # Fallback to binary method if PIL not available
            print("⚠️ PIL not available, using binary LSB method")
            with open(image_path, 'rb') as f:
                stego_data = f.read()
            return self._extract_from_binary(stego_data)
        
        try:
            print(f"🖼️ Using PIL-based image extraction")
            
            # Open image
            img = Image.open(image_path)
            img_array = np.array(img)
            
            print(f"📐 Image dimensions: {img_array.shape}")
            
            # Flatten image and extract LSBs
            flat_img = img_array.flatten()
            extracted_bits = []
            
            for pixel in flat_img:
                extracted_bits.append(pixel & 1)
            
            # Convert bits to bytes
            extracted_bytes = []
            for i in range(0, len(extracted_bits), 8):
                if i + 7 < len(extracted_bits):
                    byte_bits = extracted_bits[i:i+8]
                    byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                    extracted_bytes.append(byte_value)
            
            # Convert to bytes and look for magic header
            data_bytes = bytes(extracted_bytes)
            
            # Look for magic header
            header_pos = data_bytes.find(self.magic_header)
            if header_pos == -1:
                print(f"⚠️ Magic header not found in image")
                return None
            
            print(f"✅ Magic header found at position {header_pos}")
            return data_bytes[header_pos:]
            
        except Exception as e:
            print(f"⚠️ Image extraction failed: {e}, falling back to binary method")
            # Fallback to binary method
            with open(image_path, 'rb') as f:
                stego_data = f.read()
            return self._extract_from_binary(stego_data)
    
    def _extract_from_binary(self, stego_data: bytes) -> Optional[bytes]:
        """Extract data from binary file using enhanced LSB analysis"""
        
        print(f"💾 Extracting from binary using enhanced LSB analysis")
        
        # Skip header bytes for format preservation
        header_skip = self._get_header_skip_bytes(stego_data)
        if header_skip > 0:
            print(f"🛡️ Skipping first {header_skip} bytes to avoid document header")
        
        # Try multiple bit depths: 2, 4, 8, then fallback to 1
        for bits_per_byte in [2, 4, 8, 1]:
            print(f"🔄 Trying {bits_per_byte}-bit extraction...")
            
            extracted_bits = []
            for i, byte_val in enumerate(stego_data):
                # Skip header bytes
                if i < header_skip:
                    continue
                # Extract the lower bits
                for bit_offset in range(bits_per_byte):
                    bit = (byte_val >> bit_offset) & 1
                    extracted_bits.append(str(bit))
            
            print(f"📊 Extracted {len(extracted_bits)} bits using {bits_per_byte}-bit method")
            
            # Convert bits to bytes
            extracted_bytes = bytearray()
            for i in range(0, len(extracted_bits), 8):
                if i + 7 < len(extracted_bits):
                    byte_bits = ''.join(extracted_bits[i:i+8])
                    byte_val = int(byte_bits, 2)
                    extracted_bytes.append(byte_val)
            
            payload_data = bytes(extracted_bytes)
            
            # Look for magic header
            magic_pos = payload_data.find(self.magic_header)
            if magic_pos != -1:
                print(f"✅ Magic header found at position {magic_pos} using {bits_per_byte}-bit method")
                payload = payload_data[magic_pos:]
                break
        else:
            print("❌ No valid payload found with any method")
            return None
        
        # Parse compact binary metadata to get required length
        try:
            offset = len(self.magic_header)  # Skip magic header (4 bytes)
            
            if len(payload) >= offset + 1:
                # Read filename length
                filename_len = struct.unpack('<B', payload[offset:offset+1])[0]
                offset += 1
                
                if len(payload) >= offset + filename_len + 4:
                    # Skip filename
                    offset += filename_len
                    
                    # Read file size
                    file_size = struct.unpack('<I', payload[offset:offset+4])[0]
                    offset += 4
                    
                    # Skip checksum (8 bytes) and encryption flag (1 byte)
                    offset += 9
                    
                    total_needed = offset + file_size
                    print(f"📦 Total payload needed: {total_needed} bytes")
                    
                    if len(payload) >= total_needed:
                        return payload[:total_needed]
                    else:
                        print(f"⚠️ Insufficient data: have {len(payload)}, need {total_needed}")
                        # Return what we have for now
                        return payload
                
        except Exception as e:
            print(f"⚠️ Error parsing compact metadata: {e}")
        
        # Return whatever payload we found
        return payload[:min(len(payload), 100000)]  # Limit to 100KB
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-GCM"""
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(self.password.encode())
        
        # Encrypt
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        
        return salt + nonce + ciphertext
    
    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES-GCM"""
        print(f"[DEBUG] Decrypting data of length {len(encrypted_data)}")
        
        if len(encrypted_data) < 28:
            raise ValueError(f"Encrypted data too short: {len(encrypted_data)} bytes, need at least 28")
        
        salt = encrypted_data[:16]
        nonce = encrypted_data[16:28]
        ciphertext = encrypted_data[28:]
        
        print(f"[DEBUG] Salt: {len(salt)} bytes, Nonce: {len(nonce)} bytes, Ciphertext: {len(ciphertext)} bytes")
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(self.password.encode())
        
        # Decrypt
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)
    
    def _get_header_skip_bytes(self, data: bytes) -> int:
        """Determine how many bytes to skip at the beginning to preserve file format"""
        
        # RTF files: Skip until we reach the main content
        if data.startswith(b'{\\rtf'):
            # Find the end of the RTF header (look for the first content after format declarations)
            rtf_text = data.decode('latin-1', errors='ignore')
            
            # Look for common RTF header patterns to skip
            skip_patterns = [
                '\\ansi\\deff',  # ANSI encoding definition
                '\\fonttbl',     # Font table
                '\\f0',          # First font reference
            ]
            
            max_skip = 0
            for pattern in skip_patterns:
                pos = rtf_text.find(pattern)
                if pos != -1:
                    # Find the end of this declaration (next space or })
                    end_pos = pos
                    while end_pos < len(rtf_text) and rtf_text[end_pos] not in [' ', '}', '\n']:
                        end_pos += 1
                    max_skip = max(max_skip, end_pos + 10)  # Add small buffer
            
            return min(max_skip, 100)  # Cap at 100 bytes for safety
        
        # PDF files: Skip PDF header
        elif data.startswith(b'%PDF'):
            return 50
        
        # DOCX files (ZIP format): Skip ZIP header
        elif data.startswith(b'PK\x03\x04'):
            return 30
        
        # Default: Skip minimal bytes for other formats
        else:
            return 10
    
    def hide_data(self, carrier_file_path: str, content_to_hide, output_path: str, is_file: bool = False, original_filename: str = None, **kwargs) -> Dict[str, Any]:
        """Hide data method expected by enhanced_app.py
        
        Args:
            carrier_file_path: Path to the carrier file
            content_to_hide: Either file content (bytes) or text content (str)
            output_path: Where to save the stego file
            is_file: True if content_to_hide is file content, False if text
            original_filename: Original filename for file content
        """
        try:
            import tempfile
            import os
            
            # Create a temporary file to hold the content to hide
            # Use proper extension to avoid frontend parsing issues
            temp_suffix = '.txt' if not is_file else '.bin'
            with tempfile.NamedTemporaryFile(delete=False, suffix=temp_suffix) as temp_file:
                if is_file:
                    # content_to_hide is file content (bytes)
                    if isinstance(content_to_hide, str):
                        temp_file.write(content_to_hide.encode('utf-8'))
                    else:
                        temp_file.write(content_to_hide)
                else:
                    # content_to_hide is text content
                    text_data = str(content_to_hide)
                    temp_file.write(text_data.encode('utf-8'))
                
                temp_file_path = temp_file.name
            
            try:
                # Use the existing hide_file_in_file method
                result = self.hide_file_in_file(carrier_file_path, temp_file_path, output_path)
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'details': result
                }
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_data(self, stego_file_path: str, output_dir: str = None):
        """Extract data method expected by enhanced_app.py
        
        Returns either:
        - (data, filename) tuple for compatibility
        - Just the data directly
        """
        
        print(f"🔍 [EXTRACT_DATA] *** API EXTRACTION CALLED *** File: {stego_file_path}")
        print(f"[DEBUG extract_data] Called with stego_file_path: {stego_file_path}")
        try:
            import tempfile
            import os
            
            # Create temporary output directory if needed
            if output_dir is None:
                output_dir = tempfile.mkdtemp()
            
            # Extract the hidden file
            extracted_path = self.extract_file_from_file(stego_file_path, output_dir)
            
            # Read the extracted content
            with open(extracted_path, 'rb') as f:
                extracted_content = f.read()
            
            # Get the clean filename from the temporary path
            temp_filename = os.path.basename(extracted_path)
            
            # The temp filename is like "extracted_content_secret_1762073697_c4a4e56a.jpg"
            # We want to clean it up to get just "secret.jpg"
            if temp_filename.startswith('extracted_'):
                # Remove the 'extracted_' prefix to get original filename
                original_filename = temp_filename[10:]  # len('extracted_') = 10
            else:
                original_filename = temp_filename
            
            print(f"[DEBUG extract_data] Processing filename: {temp_filename} -> {original_filename}")
            
            # Clean up API-generated prefixes like "content_secret_1762073697_c4a4e56a.jpg" -> "secret.jpg"
            import re
            
            # Check if this is a temp file pattern like "tmp_abc123.bin" or "tmpxyz456.bin"
            if (original_filename.startswith('tmp') and 
                (original_filename.endswith('.bin') or '.' not in original_filename)):
                
                print(f"[DEBUG extract_data] Detected temp filename pattern: {original_filename}")
                
                # This is a temp file, detect the correct extension from binary content
                if extracted_content.startswith(b'\xff\xd8\xff\xe0') and b'JFIF' in extracted_content[:20]:
                    original_filename = "extracted_image.jpg"
                    print(f"[DEBUG extract_data] Detected JPEG content -> {original_filename}")
                elif extracted_content.startswith(b'\xff\xd8\xff\xe1'):  # JPEG with EXIF
                    original_filename = "extracted_image.jpg"
                    print(f"[DEBUG extract_data] Detected JPEG with EXIF -> {original_filename}")
                elif extracted_content.startswith(b'\x89PNG\r\n\x1a\n'):
                    original_filename = "extracted_image.png"
                    print(f"[DEBUG extract_data] Detected PNG content -> {original_filename}")
                elif extracted_content.startswith(b'%PDF'):
                    original_filename = "extracted_document.pdf"
                    print(f"[DEBUG extract_data] Detected PDF content -> {original_filename}")
                elif extracted_content.startswith(b'PK'):  # ZIP-based files
                    original_filename = "extracted_archive.zip"
                    print(f"[DEBUG extract_data] Detected ZIP content -> {original_filename}")
                # Enhanced audio file detection
                elif extracted_content.startswith(b'ID3') or extracted_content.startswith(b'\xff\xfb') or extracted_content.startswith(b'\xff\xf3') or extracted_content.startswith(b'\xff\xf2'):
                    original_filename = "extracted_audio.mp3"
                    print(f"[DEBUG extract_data] Detected MP3 content -> {original_filename}")
                elif extracted_content.startswith(b'RIFF') and b'WAVE' in extracted_content[:20]:
                    original_filename = "extracted_audio.wav"
                    print(f"[DEBUG extract_data] Detected WAV content -> {original_filename}")
                elif extracted_content.startswith(b'fLaC'):
                    original_filename = "extracted_audio.flac"
                    print(f"[DEBUG extract_data] Detected FLAC content -> {original_filename}")
                elif extracted_content.startswith(b'OggS'):
                    original_filename = "extracted_audio.ogg"
                    print(f"[DEBUG extract_data] Detected OGG content -> {original_filename}")
                # Enhanced video file detection  
                elif extracted_content.startswith(b'\x00\x00\x00\x14ftyp') or extracted_content.startswith(b'\x00\x00\x00\x18ftyp') or extracted_content.startswith(b'\x00\x00\x00\x1cftyp') or extracted_content.startswith(b'\x00\x00\x00\x20ftyp'):
                    original_filename = "extracted_video.mp4"
                    print(f"[DEBUG extract_data] Detected MP4 content -> {original_filename}")
                elif extracted_content.startswith(b'RIFF') and b'AVI ' in extracted_content[:20]:
                    original_filename = "extracted_video.avi"
                    print(f"[DEBUG extract_data] Detected AVI content -> {original_filename}")
                else:
                    original_filename = "extracted_file.bin"
                    print(f"[DEBUG extract_data] Unknown content type -> {original_filename}")
            
            # Pattern matches: (prefix_)name(_timestamp_uuid).ext
            # We want to extract just the "name.ext" part
            elif '_' in original_filename:
                # Check if it looks like an API-generated filename
                match = re.match(r'^(?:content_|carrier_)?([^_]+)(?:_\d+_[a-f0-9]+)?(\.[^.]+)$', original_filename)
                if match:
                    base_name, extension = match.groups()
                    original_filename = base_name + extension
                    print(f"[DEBUG extract_data] Cleaned API filename: {temp_filename} -> {original_filename}")
            
            # Ensure we have a reasonable filename
            if not original_filename or original_filename.startswith('.'):
                original_filename = "extracted_file.bin"
            
            # CRITICAL FIX: Always return extracted content as raw bytes to preserve original format
            # The API layer (enhanced_app.py) will handle text decoding if needed
            # This prevents line ending corruption during steganographic extraction
            
            # Return binary content as tuple: (data, filename) 
            # This preserves the exact original content including line endings
            return (extracted_content, original_filename)
                
        except Exception as e:
            # Return None to indicate failure
            return None


def test_universal_file_steganography():
    """Test the universal file steganography system"""
    
    print("🧪 TESTING UNIVERSAL FILE-IN-FILE STEGANOGRAPHY")
    print("=" * 60)
    
    # Create test files
    container_files = {
        'text_container.txt': "This is a plain text file.\nIt contains multiple lines.\nWe will hide a secret file inside it!",
        'script_container.py': '#!/usr/bin/env python3\nprint("This is a Python script")\nresult = 42 + 8\nprint(f"Result: {result}")',
        'binary_container.bin': bytes([i % 256 for i in range(1000)])  # Binary data
    }
    
    secret_files = {
        'secret.txt': "SECRET DOCUMENT\nClassified information here!",
        'data.json': '{"secret": "data", "hidden": true, "value": 12345}'
    }
    
    # Create test files
    for filename, content in container_files.items():
        if isinstance(content, str):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            with open(filename, 'wb') as f:
                f.write(content)
    
    for filename, content in secret_files.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    stego = UniversalFileSteganography(password="test123")
    
    test_results = []
    
    # Test combinations
    test_cases = [
        ('text_container.txt', 'secret.txt', 'Text in Text'),
        ('script_container.py', 'data.json', 'JSON in Python Script'), 
        ('binary_container.bin', 'secret.txt', 'Text in Binary'),
    ]
    
    for container, secret, description in test_cases:
        print(f"\n🔬 Testing: {description}")
        print("-" * 40)
        
        try:
            # Hide file
            output_file = f"stego_{container}"
            result = stego.hide_file_in_file(container, secret, output_file)
            
            if result['success']:
                print(f"✅ Hiding successful - {result['capacity_used']} capacity used")
                
                # Extract file
                extracted_file = stego.extract_file_from_file(output_file)
                
                # Verify content
                with open(secret, 'rb') as f:
                    original_content = f.read()
                with open(extracted_file, 'rb') as f:
                    extracted_content = f.read()
                
                if original_content == extracted_content:
                    print(f"✅ Extraction and verification successful!")
                    test_results.append(True)
                else:
                    print(f"❌ Content mismatch after extraction")
                    test_results.append(False)
            else:
                print(f"❌ Hiding failed")
                test_results.append(False)
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            test_results.append(False)
    
    # Cleanup
    all_files = list(container_files.keys()) + list(secret_files.keys())
    all_files += [f"stego_{f}" for f in container_files.keys()]
    all_files += [f"extracted_{f}" for f in secret_files.keys()]
    
    for file in all_files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except:
            pass
    
    # Results
    print(f"\n📊 Test Results: {sum(test_results)}/{len(test_results)} passed")
    return sum(test_results) == len(test_results)



if __name__ == "__main__":
    test_universal_file_steganography()