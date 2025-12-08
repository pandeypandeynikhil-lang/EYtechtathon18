# backend/app/agents/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from ..schemas.analysis import AnalysisRequest, AgentResult


class BaseAgent(ABC):
    """
    Base class for all domain agents.
    Every agent returns an AgentResult.
    """

    def __init__(self, name: str | None = None) -> None:
        self.name = name or self.__class__.__name__

    @abstractmethod
    async def run(self, request: AnalysisRequest) -> AgentResult:
        ...

    def _result(self, summary: str, raw_data: Dict[str, Any] | None = None) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            summary=summary,
            raw_data=raw_data or {},
        )
