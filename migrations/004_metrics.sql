-- Migration 004: Metrics tracking table
-- Creates comprehensive metrics storage for query, pattern, and system performance

CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Query-level metrics (nullable for pattern/system metrics)
    query_id UUID REFERENCES queries(id) ON DELETE CASCADE,
    query_latency_ms INTEGER,
    quality_score FLOAT,
    iteration_count INTEGER,
    patterns_retrieved INTEGER,
    patterns_applied INTEGER,
    
    -- Pattern-level metrics (nullable for query/system metrics)
    pattern_id VARCHAR(100),
    pattern_effectiveness FLOAT,
    
    -- System-level metrics (nullable for query/pattern metrics)
    total_queries INTEGER,
    avg_quality FLOAT,
    avg_latency_ms INTEGER,
    pattern_library_size INTEGER,
    domain_coverage INTEGER
);

-- Indexes for efficient querying
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX idx_metrics_query ON metrics(query_id) WHERE query_id IS NOT NULL;
CREATE INDEX idx_metrics_pattern ON metrics(pattern_id) WHERE pattern_id IS NOT NULL;

-- Index for trend analysis
CREATE INDEX idx_metrics_quality_time ON metrics(timestamp, quality_score) 
    WHERE quality_score IS NOT NULL;

COMMENT ON TABLE metrics IS 'Comprehensive metrics tracking for SIRA performance monitoring';
COMMENT ON COLUMN metrics.query_id IS 'Reference to query for query-level metrics';
COMMENT ON COLUMN metrics.pattern_id IS 'Pattern identifier for pattern-level metrics';
COMMENT ON COLUMN metrics.query_latency_ms IS 'Total query processing time in milliseconds';
COMMENT ON COLUMN metrics.quality_score IS 'Final quality score (0.0-1.0)';
COMMENT ON COLUMN metrics.iteration_count IS 'Number of refinement iterations performed';
COMMENT ON COLUMN metrics.pattern_effectiveness IS 'Average quality improvement from pattern usage';
