import { useState } from 'react';
import QueryForm from './components/QueryForm';
import ReasoningTrace from './components/ReasoningTrace';
import MetricsDashboard from './components/MetricsDashboard';
import { submitQuery } from './api/client';
import './App.css';

function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleQuerySubmit = async (query) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await submitQuery(query);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to process query');
      console.error('Query error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>SIRA</h1>
        <p className="subtitle">Self-Improving Reasoning Agent</p>
      </header>

      <main className="app-main">
        <div className="left-column">
          <QueryForm onSubmit={handleQuerySubmit} isLoading={isLoading} />
          {error && (
            <div className="error-banner">
              <strong>Error:</strong> {error}
            </div>
          )}
          <MetricsDashboard />
        </div>

        <div className="right-column">
          <ReasoningTrace result={result} />
        </div>
      </main>

      <footer className="app-footer">
        <p>SIRA - Self-Improving Reasoning Agent © 2025</p>
      </footer>
    </div>
  );
}

export default App;
