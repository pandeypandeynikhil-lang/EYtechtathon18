# backend/app/agents/master.py
import asyncio
import uuid
from typing import List
from .base import BaseAgent
from .grading import GradingAgent
from .report_generator import ReportGeneratorAgent
from ..schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AgentResult,
)
from ..core.config import get_settings


class MasterAgent:
    """
    Orchestrates all domain agents, grading, and report generation.
    """

    def __init__(self, agents: List[BaseAgent]) -> None:
        self.agents = agents
        self.grading_agent = GradingAgent()
        self.report_generator = ReportGeneratorAgent()
        self.settings = get_settings()

    async def _run_agents_parallel(self, request: AnalysisRequest) -> List[AgentResult]:
        coros = [agent.run(request) for agent in self.agents]
        results: List[AgentResult] = await asyncio.gather(*coros)
        return results

    async def run_pipeline(self, request: AnalysisRequest) -> AnalysisResponse:
        # 1. Generate a run ID
        run_id = str(uuid.uuid4())

        # 2. Fan out to all agents (parallel)
        agent_results = await self._run_agents_parallel(request)

        # 3. Compute grading from agent outputs
        grading = self.grading_agent.grade(agent_results)

        # 4. Generate report content (string)
        report_content = self.report_generator.generate_report(
            request=request,
            grading=grading,
            results=agent_results,
        )

        # 5. (Optional) Persist to DB or enqueue for PDF conversion here

        # 6. Return a full response
        return AnalysisResponse(
            run_id=run_id,
            grading=grading,
            results=agent_results,
            report_content=report_content,
            status="COMPLETED",
        )
