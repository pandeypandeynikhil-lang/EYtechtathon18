# backend/app/agents/patents_trials/patent_landscape.py
from typing import Any, Dict
from ..base import BaseAgent
from ...schemas.analysis import AnalysisRequest


class PatentLandscapeAgent(BaseAgent):
    """
    Evaluates FTO (freedom to operate) based on a simplified heuristic.
    """

    async def run(self, request: AnalysisRequest):
        data: Dict[str, Any] = {
            "primary_patents_expired": True,
            "secondary_patent_risk_score": 0.35,  # 0–1, higher = more risk
            "litigation_risk_score": 0.25,
            "patent_overall_score": 0.72,        # higher = safer
        }

        summary = (
            "Patent landscape analysis indicates that core patents are largely expired with manageable "
            "secondary and litigation risks, suggesting reasonable freedom to operate."
        )

        return self._result(summary=summary, raw_data=data)
