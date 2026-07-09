import pytest
from pydantic import ValidationError
from models.schemas import CommitAnalysis, ChangedFile, CommitGroup, CommitType

def test_valid_commit_analysis():
    data = {
        "summary": "Fix auth",
        "intent": "Improve reliability",
        "strategy": "single",
        "confidence": 0.9,
        "reasoning": "Simple fix",
        "commit_type": "fix",
        "subject": "improve auth reliability"
    }
    analysis = CommitAnalysis(**data)
    assert analysis.commit_type == "fix"
    assert analysis.confidence == 0.9
    assert analysis.strategy == "single"

def test_invalid_commit_type():
    data = {
        "summary": "Fix auth",
        "intent": "Improve reliability",
        "strategy": "single",
        "confidence": 0.9,
        "reasoning": "Simple fix",
        "commit_type": "invalid_type",
        "subject": "improve auth reliability"
    }
    with pytest.raises(ValidationError):
        CommitAnalysis(**data)

def test_invalid_confidence():
    data = {
        "summary": "Fix auth",
        "intent": "Improve reliability",
        "strategy": "single",
        "confidence": 1.5, # > 1.0
        "reasoning": "Simple fix",
        "commit_type": "fix",
        "subject": "improve auth reliability"
    }
    with pytest.raises(ValidationError):
        CommitAnalysis(**data)
