# backend/app/schemas/analysis.py
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class AnalysisRequest(BaseModel):
    """Input from UI / user to the Master Agent."""
    query: str
    molecule_name: Optional[str] = None
    target_indication: Optional[str] = None


class AgentResult(BaseModel):
    """Standard output for every worker agent."""
    agent_name: str
    summary: str
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class GradingBreakdown(BaseModel):
    """Scores per domain + final overall score (0–1)."""
    market_demand: float
    production_feasibility: float
    demographics: float
    patents_and_trials: float
    competition: float
    overall_score: float


class AnalysisResponse(BaseModel):
    """What the backend returns to the UI."""
    run_id: str
    grading: GradingBreakdown
    results: List[AgentResult]
    report_content: Optional[str] = None
    status: str = "COMPLETED"
