#!/usr/bin/env python3

def test_imports():
    """Test if all steganography managers can be imported and used."""
    try:
        print("Testing imports...")
        
        # Test SimpleSteganographyManager
        from simple_stego import SimpleSteganographyManager
        print("✅ SimpleSteganographyManager imported")
        
        simple_manager = SimpleSteganographyManager("test123")
        print("✅ SimpleSteganographyManager created")
        
        # Test SteganographyManager
        from stego_cli import SteganographyManager
        print("✅ SteganographyManager imported")
        
        basic_manager = SteganographyManager("test123")
        print("✅ SteganographyManager created")
        
        # Test if we can create test files
        import os
        print("\nChecking directories...")
        for directory in ["uploads", "outputs", "temp"]:
            if os.path.exists(directory):
                print(f"✅ {directory} directory exists")
            else:
                print(f"❌ {directory} directory missing")
                os.makedirs(directory)
                print(f"✅ Created {directory} directory")
        
        print("\n✅ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()