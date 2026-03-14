# Crisis Detection API

A privacy-first, bilingual (EN/ZH) crisis detection REST API service.

## Overview

This API analyzes text for crisis language indicators:
- Self-harm indicators
- Suicide ideation  
- Severe distress signals

**Important:** This API does NOT diagnose. It does NOT alert anyone. It only flags content for review.

## Features

- 🔒 Privacy-first: All processing happens locally, no external API calls
- 🌐 Bilingual: Automatic language detection for English and Chinese
- 📊 Confidence scores: Returns 0.0-1.0 confidence levels
- 🚀 Fast: Lightweight FastAPI service with async support
- 🐳 Docker-ready: One-command deployment

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Build the image
docker build -t crisis-detection-api .

# Run the container
docker run -p 8000:8000 crisis-detection-api

# Access the API
open http://localhost:8000/docs
```

### Option 2: Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn api:app --reload

# Or run directly
python api.py
```

## API Endpoints

### `POST /analyze`

Analyze a single text for crisis indicators.

**Request:**
```json
{
  "text": "I want to die",
  "language": null,
  "negation_window": 5
}
```

**Response:**
```json
{
  "is_crisis": true,
  "confidence": 0.85,
  "matched_keywords": ["want to die"],
  "negated_keywords": [],
  "language": "en",
  "severity": "high",
  "context_notes": []
}
```

### `POST /analyze/batch`

Analyze multiple texts in one request (max 100).

**Request:**
```json
{
  "texts": [
    "I'm having a good day",
    "I want to die",
    "今天心情不错"
  ],
  "language": null
}
```

**Response:**
```json
{
  "results": [
    {
      "is_crisis": false,
      "confidence": 0.0,
      "matched_keywords": [],
      "negated_keywords": [],
      "language": "en",
      "severity": "none",
      "context_notes": []
    },
    {
      "is_crisis": true,
      "confidence": 0.85,
      "matched_keywords": ["want to die"],
      "negated_keywords": [],
      "language": "en",
      "severity": "high",
      "context_notes": []
    },
    {
      "is_crisis": false,
      "confidence": 0.0,
      "matched_keywords": [],
      "negated_keywords": [],
      "language": "zh",
      "severity": "none",
      "context_notes": []
    }
  ],
  "total": 3,
  "crisis_count": 1
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": 1710460800.0
}
```

## Examples

### cURL

```bash
# Single text analysis
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I want to die"}'

# Batch analysis
curl -X POST "http://localhost:8000/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["I feel great", "I want to die"]}'

# Health check
curl "http://localhost:8000/health"
```

### Python

```python
import requests

# Single text
response = requests.post(
    "http://localhost:8000/analyze",
    json={"text": "I want to die"}
)
print(response.json())

# Batch
response = requests.post(
    "http://localhost:8000/analyze/batch",
    json={"texts": ["I'm okay", "I can't go on"]}
)
print(response.json())
```

### JavaScript

```javascript
// Single text
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'I want to die' })
});
const result = await response.json();
console.log(result);

// Batch
const batchResponse = await fetch('http://localhost:8000/analyze/batch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ texts: ['Good day', 'Bad day'] })
});
const batchResult = await batchResponse.json();
console.log(batchResult);
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `is_crisis` | boolean | Whether crisis language was detected |
| `confidence` | float | Confidence score (0.0-1.0) |
| `matched_keywords` | array | Crisis keywords that matched |
| `negated_keywords` | array | Keywords that were negated (e.g., "never kill myself") |
| `language` | string | Detected or specified language ("en" or "zh") |
| `severity` | string | Severity level: "none", "low", "medium", "high" |
| `context_notes` | array | Additional context information |

## Severity Levels

| Level | Confidence Range | Description |
|-------|------------------|-------------|
| `none` | 0.0 | No crisis indicators |
| `low` | 0.3-0.5 | Mild indicators present |
| `medium` | 0.5-0.8 | Moderate crisis language |
| `high` | 0.8-1.0 | Severe crisis indicators |

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Client    │────▶│  FastAPI     │────▶│ Crisis Detection│
│  (HTTP)     │◀────│  Server      │◀────│    Module       │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                    ┌──────┴──────┐
                    │  Negation   │
                    │  Detection  │
                    └─────────────┘
```

## Privacy

- **No data logging**: Requests are not stored
- **No external calls**: All processing is local
- **Stateless**: No database or persistence
- **Self-contained**: Single container deployment

## License

MIT

## Organization

**Human & AI Initiative**  
Department: Product & Engineering  
