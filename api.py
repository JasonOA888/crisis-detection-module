"""
Crisis Detection API Service
FastAPI-based REST API for crisis detection module.

Endpoints:
- POST /analyze - Analyze single text
- POST /analyze/batch - Analyze multiple texts
- GET /health - Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import time

from crisis_detection import detect_crisis, batch_detect

app = FastAPI(
    title="Crisis Detection API",
    description="Privacy-first bilingual (EN/ZH) crisis detection for text analysis. "
                "Flags potential crisis language without diagnosing or alerting.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for browser-based clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AnalyzeRequest(BaseModel):
    """Request model for single text analysis."""
    text: str = Field(..., description="Text to analyze for crisis indicators")
    language: Optional[str] = Field(None, description="Override language detection ('en' or 'zh')")
    negation_window: int = Field(5, description="Number of tokens to check for negation", ge=1, le=20)


class CrisisResponse(BaseModel):
    """Response model for crisis detection."""
    is_crisis: bool = Field(..., description="Whether crisis language was detected")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)", ge=0.0, le=1.0)
    matched_keywords: List[str] = Field(..., description="Crisis keywords that matched")
    negated_keywords: List[str] = Field(..., description="Keywords that were negated")
    language: str = Field(..., description="Detected or specified language")
    severity: str = Field(..., description="Severity level: 'none', 'low', 'medium', or 'high'")
    context_notes: List[str] = Field(..., description="Additional context information")


class BatchAnalyzeRequest(BaseModel):
    """Request model for batch text analysis."""
    texts: List[str] = Field(..., description="List of texts to analyze", min_length=1, max_length=100)
    language: Optional[str] = Field(None, description="Override language detection for all texts")


class BatchResponse(BaseModel):
    """Response model for batch analysis."""
    results: List[CrisisResponse] = Field(..., description="Detection results for each text")
    total: int = Field(..., description="Total number of texts analyzed")
    crisis_count: int = Field(..., description="Number of texts flagged as crisis")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    timestamp: float


# Endpoints
@app.post("/analyze", response_model=CrisisResponse, 
          summary="Analyze single text",
          description="Analyze a single text for crisis language indicators.")
async def analyze_text(request: AnalyzeRequest) -> CrisisResponse:
    """
    Analyze a single text for crisis language indicators.
    
    Returns confidence score, matched keywords, and severity level.
    
    Example request:
    ```json
    {
        "text": "I want to die",
        "language": null,
        "negation_window": 5
    }
    ```
    
    Example response:
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
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    result = detect_crisis(
        text=request.text,
        language=request.language,
        negation_window=request.negation_window
    )
    
    return CrisisResponse(**result)


@app.post("/analyze/batch", response_model=BatchResponse,
          summary="Analyze multiple texts",
          description="Analyze multiple texts for crisis language indicators in one request.")
async def analyze_batch(request: BatchAnalyzeRequest) -> BatchResponse:
    """
    Analyze multiple texts for crisis language indicators.
    
    Maximum 100 texts per request.
    
    Example request:
    ```json
    {
        "texts": ["I'm having a good day", "I want to die", "今天心情不错"],
        "language": null
    }
    ```
    
    Example response:
    ```json
    {
        "results": [
            {"is_crisis": false, "confidence": 0.0, ...},
            {"is_crisis": true, "confidence": 0.85, ...},
            {"is_crisis": false, "confidence": 0.0, ...}
        ],
        "total": 3,
        "crisis_count": 1
    }
    ```
    """
    results = batch_detect(request.texts, language=request.language)
    crisis_count = sum(1 for r in results if r["is_crisis"])
    
    return BatchResponse(
        results=[CrisisResponse(**r) for r in results],
        total=len(results),
        crisis_count=crisis_count
    )


@app.get("/health", response_model=HealthResponse,
         summary="Health check",
         description="Check if the API is running.")
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns service status and version.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=time.time()
    )


@app.get("/", summary="Root endpoint",
         description="Returns basic API information.")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Crisis Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "analyze": "POST /analyze",
            "batch": "POST /analyze/batch",
            "health": "GET /health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
