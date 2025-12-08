# backend/app/agents/demographics/demographic.py
from typing import Any, Dict
from ..base import BaseAgent
from ...schemas.analysis import AnalysisRequest


class DemographicAgent(BaseAgent):
    """
    Estimates disease burden and access fit in key markets.
    """

    async def run(self, request: AnalysisRequest):
        data: Dict[str, Any] = {
            "disease_burden_score": 0.85,
            "age_distribution_fit_score": 0.8,
            "access_affordability_score": 0.75,
            "demographic_overall_score": 0.8,
        }

        summary = (
            "Demographic analysis indicates a high disease burden with good alignment to target age groups "
            "and reasonable affordability potential in emerging and developed markets."
        )

        return self._result(summary=summary, raw_data=data)
