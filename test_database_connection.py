"""
Database Connection Test
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_service import SteganographyDatabase

def test_database_connection():
    """Test the database connection and table access"""
    print("Testing database connection...")
    
    try:
        # Create database instance
        db = SteganographyDatabase()
        print("✅ Database instance created successfully")
        
        # Test table access - try to query users table
        print("\nTesting table access...")
        
        # Try to get a user (this will fail if table doesn't exist)
        result = db.get_user_by_email("test@example.com")
        print("✅ Users table accessible")
        
        # Try to create a test user
        print("\nTesting user creation...")
        test_user_id = db.create_user("test_user@example.com", "test_user")
        if test_user_id:
            print(f"✅ User created successfully with ID: {test_user_id}")
        else:
            print("ℹ️ User creation failed (likely already exists)")
            # Try to get existing user
            existing_user = db.get_user_by_email("test_user@example.com")
            if existing_user:
                test_user_id = existing_user['id']
                print(f"✅ Using existing user with ID: {test_user_id}")
        
        # Test operation logging
        print("\nTesting operation logging...")
        # Use a proper UUID format and ensure user exists
        if test_user_id:
            operation_id = db.log_operation_start(
                user_id=test_user_id,
                operation_type="hide",  # Must be 'hide' or 'extract'
                media_type="video",
                original_filename="test.mp4",
                password="test123"
            )
        
        if operation_id:
            print(f"✅ Operation logged successfully with ID: {operation_id}")
            
            # Test completion logging
            success = db.log_operation_complete(
                operation_id=operation_id,
                success=True,
                output_filename="stego_test.mp4",
                file_size=1024,
                message_preview="Test message",
                processing_time=1.5
            )
            
            if success:
                print("✅ Operation completion logged successfully")
            else:
                print("❌ Operation completion logging failed")
        else:
            print("❌ Operation start logging failed")
            
    except Exception as e:
        print(f"❌ Database connection test failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Check if it's a connection issue
        if "connection" in str(e).lower():
            print("\n🔧 This appears to be a connection issue.")
            print("Please check your Supabase URL and API key in supabase_config.py")
        elif "table" in str(e).lower() or "relation" in str(e).lower():
            print("\n🔧 This appears to be a missing table issue.")
            print("Please make sure you ran the SQL setup script in Supabase dashboard.")
        else:
            print(f"\n🔧 Unexpected error: {e}")

if __name__ == "__main__":
    test_database_connection()