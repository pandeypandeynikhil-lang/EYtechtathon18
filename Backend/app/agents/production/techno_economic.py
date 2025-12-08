# backend/app/agents/production/techno_economic.py
from typing import Any, Dict
from ..base import BaseAgent
from ...schemas.analysis import AnalysisRequest


class TechnoEconomicAgent(BaseAgent):
    """
    Performs a simple techno-economic assessment (placeholder logic).
    """

    async def run(self, request: AnalysisRequest):
        data: Dict[str, Any] = {
            "capex_million_usd": 25.0,
            "opex_million_usd_per_year": 6.0,
            "payback_period_years": 4.5,
            "internal_rate_of_return": 0.23,  # 23%
            "production_feasibility_score": 0.81,
        }

        summary = (
            "Techno-economic analysis suggests acceptable CAPEX and OPEX with a payback period of "
            f"{data['payback_period_years']} years and an IRR of {int(data['internal_rate_of_return'] * 100)}%, "
            "indicating strong economic feasibility for plant investment."
        )

        return self._result(summary=summary, raw_data=data)
