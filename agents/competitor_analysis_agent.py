from typing import Dict, List, Any
from langchain.llms.base import BaseLLM

from memory.qdrant_memory import QdrantMemoryStore
from prompts.competitor_analysis_prompts import COMPETITOR_ANALYSIS_PROMPT_TEMPLATE

class CompetitorAnalysisAgent:
    """Agent responsible for analyzing competitors."""
    
    def __init__(self, llm: BaseLLM, memory: QdrantMemoryStore):
        self.llm = llm
        self.memory = memory
    
    def analyze_competitors(
        self, 
        startup_info: Dict[str, str], 
        research_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze competitors based on startup information and research results.
        
        Args:
            startup_info: Dictionary containing information about the startup
            research_results: Dictionary containing research results
            
        Returns:
            Dictionary containing competitor analysis
        """
        # Create a prompt for competitor analysis
        prompt = COMPETITOR_ANALYSIS_PROMPT_TEMPLATE.format(
            startup_name=startup_info["name"],
            industry=startup_info["industry"],
            problem_statement=startup_info["problem_statement"],
            solution=startup_info["solution"],
            market_trends=research_results["market_trends"]
        )
        
        # Get competitor analysis from LLM
        analysis_response = self.llm.generate([prompt])
        analysis_text = analysis_response.generations[0][0].text
        
        # Parse the analysis response into structured data
        competitor_analysis = self._parse_competitor_analysis(analysis_text)
        
        # Store competitor analysis in memory
        self.memory.add_to_memory(
            text=analysis_text,
            metadata={"type": "competitor_analysis", "startup": startup_info["name"]}
        )
        
        return competitor_analysis
    
    def _parse_competitor_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse competitor analysis from text into structured data."""
        # This is a simplified implementation
        sections = analysis_text.split("\n\n")
        
        competitors = []
        competitive_advantages = []
        
        for section in sections:
            if "Competitor:" in section:
                competitors.append(section)
            elif "Advantage:" in section:
                competitive_advantages.append(section)
        
        return {
            "competitors": competitors,
            "competitive_advantages": competitive_advantages
        }
