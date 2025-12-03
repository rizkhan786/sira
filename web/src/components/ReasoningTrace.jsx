import { useState } from 'react';
import './ReasoningTrace.css';

function ReasoningStep({ step, index }) {
  const [isExpanded, setIsExpanded] = useState(index === 0);

  return (
    <div className="reasoning-step">
      <div 
        className="step-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="step-number">Step {step.step_number || index + 1}</span>
        <span className="step-title">{step.description || step.step_type || 'Reasoning Step'}</span>
        {step.quality_score !== undefined && (
          <span className="quality-score">
            Quality: {(step.quality_score * 100).toFixed(0)}%
          </span>
        )}
        <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>▼</span>
      </div>
      {isExpanded && (
        <div className="step-content">
          {step.reasoning && (
            <div className="step-reasoning">
              <strong>Reasoning:</strong>
              <p>{step.reasoning}</p>
            </div>
          )}
          {step.result && (
            <div className="step-result">
              <strong>Result:</strong>
              <p>{step.result}</p>
            </div>
          )}
          {step.patterns_used && step.patterns_used.length > 0 && (
            <div className="step-patterns">
              <strong>Patterns Used:</strong>
              <ul>
                {step.patterns_used.map((pattern, i) => (
                  <li key={i}>{pattern}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ReasoningTrace({ result }) {
  if (!result) {
    return (
      <div className="reasoning-trace-container">
        <h2>Reasoning Trace</h2>
        <p className="empty-message">Submit a query to see the reasoning process...</p>
      </div>
    );
  }

  const { response, reasoning_steps, metadata } = result;
  const quality_score = metadata?.quality_score;
  const patterns_retrieved = metadata?.patterns_retrieved_count;

  return (
    <div className="reasoning-trace-container">
      <h2>Reasoning Trace</h2>
      
      <div className="trace-summary">
        <div className="summary-item">
          <strong>Overall Quality:</strong> {(quality_score * 100).toFixed(0)}%
        </div>
        {patterns_retrieved !== undefined && (
          <div className="summary-item">
            <strong>Patterns Retrieved:</strong> {patterns_retrieved}
          </div>
        )}
      </div>

      {reasoning_steps && reasoning_steps.length > 0 && (
        <div className="trace-steps">
          {reasoning_steps.map((step, index) => (
            <ReasoningStep key={index} step={step} index={index} />
          ))}
        </div>
      )}

      <div className="final-response">
        <h3>Final Response</h3>
        <p>{response}</p>
      </div>
    </div>
  );
}
