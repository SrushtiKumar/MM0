#!/usr/bin/env python3
"""
Alternative Database Setup Script
This script creates the database tables without requiring special Supabase functions
"""
import os
import sys
from pathlib import Path

def create_tables_via_direct_connection():
    """
    Create tables using direct PostgreSQL connection
    """
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Get database URL from environment
        database_url = os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL")
        
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            print("Please set DATABASE_URL or use the Supabase dashboard method")
            return False
        
        # Parse database URL
        parsed = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        
        # Read SQL file
        sql_file = Path(__file__).parent / "SUPABASE_SETUP.sql"
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        # Execute SQL
        cursor.execute(sql_content)
        conn.commit()
        
        print("✅ Tables created successfully via direct connection!")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def setup_via_supabase_dashboard():
    """
    Instructions for manual setup via Supabase dashboard
    """
    print("\n" + "="*60)
    print("🔧 MANUAL DATABASE SETUP INSTRUCTIONS")
    print("="*60)
    print("\nSince automatic setup failed, please follow these steps:")
    print("\n1. Open your Supabase project dashboard:")
    print("   https://app.supabase.com")
    print("\n2. Navigate to 'SQL Editor' in the left sidebar")
    print("\n3. Click 'New Query'")
    print("\n4. Copy the contents of 'SUPABASE_SETUP.sql' file")
    print("   (located in the same directory as this script)")
    print("\n5. Paste the SQL code into the editor")
    print("\n6. Click 'RUN' to execute the setup")
    print("\n7. Verify that tables were created successfully")
    print("\n" + "="*60)
    print("After completing these steps, your database will be ready!")
    print("="*60)

def test_database_connection():
    """
    Test if database tables exist and are accessible
    """
    try:
        from supabase_service import SteganographyDatabase
        
        print("🔄 Testing database connection...")
        db = SteganographyDatabase()
        
        # Try to query the operations table
        result = db.supabase.table('steganography_operations').select('*').limit(1).execute()
        
        print("✅ Database connection successful!")
        print("✅ steganography_operations table is accessible!")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if 'PGRST205' in error_msg or 'table' in error_msg.lower():
            print("❌ Tables not found - setup required")
        else:
            print(f"❌ Database connection failed: {e}")
        return False

def main():
    """
    Main function - try different setup methods
    """
    print("🔧 DATABASE SETUP FOR STEGANOGRAPHY APPLICATION")
    print("=" * 50)
    
    # First, test if database is already set up
    if test_database_connection():
        print("\n✅ Database is already set up and working!")
        print("No further action required.")
        return
    
    print("\n🔄 Database setup required...")
    
    # Method 1: Try direct connection setup
    print("\nMethod 1: Attempting automatic setup...")
    if create_tables_via_direct_connection():
        print("✅ Automatic setup successful!")
        
        # Test again
        if test_database_connection():
            print("✅ Database verified - ready to use!")
            return
    
    # Method 2: Manual setup instructions
    print("\nMethod 2: Manual setup required")
    setup_via_supabase_dashboard()

if __name__ == "__main__":
    main()