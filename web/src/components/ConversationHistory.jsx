import { useState } from 'react';
import './ConversationHistory.css';

export default function ConversationHistory({ history, onClear, sessionId }) {
  const [expandedIndex, setExpandedIndex] = useState(null);

  const toggleExpanded = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  };

  if (history.length === 0) {
    return (
      <div className="conversation-history empty">
        <div className="empty-state">
          <h3>💬 Start a Conversation</h3>
          <p>Ask SIRA a question to begin.</p>
          <p className="tip">SIRA will remember the context of your conversation!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="conversation-history">
      <div className="conversation-header">
        <div className="header-info">
          <h3>💬 Conversation</h3>
          <span className="message-count">{history.length} message{history.length !== 1 ? 's' : ''}</span>
          {sessionId && (
            <span className="session-id" title={`Session: ${sessionId}`}>
              🔗 Connected
            </span>
          )}
        </div>
        <button 
          onClick={onClear} 
          className="clear-button"
          title="Start a new conversation"
        >
          🗑️ Clear
        </button>
      </div>

      <div className="messages-container">
        {history.map((item, index) => (
          <div key={index} className="message-pair">
            {/* User Query */}
            <div className="message user-message">
              <div className="message-header">
                <span className="message-label">👤 You</span>
                <span className="message-time">{formatTimestamp(item.timestamp)}</span>
              </div>
              <div className="message-content">
                {item.query}
              </div>
            </div>

            {/* SIRA Response */}
            <div className="message sira-message">
              <div className="message-header">
                <span className="message-label">🤖 SIRA</span>
                {item.quality_score && (
                  <span className="quality-badge" title="Quality Score">
                    ⭐ {(item.quality_score * 100).toFixed(0)}%
                  </span>
                )}
              </div>
              <div className="message-content">
                {item.response}
              </div>
              {item.reasoning_steps && item.reasoning_steps.length > 0 && (
                <button
                  className="toggle-reasoning"
                  onClick={() => toggleExpanded(index)}
                >
                  {expandedIndex === index ? '▼' : '▶'} 
                  {' '}Reasoning Steps ({item.reasoning_steps.length})
                </button>
              )}
              {expandedIndex === index && item.reasoning_steps && (
                <div className="reasoning-steps">
                  {item.reasoning_steps.map((step, stepIdx) => (
                    <div key={stepIdx} className="reasoning-step">
                      <div className="step-header">
                        <span className="step-number">Step {step.step_number}</span>
                        <span className="step-type">{step.step_type}</span>
                      </div>
                      <div className="step-content">{step.content}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
