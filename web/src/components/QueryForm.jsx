import { useState } from 'react';
import './QueryForm.css';

export default function QueryForm({ onSubmit, isLoading }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query);
    }
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
          {isLoading ? 'Processing...' : 'Submit Query'}
        </button>
      </form>
    </div>
  );
}
