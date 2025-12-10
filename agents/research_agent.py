from typing import Dict, Any
from langchain_core.language_models import BaseLanguageModel

from memory.memory import PineconeMemoryStore
from prompts.research_prompts import RESEARCH_PROMPT_TEMPLATE

class ResearchAgent:
    """Agent responsible for conducting research about the startup and its market."""
    
    def __init__(self, llm: BaseLanguageModel, memory: PineconeMemoryStore):
        self.llm = llm
        self.memory = memory
    
    def research_startup(self, startup_info: Dict[str, str]) -> Dict[str, Any]:

        prompt = RESEARCH_PROMPT_TEMPLATE.format(
            startup_name=startup_info["name"],
            industry=startup_info["industry"],
            problem_statement=startup_info["problem_statement"],
            solution=startup_info["solution"]
        )
        
        # Modern LLM call
        output = self.llm.invoke(prompt)

        research_text = output.content if hasattr(output, "content") else output
        
        research_results = self._parse_research_results(research_text)
        
        self.memory.add_to_memory(
            text=research_text,
            metadata={"type": "research", "startup": startup_info["name"]}
        )
        
        return research_results
    
    def _parse_research_results(self, research_text: str) -> Dict[str, Any]:

        sections = research_text.split("\n\n")
        
        return {
            "market_trends": sections[0] if len(sections) > 0 else "",
            "market_size": sections[1] if len(sections) > 1 else "",
            "customer_segments": sections[2] if len(sections) > 2 else "",
            "potential_challenges": sections[3] if len(sections) > 3 else ""
        }
