-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text UNIQUE NOT NULL,
    username text UNIQUE NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Steganography operations table
CREATE TABLE IF NOT EXISTS steganography_operations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    operation_type text NOT NULL CHECK (operation_type IN ('hide', 'extract')),
    media_type text NOT NULL CHECK (media_type IN ('video', 'audio', 'image', 'document')),
    original_filename text NOT NULL,
    output_filename text,
    file_size bigint,
    message_preview text,
    password_hash text NOT NULL,
    encryption_method text DEFAULT 'xor_md5',
    success boolean DEFAULT false,
    error_message text,
    processing_time real,
    created_at timestamp with time zone DEFAULT now()
);

-- File metadata table
CREATE TABLE IF NOT EXISTS file_metadata (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_id uuid REFERENCES steganography_operations(id) ON DELETE CASCADE,
    file_type text NOT NULL,
    mime_type text,
    file_path text,
    file_hash text,
    file_size bigint,
    dimensions text,
    duration real,
    created_at timestamp with time zone DEFAULT now()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_operations_user_id ON steganography_operations(user_id);
CREATE INDEX IF NOT EXISTS idx_operations_created_at ON steganography_operations(created_at);
CREATE INDEX IF NOT EXISTS idx_operations_media_type ON steganography_operations(media_type);
CREATE INDEX IF NOT EXISTS idx_metadata_operation_id ON file_metadata(operation_id);