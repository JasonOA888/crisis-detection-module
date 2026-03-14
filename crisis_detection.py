"""
Crisis Detection Module v0.2
A privacy-first, bilingual crisis language detector.

v0.2 improvements:
- Negation detection: "I would never kill myself" → NOT crisis
- Context disambiguation: "die of laughter" vs "want to die"
- Enhanced bilingual support with mixed-language handling
- Comprehensive test coverage (30+ cases)

IMPORTANT: This module does NOT diagnose. It does NOT alert anyone.
It only flags content that may need human review.
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class CrisisResult:
    """Result of crisis detection analysis."""
    is_crisis: bool
    confidence: float
    matched_keywords: List[str]
    negated_keywords: List[str]
    language: str
    severity: str
    context_notes: List[str]


# Negation words by language
NEGATION_WORDS = {
    "en": {
        "never", "not", "no", "don't", "dont", "didn't", "didnt", 
        "wouldn't", "wouldnt", "couldn't", "couldnt", "won't", "wont",
        "doesn't", "doesnt", "isn't", "isnt", "aren't", "arent",
        "haven't", "havent", "hasn't", "hasnt", "hadn't", "hadnt",
        "without", "lack", "lacking", "free", "rid"
    },
    "zh": {
        "不", "不会", "不想", "没有", "没", "并非", "不是",
        "从未", "决不", "绝不", "并不", "再也不会"
    }
}

# Context phrases that indicate non-crisis usage
# These are checked BEFORE crisis keywords
CONTEXT_EXCEPTIONS = {
    "en": [
        r"\bdie (of|from) (laughter|laughing|embarrassment|joy|happiness|boredom)\b",
        r"\bdying (of|from) (laughter|laughing|embarrassment|joy|happiness)\b",
        r"\bkill (myself )?laughing\b",
        r"\bkill (the|this) (vibe|mood|party|buzz)\b",
        r"\b(kill|destroy) it\b",  # "you're killing it!"
        r"\bgive up (on )?(coffee|diet|exercise|smoking|drinking)\b",
    ],
    "zh": [
        r"笑死(我了)?(啊|呀|哈哈)?$",  # 笑死我了 - laughing to death
        r"笑(得|到).{0,5}死",  # 笑得要死
        r"高兴死(我了)?",  # happy to death
        r"开心死(我了)?",  
        r"乐死(我了)?",
        r"美死(我了)?",
        r"累死(我了)?",  # tired to death
        r"饿死(我了)?",  
        r"急死(我了)?",
        r"气死(我了)?",  # angry to death
        r"想死(你|你们|您)",  # miss you to death
        r"^死(都不|也不)",  # even if I die, I won't...
        r"不(会|想|能)死",  # won't die / don't want to die
    ]
}

# Crisis keywords organized by severity
CRISIS_KEYWORDS = {
    "en": {
        "high": [
            r"\bwant to (die|kill myself|end it)\b",
            r"\bgoing to (kill myself|commit suicide|end my life)\b",
            r"\b(plan|planning|planned) to (kill myself|commit suicide)\b",
            r"\b(suicidal|suicide)\b",
            r"\b(end my life|take my life)\b",
            r"\b(harm myself|hurting myself)\b",
            r"\b(cut myself|cutting myself)\b",
        ],
        "medium": [
            r"\b(can't (go on|live|take it) anymore)\b",
            r"\b(no (point|reason) (in living|to live))\b",
            r"\b(better off (dead|without me))\b",
            r"\b(wish I (was|were) dead)\b",
            r"\b(want to (disappear|vanish))\b",
            r"\b(tired of living|done with life)\b",
            r"\bgive up\b",
        ],
        "low": [
            r"\b(feel(ing)? (worthless|trapped|empty))\b",
            r"\b(no (hope|future))\b",
            r"\b(everything is (pointless|meaningless))\b",
            r"\b(burden to (everyone|others|family))\b",
        ],
    },
    "zh": {
        "high": [
            r"想(要)?死(?!(你|你们|您))",  # 想死 but not 想死你
            r"自杀",
            r"不想活(了)?",
            r"结束生命",
            r"结束自己",
            r"去死",
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
            r"没人理解",
            r"没人(在乎|关心)",
            r"是个累赘",
            r"没价值",
        ],
    },
}


def detect_language(text: str) -> str:
    """Detect if text is primarily Chinese or English."""
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    english_chars = len(re.findall(r"[a-zA-Z]", text))
    total_chars = chinese_chars + english_chars
    
    if total_chars == 0:
        return "en"
    
    return "zh" if chinese_chars / total_chars > 0.25 else "en"


def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    return " ".join(text.lower().split())


def find_negation_in_text(text: str, keyword: str, language: str, window: int = 5) -> bool:
    """Check if there's a negation word within window before the keyword."""
    negation_words = NEGATION_WORDS.get(language, NEGATION_WORDS["en"])
    normalized = normalize_text(text)
    
    keyword_pos = normalized.find(keyword.lower())
    if keyword_pos == -1:
        return False
    
    text_before = normalized[:keyword_pos]
    
    if language == "zh":
        chars_to_check = text_before[-window*2:]
        return any(char in negation_words for char in chars_to_check)
    else:
        words_before = text_before.split()[-window:]
        return any(word.strip(".,!?;:\"'") in negation_words for word in words_before)


