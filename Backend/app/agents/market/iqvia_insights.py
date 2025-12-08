# backend/app/agents/market/iqvia_insights.py
from typing import Any, Dict
from ..base import BaseAgent
from ...schemas.analysis import AnalysisRequest


class IQVIAInsightsAgent(BaseAgent):
    """
    Simulated agent for IQVIA-like market insights.
    In a real system this would call external APIs.
    """

    async def run(self, request: AnalysisRequest):
        molecule = request.molecule_name or "the molecule"
        indication = request.target_indication or "the indication"

        data: Dict[str, Any] = {
            "estimated_market_size_billion_usd": 1.8,
            "cagr": 0.09,
            "key_regions": ["US", "EU5", "India"],
            # 0–1 score reflecting demand strength (hard-coded heuristic)
            "market_demand_score": 0.82,
        }

        summary = (
            f"For {molecule} in {indication}, the estimated global market size is "
            f"~${data['estimated_market_size_billion_usd']}B with ~{int(data['cagr'] * 100)}% CAGR. "
            f"Strong demand is observed in {', '.join(data['key_regions'])}."
        )

        return self._result(summary=summary, raw_data=data)
