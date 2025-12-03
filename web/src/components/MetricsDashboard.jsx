import { useState, useEffect } from 'react';
import { getMetrics } from '../api/client';
import './MetricsDashboard.css';

export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMetrics();
    // Refresh metrics every 10 seconds
    const interval = setInterval(fetchMetrics, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const data = await getMetrics();
      setMetrics(data);
      setError(null);
    } catch (err) {
      setError('Failed to load metrics');
      console.error('Metrics fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="metrics-dashboard">
        <h2>System Metrics</h2>
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="metrics-dashboard">
        <h2>System Metrics</h2>
        <p className="error-message">{error}</p>
      </div>
    );
  }

  return (
    <div className="metrics-dashboard">
      <h2>System Metrics</h2>
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Total Queries</div>
          <div className="metric-value">{metrics?.total_queries || 0}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Avg Quality</div>
          <div className="metric-value">
            {metrics?.avg_quality ? (metrics.avg_quality * 100).toFixed(1) + '%' : 'N/A'}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Avg Latency</div>
          <div className="metric-value">
            {metrics?.avg_latency_ms ? (metrics.avg_latency_ms / 1000).toFixed(1) + 's' : 'N/A'}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Patterns Stored</div>
          <div className="metric-value">{metrics?.pattern_library_size || 0}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Pattern Reuse Rate</div>
          <div className="metric-value">
            {metrics?.pattern_reuse_rate ? (metrics.pattern_reuse_rate * 100).toFixed(1) + '%' : 'N/A'}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Cache Hit Rate</div>
          <div className="metric-value">
            {metrics?.cache_hit_rate ? (metrics.cache_hit_rate * 100).toFixed(1) + '%' : 'N/A'}
          </div>
        </div>
      </div>
    </div>
  );
}
