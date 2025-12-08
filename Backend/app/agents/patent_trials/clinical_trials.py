# backend/app/agents/patents_trials/clinical_trials.py
from typing import Any, Dict
from ..base import BaseAgent
from ...schemas.analysis import AnalysisRequest


class ClinicalTrialAgent(BaseAgent):
    """
    Looks at ongoing trials / label expansions (simulated).
    """

    async def run(self, request: AnalysisRequest):
        data: Dict[str, Any] = {
            "ongoing_trials_count": 12,
            "indication_expansion_potential_score": 0.7,
            "safety_signal_risk_score": 0.2,
            "patents_and_trials_score": 0.68,
        }

        summary = (
            "Clinical trial activity is healthy with multiple ongoing studies and limited safety concerns, "
            "supporting sustainable long-term demand for the molecule."
        )

        return self._result(summary=summary, raw_data=data)
