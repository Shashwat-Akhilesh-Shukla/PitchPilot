from typing import Dict, List, Any
from langchain.llms.base import BaseLLM

from memory.qdrant_memory import QdrantMemoryStore
from prompts.pitch_creation_prompts import PITCH_CREATION_PROMPT_TEMPLATE
from utils.context_prioritization import prioritize_context

class PitchCreationAgent:
    """Agent responsible for creating the pitch content."""
    
    def __init__(self, llm: BaseLLM, memory: QdrantMemoryStore):
        self.llm = llm
        self.memory = memory
    
    def create_pitch_content(
        self, 
        startup_info: Dict[str, str], 
        research_results: Dict[str, Any],
        competitor_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create pitch content based on startup information, research results, and competitor analysis.
        
        Args:
            startup_info: Dictionary containing information about the startup
            research_results: Dictionary containing research results
            competitor_analysis: Dictionary containing competitor analysis
            
        Returns:
            Dictionary containing pitch content for each slide
        """
        # Retrieve relevant context from memory
        context_items = self.memory.retrieve_relevant(
            query=f"{startup_info['name']} {startup_info['industry']} pitch deck",
            limit=10
        )
        
        # Prioritize context items
        prioritized_context = prioritize_context(context_items, startup_info)
        
        # Create a prompt with prioritized context
        prompt = PITCH_CREATION_PROMPT_TEMPLATE.format(
            startup_name=startup_info["name"],
            industry=startup_info["industry"],
            problem_statement=startup_info["problem_statement"],
            solution=startup_info["solution"],
            target_market=startup_info["target_market"],
            business_model=startup_info["business_model"],
            traction=startup_info["traction"],
            team=startup_info["team"],
            market_trends=research_results["market_trends"],
            market_size=research_results["market_size"],
            customer_segments=research_results["customer_segments"],
            potential_challenges=research_results["potential_challenges"],
            competitors=competitor_analysis["competitors"],
            competitive_advantages=competitor_analysis["competitive_advantages"],
            context="\n".join(prioritized_context)
        )
        
        # Generate pitch content
        pitch_response = self.llm.generate([prompt])
        pitch_text = pitch_response.generations[0][0].text
        
        # Parse pitch content into structured data
        pitch_content = self._parse_pitch_content(pitch_text)
        
        # Store pitch content in memory
        self.memory.add_to_memory(
            text=pitch_text,
            metadata={"type": "pitch_content", "startup": startup_info["name"]}
        )
        
        return pitch_content
    
    def _parse_pitch_content(self, pitch_text: str) -> Dict[str, Any]:
        """Parse pitch content from text into structured data."""
        # This is a simplified implementation
        lines = pitch_text.split("\n")
        current_section = "overview"
        pitch_content = {"overview": []}
        
        for line in lines:
            if line.startswith("# "):
                current_section = line[2:].lower().replace(" ", "_")
                pitch_content[current_section] = []
            else:
                if line.strip():
                    pitch_content[current_section].append(line)
        
        return pitch_content
