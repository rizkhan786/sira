import { useState, useEffect, useRef } from 'react';
import QueryForm from './components/QueryForm';
import ReasoningTrace from './components/ReasoningTrace';
import MetricsDashboard from './components/MetricsDashboard';
import ConversationHistory from './components/ConversationHistory';
import { submitQuery } from './api/client';
import './App.css';

function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);

  const handleQuerySubmit = async (query) => {
    setIsLoading(true);
    setError(null);
    try {
      // Submit query with session ID to maintain conversation
      const data = await submitQuery(query, sessionId);
      
      // Update or set session ID
      if (!sessionId && data.session_id) {
        setSessionId(data.session_id);
      }
      
      // Add to conversation history
      setConversationHistory(prev => [
        ...prev,
        {
          query: query,
          response: data.response,
          timestamp: new Date().toISOString(),
          quality_score: data.metadata?.quality_score,
          reasoning_steps: data.reasoning_steps
        }
      ]);
      
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to process query');
      console.error('Query error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearConversation = () => {
    setConversationHistory([]);
    setSessionId(null);
    setResult(null);
    setError(null);
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
          <ConversationHistory 
            history={conversationHistory}
            onClear={handleClearConversation}
            sessionId={sessionId}
          />
        </div>

        <div className="right-column">
          <MetricsDashboard />
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
