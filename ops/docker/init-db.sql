-- Database initialization script for SIRA
-- Runs automatically on first PostgreSQL container start

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY,
    user_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Create queries table
CREATE TABLE IF NOT EXISTS queries (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    reasoning_steps JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    processing_time FLOAT NOT NULL,
    token_usage JSONB NOT NULL,
    quality_score FLOAT,
    quality_breakdown JSONB
);

-- Create metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    response_quality FLOAT,
    user_feedback INT
);

-- Create pattern_metadata table
CREATE TABLE IF NOT EXISTS pattern_metadata (
    id UUID PRIMARY KEY,
    quality_score FLOAT NOT NULL,
    usage_count INT NOT NULL DEFAULT 0,
    success_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_queries_session_id ON queries(session_id);
CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON queries(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_query_id ON metrics(query_id);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_pattern_metadata_quality ON pattern_metadata(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_pattern_metadata_usage ON pattern_metadata(usage_count DESC);
