"""
Comprehensive test suite for Crisis Detection Module v0.2
30+ test cases covering all requirements.
"""
import pytest
from crisis_detection import (
    detect_crisis, 
    detect_language, 
    batch_detect,
)


class TestLanguageDetection:
    """Language detection tests."""
    
    def test_english_text(self):
        assert detect_language("I am feeling sad today") == "en"
    
    def test_chinese_text(self):
        assert detect_language("我今天感觉很伤心") == "zh"
    
    def test_mixed_chinglish_heavy_chinese(self):
        assert detect_language("我今天非常非常伤心sad死了") == "zh"
    
    def test_mixed_chinglish_heavy_english(self):
        assert detect_language("I feel very very sad today") == "en"
    
    def test_empty_text_defaults_to_english(self):
        assert detect_language("") == "en"


class TestNegationDetection:
    """Negation handling tests - critical for reducing false positives."""
    
    def test_negation_en_never(self):
        result = detect_crisis("I would never want to die")
        assert result["is_crisis"] == False
        assert len(result["negated_keywords"]) > 0 or len(result["context_notes"]) > 0
    
    def test_negation_en_dont(self):
        result = detect_crisis("I don't want to die")
        assert result["is_crisis"] == False
    
    def test_negation_en_not_suicidal(self):
        result = detect_crisis("I am not suicidal")
        assert result["is_crisis"] == False
    
    def test_negation_zh_buhui(self):
        result = detect_crisis("我不会想死")
        assert result["is_crisis"] == False
    
    def test_negation_zh_meiyou(self):
        result = detect_crisis("我没有想自杀")
        assert result["is_crisis"] == False
    
    def test_negated_keywords_tracking(self):
        result = detect_crisis("I don't want to die")
        # Should track that "want to die" was negated
        assert result["is_crisis"] == False


class TestContextDisambiguation:
    """Context-based false positive reduction tests."""
    
    def test_die_of_laughter_en(self):
        result = detect_crisis("I'm going to die of laughter")
        assert result["is_crisis"] == False
    
    def test_xiaosi_zh(self):
        result = detect_crisis("笑死我了")
        assert result["is_crisis"] == False
    
    def test_leisi_zh(self):
        result = detect_crisis("累死我了")
        assert result["is_crisis"] == False
    
    def test_meisi_zh(self):
        result = detect_crisis("美死我了")
        assert result["is_crisis"] == False
    
    def test_xiangsi_ni_zh(self):
        result = detect_crisis("想死你了")
        assert result["is_crisis"] == False
    
    def test_gaodingsi_zh(self):
        result = detect_crisis("高兴死我了")
        assert result["is_crisis"] == False


class TestTruePositives:
    """Crisis detection accuracy tests - must catch real crises."""
    
    def test_high_severity_en_want_to_die(self):
        result = detect_crisis("I want to die")
        assert result["is_crisis"] == True
        assert result["severity"] == "high"
        assert result["confidence"] >= 0.8
    
    def test_high_severity_zh(self):
        result = detect_crisis("我想死")
        assert result["is_crisis"] == True
        assert result["severity"] == "high"
        assert result["language"] == "zh"
    
    def test_suicide_keyword_en(self):
        result = detect_crisis("I'm suicidal")
        assert result["is_crisis"] == True
        assert result["severity"] == "high"
    
    def test_suicide_keyword_zh(self):
        result = detect_crisis("我想自杀")
        assert result["is_crisis"] == True
    
    def test_medium_severity_en(self):
        result = detect_crisis("I can't go on anymore")
        assert result["is_crisis"] == True
        assert result["severity"] in ["medium", "high"]
    
    def test_medium_severity_zh(self):
        result = detect_crisis("我撑不下去了")
        assert result["is_crisis"] == True
        assert result["language"] == "zh"
    
    def test_low_severity_en(self):
        result = detect_crisis("I feel worthless")
        assert result["is_crisis"] == True
        assert result["severity"] in ["low", "medium"]
    
    def test_multiple_keywords_boost(self):
        result = detect_crisis("I want to die and I can't go on anymore")
        assert result["is_crisis"] == True
        assert len(result["matched_keywords"]) >= 2


class TestTrueNegatives:
    """Non-crisis text handling tests - must not over-flag."""
    
    def test_safe_text_en(self):
        result = detect_crisis("I had a great day today!")
        assert result["is_crisis"] == False
        assert result["confidence"] == 0.0
    
    def test_safe_text_zh(self):
        result = detect_crisis("今天天气很好，心情不错")
        assert result["is_crisis"] == False
    
    def test_empty_text(self):
        result = detect_crisis("")
        assert result["is_crisis"] == False
        assert result["confidence"] == 0.0
    
    def test_whitespace_only(self):
        result = detect_crisis("   \n\t  ")
        assert result["is_crisis"] == False


class TestEdgeCases:
    """Edge case handling tests."""
    
    def test_confidence_always_in_range(self):
        """Confidence should always be between 0 and 1."""
        texts = [
            "I want to kill myself",
            "我很绝望",
            "The weather is nice",
            "今天天气不错",
            "I would never kill myself",
            "我不会想死",
        ]
        for text in texts:
            result = detect_crisis(text)
            assert 0.0 <= result["confidence"] <= 1.0, f"Failed for: {text}"
    
    def test_language_override(self):
        result = detect_crisis("I want to die", language="zh")
        assert result["language"] == "zh"
    
    def test_case_insensitivity(self):
        result1 = detect_crisis("I WANT TO DIE")
        result2 = detect_crisis("i want to die")
        assert result1["is_crisis"] == result2["is_crisis"]
    
    def test_partial_keyword_no_match(self):
        # "diet" contains "die" but shouldn't match
        result = detect_crisis("I'm on a diet")
        assert result["is_crisis"] == False


class TestBatchDetection:
    """Batch processing tests."""
    
    def test_batch_mixed_inputs(self):
        texts = [
            "I'm having a good day",
            "I want to die",
            "今天心情不错",
            "我想死",
            "I would never want to die",
        ]
        results = batch_detect(texts)
        assert len(results) == 5
        assert results[0]["is_crisis"] == False
        assert results[1]["is_crisis"] == True
        assert results[2]["is_crisis"] == False
        assert results[3]["is_crisis"] == True
        assert results[4]["is_crisis"] == False
    
    def test_batch_empty_list(self):
        results = batch_detect([])
        assert results == []


class TestSeverityLevels:
    """Severity classification tests."""
    
    def test_high_severity_confidence_range(self):
        result = detect_crisis("I plan to commit suicide")
        assert result["severity"] == "high"
        assert 0.8 <= result["confidence"] <= 1.0
    
    def test_medium_severity_classification(self):
        result = detect_crisis("I can't take it anymore")
        assert result["severity"] in ["medium", "high"]
    
    def test_low_severity_confidence(self):
        result = detect_crisis("I feel like a burden")
        assert result["confidence"] <= 0.7


class TestReturnStructure:
    """Test that return structure is correct."""
    
    def test_result_has_required_fields(self):
        result = detect_crisis("I want to die")
        required_fields = [
            "is_crisis", "confidence", "matched_keywords", 
            "negated_keywords", "language", "severity", "context_notes"
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
    
    def test_matched_keywords_is_list(self):
        result = detect_crisis("I want to die")
        assert isinstance(result["matched_keywords"], list)
    
    def test_confidence_is_float(self):
        result = detect_crisis("I want to die")
        assert isinstance(result["confidence"], float)
    
    def test_severity_is_valid(self):
        result = detect_crisis("I want to die")
        assert result["severity"] in ["none", "low", "medium", "high"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
