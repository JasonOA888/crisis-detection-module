"""
Crisis Detection Module v0.1
A privacy-first, bilingual crisis language detector.

IMPORTANT: This module does NOT diagnose. It does NOT alert anyone.
It only flags content that may need human review.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CrisisResult:
    """Result of crisis detection analysis."""
    is_crisis: bool
    confidence: float
    matched_keywords: List[str]
    language: str
    severity: str  # "low", "medium", "high"


# Crisis keywords organized by severity
# These are patterns, not exact matches - designed to minimize false positives

CRISIS_KEYWORDS = {
    "en": {
        "high": [
            r"\bwant to (die|kill myself|end it)\b",
            r"\bgoing to (kill myself|commit suicide|end my life)\b",
            r"\b(plan|planning) to (kill myself|commit suicide)\b",
            r"\b(suicidal|suicide)\b",
            r"\b(end my life|take my life)\b",
            r"\b(harm myself|hurting myself)\b",
            r"\b(cut myself|cutting myself)\b",
            r"\b(kill me|killing me)\b",
        ],
        "medium": [
            r"\b(can't (go on|live|take it) anymore)\b",
            r"\b(no (point|reason) (in living|to live))\b",
            r"\b(better off (dead|without me))\b",
            r"\b(wish I (was|were) dead)\b",
            r"\b(want to (disappear|vanish))\b",
            r"\b(tired of living|done with life)\b",
            r"\b(hopeless|helpless)\b",
            r"\b(give up)\b",
        ],
        "low": [
            r"\b(feel(ing)? (hopeless|worthless|trapped))\b",
            r"\b(no (hope|future))\b",
            r"\b(everything is (pointless|meaningless))\b",
            r"\b(burden to (everyone|others))\b",
        ],
    },
    "zh": {
        "high": [
            r"想(要)?死",
            r"自杀",
            r"不想活(了)?",
            r"结束生命",
            r"结束自己",
            r"去死",
            r"活(得)?太累",
            r"伤害自己",
            r"割腕",
            r"跳楼",
            r"服毒",
        ],
        "medium": [
            r"没(有)?意义",
            r"活(着)?没意思",
            r"看不到希望",
            r"绝望",
            r"撑不下去了",
            r"坚持不下去",
            r"想放弃",
            r"想消失",
        ],
        "low": [
            r"很痛苦",
            r"很累",
            r"没人理解",
            r"没人(在乎|关心)",
            r"是个累赘",
            r"没价值",
        ],
    },
}


def detect_language(text: str) -> str:
    """Detect if text is primarily Chinese or English."""
    # Count Chinese characters
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    total_chars = len(re.findall(r"\w", text))
    
    if total_chars == 0:
        return "en"  # Default to English
    
    chinese_ratio = chinese_chars / total_chars
    return "zh" if chinese_ratio > 0.3 else "en"


def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    # Convert to lowercase for English
    text = text.lower()
    # Normalize whitespace
    text = " ".join(text.split())
    return text


def detect_crisis(text: str, language: Optional[str] = None) -> Dict:
    """
    Analyze text for crisis language indicators.
    
    Args:
        text: Input text to analyze
        language: Override language detection ("en" or "zh")
    
    Returns:
        Dictionary with:
        - is_crisis: bool
        - confidence: float (0.0-1.0)
        - matched_keywords: list of matched keyword strings
        - language: detected/specified language
        - severity: "low", "medium", or "high"
    
    Example:
        >>> detect_crisis("I want to die")
        {"is_crisis": True, "confidence": 0.9, "matched_keywords": ["want to die"], "language": "en", "severity": "high"}
    """
    if not text or not text.strip():
        return {
            "is_crisis": False,
            "confidence": 0.0,
            "matched_keywords": [],
            "language": language or "en",
            "severity": "none"
        }
    
    # Detect or use provided language
    detected_lang = language or detect_language(text)
    normalized_text = normalize_text(text)
    
    # Get keywords for detected language, fallback to English
    keywords = CRISIS_KEYWORDS.get(detected_lang, CRISIS_KEYWORDS["en"])
    
    matched = {
        "high": [],
        "medium": [],
        "low": [],
    }
    
    # Check each severity level
    for severity, patterns in keywords.items():
        for pattern in patterns:
            if re.search(pattern, normalized_text, re.IGNORECASE):
                # Extract the matched text
                match = re.search(pattern, normalized_text, re.IGNORECASE)
                if match:
                    matched[severity].append(match.group())
    
    # Calculate results
    all_matched = matched["high"] + matched["medium"] + matched["low"]
    
    if not all_matched:
        return {
            "is_crisis": False,
            "confidence": 0.0,
            "matched_keywords": [],
            "language": detected_lang,
            "severity": "none"
        }
    
    # Determine severity and confidence
    if matched["high"]:
        severity = "high"
        # High severity keywords = 0.8-1.0 confidence
        confidence = min(0.95, 0.8 + len(matched["high"]) * 0.05)
    elif matched["medium"]:
        severity = "medium"
        # Medium severity = 0.5-0.8 confidence
        confidence = min(0.8, 0.5 + len(matched["medium"]) * 0.1)
    else:
        severity = "low"
        # Low severity = 0.3-0.5 confidence
        confidence = min(0.5, 0.3 + len(matched["low"]) * 0.1)
    
    # Boost confidence if multiple severity levels matched
    if matched["high"] and matched["medium"]:
        confidence = min(1.0, confidence + 0.05)
    
    return {
        "is_crisis": True,
        "confidence": round(confidence, 2),
        "matched_keywords": all_matched,
        "language": detected_lang,
        "severity": severity
    }


def batch_detect(texts: List[str], language: Optional[str] = None) -> List[Dict]:
    """
    Analyze multiple texts for crisis indicators.
    
    Args:
        texts: List of input texts
        language: Override language detection
    
    Returns:
        List of detection results
    """
    return [detect_crisis(text, language) for text in texts]


# CLI interface
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python crisis_detection.py \"text to analyze\"")
        print("       python crisis_detection.py --interactive")
        sys.exit(1)
    
    if sys.argv[1] == "--interactive":
        print("Crisis Detection Module v0.1")
        print("Type 'quit' to exit\n")
        while True:
            try:
                text = input("Enter text: ")
                if text.lower() == "quit":
                    break
                result = detect_crisis(text)
                print(json.dumps(result, indent=2, ensure_ascii=False))
                print()
            except (EOFError, KeyboardInterrupt):
                break
    else:
        text = " ".join(sys.argv[1:])
        result = detect_crisis(text)
        print(json.dumps(result, indent=2, ensure_ascii=False))
