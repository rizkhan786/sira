-- Migration: Create pattern_usage table for tracking pattern application
-- Sprint: 3
-- Deliverable: DEL-007 (Pattern Application Logic)

CREATE TABLE IF NOT EXISTS pattern_usage (
    id UUID PRIMARY KEY,
    query_id UUID REFERENCES queries(id) ON DELETE CASCADE,
    pattern_id VARCHAR(100) NOT NULL,
    similarity_score FLOAT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effectiveness_score FLOAT,
    improved_quality BOOLEAN
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_pattern_usage_pattern ON pattern_usage(pattern_id);
CREATE INDEX IF NOT EXISTS idx_pattern_usage_query ON pattern_usage(query_id);
CREATE INDEX IF NOT EXISTS idx_pattern_usage_applied_at ON pattern_usage(applied_at);

-- Index for effectiveness analysis
CREATE INDEX IF NOT EXISTS idx_pattern_usage_effectiveness 
    ON pattern_usage(pattern_id, effectiveness_score) 
    WHERE effectiveness_score IS NOT NULL;

COMMENT ON TABLE pattern_usage IS 'Tracks when patterns are applied to queries and their effectiveness';
COMMENT ON COLUMN pattern_usage.similarity_score IS 'Similarity between query and pattern (0-1)';
COMMENT ON COLUMN pattern_usage.effectiveness_score IS 'Quality improvement from using pattern';
COMMENT ON COLUMN pattern_usage.improved_quality IS 'Whether quality improved with pattern';