def check_context_exceptions(text: str, language: str) -> Tuple[bool, Optional[str]]:
    """Check if text matches a non-crisis context pattern."""
    patterns = CONTEXT_EXCEPTIONS.get(language, [])
    normalized = normalize_text(text)
    
    for pattern in patterns:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True, pattern
    
    return False, None


def detect_crisis(text: str, language: Optional[str] = None, 
                  negation_window: int = 5) -> Dict:
    """
    Analyze text for crisis language indicators with negation detection.
    
    Args:
        text: Input text to analyze
        language: Override language detection ("en" or "zh")
        negation_window: Number of tokens to check for negation (default 5)
    
    Returns:
        Dictionary with detection results
    """
    if not text or not text.strip():
        return {
            "is_crisis": False,
            "confidence": 0.0,
            "matched_keywords": [],
            "negated_keywords": [],
            "language": language or "en",
            "severity": "none",
            "context_notes": []
        }
    
    detected_lang = language or detect_language(text)
    normalized_text = normalize_text(text)
    context_notes = []
    
    # Check context exceptions first
    is_exception, exception_pattern = check_context_exceptions(normalized_text, detected_lang)
    if is_exception:
        context_notes.append(f"Non-crisis context: '{exception_pattern}'")
        return {
            "is_crisis": False,
            "confidence": 0.0,
            "matched_keywords": [],
            "negated_keywords": [],
            "language": detected_lang,
            "severity": "none",
            "context_notes": context_notes
        }
    
    keywords = CRISIS_KEYWORDS.get(detected_lang, CRISIS_KEYWORDS["en"])
    
    matched = {"high": [], "medium": [], "low": []}
    negated = {"high": [], "medium": [], "low": []}
    
    for severity, patterns in keywords.items():
        for pattern in patterns:
            if re.search(pattern, normalized_text, re.IGNORECASE):
                match = re.search(pattern, normalized_text, re.IGNORECASE)
                if match:
                    keyword = match.group()
                    
                    if find_negation_in_text(text, keyword, detected_lang, negation_window):
                        negated[severity].append(keyword)
                        context_notes.append(f"Negated: '{keyword}'")
                    else:
                        matched[severity].append(keyword)
    
    all_matched = matched["high"] + matched["medium"] + matched["low"]
    all_negated = negated["high"] + negated["medium"] + negated["low"]
    
    if not all_matched:
        return {
            "is_crisis": False,
            "confidence": 0.0,
            "matched_keywords": [],
            "negated_keywords": all_negated,
            "language": detected_lang,
            "severity": "none",
            "context_notes": context_notes
        }
    
    if matched["high"]:
        severity = "high"
        confidence = min(0.95, 0.8 + len(matched["high"]) * 0.05)
    elif matched["medium"]:
        severity = "medium"
        confidence = min(0.8, 0.5 + len(matched["medium"]) * 0.1)
    else:
        severity = "low"
        confidence = min(0.5, 0.3 + len(matched["low"]) * 0.1)
    
    if sum(1 for s in ["high", "medium", "low"] if matched[s]) > 1:
        confidence = min(1.0, confidence + 0.05)
        context_notes.append("Multiple severity indicators")
    
    if all_negated:
        confidence = max(0.3, confidence - 0.1 * len(all_negated))
        context_notes.append(f"{len(all_negated)} negated keyword(s)")
    
    return {
        "is_crisis": True,
        "confidence": round(confidence, 2),
        "matched_keywords": all_matched,
        "negated_keywords": all_negated,
        "language": detected_lang,
        "severity": severity,
        "context_notes": context_notes
    }


def batch_detect(texts: List[str], language: Optional[str] = None) -> List[Dict]:
    """Analyze multiple texts for crisis indicators."""
    return [detect_crisis(text, language) for text in texts]


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Crisis Detection Module v0.2")
        print("Usage: python crisis_detection.py \"text to analyze\"")
        print("       python crisis_detection.py --interactive")
        sys.exit(1)
    
    if sys.argv[1] == "--interactive":
        print("Crisis Detection Module v0.2")
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
