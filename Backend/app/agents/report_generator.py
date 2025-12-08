# backend/app/agents/report_generator.py
from typing import List
from ..schemas.analysis import AnalysisRequest, AgentResult, GradingBreakdown


class ReportGeneratorAgent:
    """
    Builds a human-readable report string based on all agents + grading.
    In production this can be converted to PDF by a separate worker.
    """

    def generate_report(
        self,
        request: AnalysisRequest,
        grading: GradingBreakdown,
        results: List[AgentResult],
    ) -> str:
        lines: list[str] = []

        title = f"Generic Opportunity Report for {request.molecule_name or 'Selected Molecule'}"
        lines.append(title)
        lines.append("=" * len(title))
        lines.append("")

        lines.append("1. Executive Summary")
        lines.append(
            f"- Overall feasibility grade: {grading.overall_score * 100:.1f} / 100"
        )
        lines.append(
            f"- Market Demand: {grading.market_demand * 100:.1f} / 100"
        )
        lines.append(
            f"- Production Feasibility: {grading.production_feasibility * 100:.1f} / 100"
        )
        lines.append(
            f"- Demographic Fit: {grading.demographics * 100:.1f} / 100"
        )
        lines.append(
            f"- Patents & Trials: {grading.patents_and_trials * 100:.1f} / 100"
        )
        lines.append(
            f"- Competition Landscape: {grading.competition * 100:.1f} / 100"
        )
        lines.append("")

        lines.append("2. Detailed Agent Insights")
        for idx, r in enumerate(results, start=1):
            lines.append(f"{idx}. {r.agent_name}")
            lines.append("-" * (len(r.agent_name) + 3))
            lines.append(r.summary)
            lines.append("")

        lines.append("3. Conclusion")
        if grading.overall_score >= 0.75:
            conclusion = (
                "The molecule presents a highly attractive opportunity for generic manufacturing, "
                "with strong scores across most dimensions."
            )
        elif grading.overall_score >= 0.55:
            conclusion = (
                "The molecule presents a moderately attractive opportunity. "
                "It can be considered with further due diligence on weaker dimensions."
            )
        else:
            conclusion = (
                "The molecule currently appears to have limited attractiveness for generic manufacturing. "
                "Significant risks or constraints have been identified."
            )
        lines.append(conclusion)

        return "\n".join(lines)
