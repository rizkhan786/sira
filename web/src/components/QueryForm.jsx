import { useState, useEffect } from 'react';
import './QueryForm.css';

export default function QueryForm({ onSubmit, isLoading }) {
  const [query, setQuery] = useState('');
  const [elapsedTime, setElapsedTime] = useState(0);

  // Timer for elapsed time
  useEffect(() => {
    let interval;
    if (isLoading) {
      setElapsedTime(0);
      interval = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="query-form-container">
      <h2>Submit Query</h2>
      <form onSubmit={handleSubmit} className="query-form">
        <textarea
          className="query-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query here... (e.g., What is 2 + 2?)"
          rows={4}
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="submit-button"
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? (
            <span>
              Processing... {formatTime(elapsedTime)}
              {elapsedTime > 30 && <span className="slow-warning"> (Taking longer than usual)</span>}
            </span>
          ) : 'Submit Query'}
        </button>
        {isLoading && (
          <div className="progress-info">
            <p>⏳ SIRA is thinking... This may take up to 5 minutes for complex queries.</p>
            <p className="progress-details">
              Elapsed: {formatTime(elapsedTime)} / 5:00 max
            </p>
          </div>
        )}
      </form>
    </div>
  );
}
