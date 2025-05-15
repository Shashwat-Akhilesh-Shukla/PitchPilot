from typing import Dict, List, Any
from langchain.llms.base import BaseLLM

from memory.qdrant_memory import QdrantMemoryStore
from prompts.research_prompts import RESEARCH_PROMPT_TEMPLATE

class ResearchAgent:
    """Agent responsible for conducting research about the startup and its market."""
    
    def __init__(self, llm: BaseLLM, memory: QdrantMemoryStore):
        self.llm = llm
        self.memory = memory
    
    def research_startup(self, startup_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Research the startup and gather relevant information.
        
        Args:
            startup_info: Dictionary containing information about the startup
            
        Returns:
            Dictionary containing research results
        """
        # Create a research prompt based on startup info
        prompt = RESEARCH_PROMPT_TEMPLATE.format(
            startup_name=startup_info["name"],
            industry=startup_info["industry"],
            problem_statement=startup_info["problem_statement"],
            solution=startup_info["solution"]
        )
        
        # Get research results from LLM
        research_response = self.llm.generate([prompt])
        research_text = research_response.generations[0][0].text
        
        # Parse the research response into structured data
        research_results = self._parse_research_results(research_text)
        
        # Store research results in memory
        self.memory.add_to_memory(
            text=research_text,
            metadata={"type": "research", "startup": startup_info["name"]}
        )
        
        return research_results
    
    def _parse_research_results(self, research_text: str) -> Dict[str, Any]:
        """Parse research results from text into structured data."""
        # This is a simplified implementation. In a real system, this would be more sophisticated.
        sections = research_text.split("\n\n")
        
        research_results = {
            "market_trends": sections[0] if len(sections) > 0 else "",
            "market_size": sections[1] if len(sections) > 1 else "",
            "customer_segments": sections[2] if len(sections) > 2 else "",
            "potential_challenges": sections[3] if len(sections) > 3 else ""
        }
        
        return research_results
