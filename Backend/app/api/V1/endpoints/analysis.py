# backend/app/api/v1/endpoints/analysis.py
from fastapi import APIRouter, Depends
from ...schemas.analysis import AnalysisRequest, AnalysisResponse
from ...agents.master import MasterAgent
from ...agents.market.iqvia_insights import IQVIAInsightsAgent
from ...agents.market.exim_trends import EXIMTrendAgent
from ...agents.production.process_design import ProcessDesignAgent
from ...agents.production.techno_economic import TechnoEconomicAgent
from ...agents.patents_trials.patent_landscape import PatentLandscapeAgent
from ...agents.patents_trials.clinical_trials import ClinicalTrialAgent
from ...agents.demographics.demographic import DemographicAgent
from ...agents.competition.competition import CompetitionAgent
from ...agents.knowledge.web_intelligence import WebIntelligenceAgent
from ...agents.knowledge.internal_knowledge import InternalKnowledgeAgent


router = APIRouter()


def get_master_agent() -> MasterAgent:
    agents = [
        IQVIAInsightsAgent(),
        EXIMTrendAgent(),
        ProcessDesignAgent(),
        TechnoEconomicAgent(),
        PatentLandscapeAgent(),
        ClinicalTrialAgent(),
        DemographicAgent(),
        CompetitionAgent(),
        WebIntelligenceAgent(),
        InternalKnowledgeAgent(),
    ]
    return MasterAgent(agents=agents)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    payload: AnalysisRequest,
    master_agent: MasterAgent = Depends(get_master_agent),
) -> AnalysisResponse:
    """
    Main entry point: user query → Master Agent → agents → grading → report.
    """
    return await master_agent.run_pipeline(payload)
