# backend/app/agents/competition/competition.py
from typing import Any, Dict
from ..base import BaseAgent
from ...schemas.analysis import AnalysisRequest


class CompetitionAgent(BaseAgent):
    """
    Assesses generic competition intensity and price erosion.
    """

    async def run(self, request: AnalysisRequest):
        data: Dict[str, Any] = {
            "number_of_generic_players": 6,
            "price_erosion_score": 0.6,  # higher = more price pressure
            "differentiation_potential_score": 0.7,
            "competition_overall_score": 0.55,  # higher = more favourable competition
        }

        summary = (
            "Competition analysis shows multiple generic players and moderate price erosion, but "
            "there is still room for differentiation via cost, quality or supply reliability."
        )

        return self._result(summary=summary, raw_data=data)
