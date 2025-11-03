"""
Debug the actual embedded file to see if it contains the expected magic header
"""

def check_embedded_file():
    """Check if the embedded file actually contains hidden data"""
    
    embedded_file = r"outputs\stego_carrier_copyright_demo_file_1762182815_938567e8_1762182815_cc2e85b4.png"
    magic_header = b"VEILFORGE_UNIVERSAL_SAFE_V2"
    
    print("🔍 CHECKING EMBEDDED FILE STRUCTURE")
    print("=" * 50)
    print(f"File: {embedded_file}")
    
    try:
        with open(embedded_file, 'rb') as f:
            file_data = f.read()
        
        print(f"File size: {len(file_data)} bytes")
        
        # Look for magic header
        magic_pos = file_data.find(magic_header)
        
        if magic_pos == -1:
            print("❌ NO MAGIC HEADER FOUND!")
            print("This means no data was actually embedded in the file")
            
            # Check if it's just an image file
            if file_data.startswith(b'\x89PNG'):
                print("📸 File appears to be a regular PNG image")
            elif file_data.startswith(b'\xff\xd8'):
                print("📸 File appears to be a regular JPEG image")
            else:
                print("❓ Unknown file format")
            
            return False
        else:
            print(f"✅ Magic header found at position: {magic_pos}")
            
            # Try to parse the metadata
            try:
                metadata_size_pos = magic_pos + len(magic_header)
                metadata_size = int.from_bytes(file_data[metadata_size_pos:metadata_size_pos+4], 'little')
                print(f"📊 Metadata size: {metadata_size} bytes")
                
                metadata_pos = metadata_size_pos + 4
                metadata_json = file_data[metadata_pos:metadata_pos+metadata_size]
                
                import json
                metadata = json.loads(metadata_json.decode('utf-8'))
                print(f"📋 Metadata: {metadata}")
                
                # Check if encrypted
                if metadata.get('encrypted'):
                    print("🔒 Data is encrypted (requires password)")
                else:
                    print("🔓 Data is not encrypted")
                
                return True
                
            except Exception as e:
                print(f"⚠️ Error parsing metadata: {e}")
                return False
        
    except FileNotFoundError:
        print("❌ File not found")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    check_embedded_file()