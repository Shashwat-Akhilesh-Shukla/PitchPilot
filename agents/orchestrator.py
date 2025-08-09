from typing import Dict, List, Any
import json
from langchain.callbacks.base import BaseCallbackHandler
from custom_llm import GroqHuggingFaceLLM
from agents.research_agent import ResearchAgent
from agents.pitch_creation_agent import PitchCreationAgent
from agents.competitor_analysis_agent import CompetitorAnalysisAgent
from agents.slide_design_agent import SlideDesignAgent
from memory.qdrant_memory import QdrantMemoryStore
from utils.reflection_loops import ReflectionSystem
from utils.memory_pruning import prune_memory
from config import PitchPilotConfig

class PitchPilotOrchestrator:
    """Orchestrator that manages the entire pitch deck generation process."""
    
    def __init__(self, config: PitchPilotConfig, callbacks: List[BaseCallbackHandler] = None):
        self.config = config
        self.callbacks = callbacks or []
        
        # Initialize the LLM
        self.llm = GroqHuggingFaceLLM(
            model=config.model,
            provider="groq",
            api_key=config.api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

        # Initialize memory
        self.memory = QdrantMemoryStore(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
            collection_name=config.collection_name,
            vector_dimension=config.vector_dimension
        )
        
        # Initialize agents
        self.research_agent = ResearchAgent(self.llm, self.memory)
        self.pitch_creation_agent = PitchCreationAgent(self.llm, self.memory)
        self.competitor_analysis_agent = CompetitorAnalysisAgent(self.llm, self.memory)
        self.slide_design_agent = SlideDesignAgent(self.llm, self.memory)
        
        # Initialize reflection system
        self.reflection_system = ReflectionSystem(
            llm=self.llm,
            threshold=config.reflection_threshold
        )
    
    def generate_pitch_deck(self, startup_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate a complete pitch deck based on startup information.
        
        Args:
            startup_info: Dictionary containing information about the startup
            
        Returns:
            Dictionary containing the generated pitch deck
        """
        # Step 1: Research phase
        research_results = self.research_agent.research_startup(startup_info)
        
        # Step 2: Competitor analysis
        competitor_analysis = self.competitor_analysis_agent.analyze_competitors(
            startup_info, 
            research_results
        )
        
        # Step 3: Create pitch content
        pitch_content = self.pitch_creation_agent.create_pitch_content(
            startup_info,
            research_results,
            competitor_analysis
        )
        
        # Apply reflection loop to improve content
        pitch_content = self.reflection_system.improve_content(pitch_content)
        
        # Step 4: Design slides
        slides = self.slide_design_agent.design_slides(
            startup_info,
            pitch_content,
            self.config.default_slides
        )
        
        # Compile the final pitch deck
        pitch_deck = {
            "title": f"{startup_info['name']} Pitch Deck",
            "startup_info": startup_info,
            "slides": slides
        }
        
        return pitch_deck
