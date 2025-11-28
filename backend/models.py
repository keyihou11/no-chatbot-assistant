"""Data models for the No-Chatbot backend API."""
from typing import List, Optional
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    """Request model for code analysis."""
    file_path: str
    code_content: str
    event_type: str = "save"


class FixSuggestion(BaseModel):
    """Model for a fix suggestion from the LLM."""
    title: str
    description: str
    patch: str
    risks: str


class Issue(BaseModel):
    """Model for a code issue detected by static analysis."""
    line: int
    column: int
    severity: str  # "error", "warning", "info"
    message: str
    rule_id: str
    fix: Optional[FixSuggestion] = None


class AnalyzeResponse(BaseModel):
    """Response model for code analysis."""
    issues: List[Issue]
    analyzed_with: str = "pylint"
