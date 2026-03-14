"""Tests for crisis detection module."""
import pytest
from crisis_detection import detect_crisis, detect_language, batch_detect


class TestDetectLanguage:
    def test_english_text(self):
        assert detect_language("I am feeling sad") == "en"
    
    def test_chinese_text(self):
        assert detect_language("我很伤心") == "zh"
    
    def test_mixed_text(self):
        # More Chinese characters
        assert detect_language("我今天feel sad") == "zh"
        # More English
        assert detect_language("I feel 伤心 today") == "en"


class TestDetectCrisis:
    def test_empty_text(self):
        result = detect_crisis("")
        assert result["is_crisis"] == False
        assert result["confidence"] == 0.0
    
    def test_safe_text_en(self):
        result = detect_crisis("I had a great day today!")
        assert result["is_crisis"] == False
    
    def test_safe_text_zh(self):
        result = detect_crisis("今天天气很好")
        assert result["is_crisis"] == False
    
    def test_high_severity_en(self):
        result = detect_crisis("I want to die")
        assert result["is_crisis"] == True
        assert result["severity"] == "high"
        assert result["confidence"] >= 0.8
    
    def test_high_severity_zh(self):
        result = detect_crisis("我想死")
        assert result["is_crisis"] == True
        assert result["severity"] == "high"
        assert result["language"] == "zh"
    
    def test_medium_severity_en(self):
        result = detect_crisis("I can't go on anymore")
        assert result["is_crisis"] == True
        assert result["severity"] in ["medium", "high"]
    
    def test_medium_severity_zh(self):
        result = detect_crisis("我撑不下去了")
        assert result["is_crisis"] == True
        assert result["language"] == "zh"
    
    def test_low_severity_en(self):
        result = detect_crisis("I feel hopeless sometimes")
        assert result["is_crisis"] == True
        assert result["severity"] == "low"
    
    def test_confidence_range(self):
        """Confidence should always be between 0 and 1."""
        texts = [
            "I want to kill myself",
            "我很绝望",
            "The weather is nice",
            "今天天气不错",
        ]
        for text in texts:
            result = detect_crisis(text)
            assert 0.0 <= result["confidence"] <= 1.0
    
    def test_language_override(self):
        result = detect_crisis("I want to die", language="zh")
        assert result["language"] == "zh"


class TestBatchDetect:
    def test_batch(self):
        texts = [
            "I'm having a good day",
            "I want to die",
            "今天心情不错",
            "我想死",
        ]
        results = batch_detect(texts)
        assert len(results) == 4
        assert results[0]["is_crisis"] == False
        assert results[1]["is_crisis"] == True
        assert results[2]["is_crisis"] == False
        assert results[3]["is_crisis"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
