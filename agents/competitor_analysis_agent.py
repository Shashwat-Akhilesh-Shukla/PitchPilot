from typing import Dict, List, Any
from langchain_core.language_models import BaseChatModel

from memory.memory import PineconeMemoryStore
from prompts.competitor_analysis_prompts import COMPETITOR_ANALYSIS_PROMPT_TEMPLATE

class CompetitorAnalysisAgent:
    """Agent responsible for analyzing competitors."""
    
    def __init__(self, llm: BaseChatModel, memory: PineconeMemoryStore):
        self.llm = llm
        self.memory = memory
    
    def analyze_competitors(
        self, 
        startup_info: Dict[str, str], 
        research_results: Dict[str, Any]
    ) -> Dict[str, Any]:

        prompt = COMPETITOR_ANALYSIS_PROMPT_TEMPLATE.format(
            startup_name=startup_info["name"],
            industry=startup_info["industry"],
            problem_statement=startup_info["problem_statement"],
            solution=startup_info["solution"],
            market_trends=research_results["market_trends"]
        )
        
        # Modern LangChain call
        analysis_text = self.llm.invoke(prompt)
        
        # If your model returns ChatMessage objects, extract the content
        if hasattr(analysis_text, "content"):
            analysis_text = analysis_text.content
        
        competitor_analysis = self._parse_competitor_analysis(analysis_text)
        
        self.memory.add_to_memory(
            text=analysis_text,
            metadata={"type": "competitor_analysis", "startup": startup_info["name"]}
        )
        
        return competitor_analysis
    
    def _parse_competitor_analysis(self, analysis_text: str) -> Dict[str, Any]:
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
