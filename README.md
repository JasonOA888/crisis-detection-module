# Crisis Detection API

[![CI](https://github.com/JasonOA888/crisis-detection-module/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonOA888/crisis-detection-module/actions/workflows/ci.yml)

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
- ✅ CI/CD: Automated testing and Docker builds

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
  "results": [...],
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

## Development

### Run Tests

```bash
pip install pytest
pytest test_crisis_detection.py -v
```

### Lint

```bash
pip install ruff
ruff check crisis_detection.py api.py
```

## Examples

### cURL

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I want to die"}'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={"text": "I want to die"}
)
print(response.json())
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'I want to die' })
});
const result = await response.json();
```

## License

MIT

---

**Human & AI Initiative** | Department: Product & Engineering
