import { useState, useEffect, useRef } from 'react';
import './QueryForm.css';

export default function QueryForm({ onSubmit, isLoading }) {
  const [query, setQuery] = useState('');
  const [elapsedTime, setElapsedTime] = useState(0);
  const textareaRef = useRef(null);

  // Timer for elapsed time
  useEffect(() => {
    let interval;
    if (isLoading) {
      setElapsedTime(0);
      interval = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else {
      // Focus textbox when loading completes
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query);
      setQuery(''); // Clear input after submission
    }
  };

  const handleKeyDown = (e) => {
    // Submit on Enter (but not Shift+Enter)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (query.trim() && !isLoading) {
        onSubmit(query);
        setQuery('');
      }
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="query-form-container">
      <form onSubmit={handleSubmit} className="query-form">
        <textarea
          ref={textareaRef}
          className="query-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message SIRA..."
          rows={1}
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="submit-button"
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? '...' : '↑'}
        </button>
      </form>
      {isLoading && (
        <div className="progress-info">
          <p className="progress-message">⏳ Thinking... {formatTime(elapsedTime)} / 5:00</p>
        </div>
      )}
    </div>
  );
}
