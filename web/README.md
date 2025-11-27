# SIRA Web Interface

React-based web interface for the Self-Improving Reasoning Agent (SIRA).

## Features

- **Query Submission**: Submit queries to SIRA and see real-time processing
- **Reasoning Trace Visualization**: Expandable step-by-step view of the reasoning process with quality scores
- **Metrics Dashboard**: Real-time system metrics including query count, quality, latency, and cache performance

## Technology Stack

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Axios**: HTTP client for API communication
- **CSS**: Custom styling (no heavy frameworks)

## Development

### Local Development

```bash
cd web
npm install
npm run dev
```

The app will be available at http://localhost:3000

### Docker Development

From the project root:

```bash
cd ops/docker
docker-compose up sira-web
```

## Project Structure

```
web/
├── src/
│   ├── api/
│   │   └── client.js          # API client for backend communication
│   ├── components/
│   │   ├── QueryForm.jsx       # Query input component
│   │   ├── ReasoningTrace.jsx  # Reasoning visualization component
│   │   └── MetricsDashboard.jsx # Metrics display component
│   ├── App.jsx                 # Main application component
│   ├── App.css                 # Application styles
│   ├── main.jsx                # React entry point
│   └── index.css               # Global styles
├── index.html                  # HTML entry point
├── package.json                # Dependencies
└── vite.config.js             # Vite configuration
```

## Components

### QueryForm
- Text area for query input
- Submit button with loading state
- Disabled state during processing

### ReasoningTrace
- Collapsible reasoning steps
- Quality scores for each step
- Pattern usage information
- Final response display

### MetricsDashboard
- Total queries processed
- Average quality score
- Average latency
- Pattern storage stats
- Pattern reuse rate
- Cache hit rate

## API Integration

The web interface communicates with the SIRA API through the `/api` proxy configured in Vite:

- `POST /query` - Submit queries
- `GET /metrics/summary` - Get system metrics
- `GET /metrics/core` - Get core SIRA metrics
- `GET /session/{id}` - Get session history

## Acceptance Criteria

✅ **AC-082**: Web interface loads at http://localhost:3000 with query submission form  
✅ **AC-083**: Reasoning trace rendered as expandable steps with quality scores  
✅ **AC-084**: Metrics dashboard displays real-time stats from /metrics/summary

## Environment Variables

- `VITE_API_BASE_URL`: API base URL (default: `/api` for proxy)

## Building for Production

```bash
npm run build
```

Outputs to `dist/` directory.

## Browser Support

- Modern browsers with ES6+ support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
