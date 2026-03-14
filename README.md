# Crisis Detection Module

A privacy-first, bilingual (EN/ZH) crisis detection module for text analysis.

## Overview

This module analyzes text input and flags potential crisis language:
- Self-harm indicators
- Suicide ideation
- Severe distress signals

**Important:** This module does NOT diagnose. It does NOT alert anyone. It only flags content for review.

## Features

- 🔒 Privacy-first: No data leaves your system
- 🌐 Bilingual: English and Chinese support
- 📊 Confidence scores: Returns 0.0-1.0, not just boolean
- ⚡ Lightweight: Pure Python, minimal dependencies

## Installation

```bash
pip install crisis-detection
```

## Quick Start

```python
from crisis_detection import detect_crisis

result = detect_crisis("I can't go on anymore")
print(result)
# {"is_crisis": True, "confidence": 0.85, "matched_keywords": ["can't go on"], "language": "en"}
```

## API

### `detect_crisis(text: str) -> dict`

**Parameters:**
- `text` (str): Input text to analyze

**Returns:**
- `is_crisis` (bool): Whether crisis language was detected
- `confidence` (float): Confidence score 0.0-1.0
- `matched_keywords` (list): Keywords that triggered detection
- `language` (str): Detected language ("en" or "zh")

## License

MIT
