import os

class PitchPilotConfig:
    """Configuration for the PitchPilot application."""
    
    def __init__(self):
        # LLM settings
        self.api_key = os.getenv("HF_TOKEN")
        self.model = "meta-llama/Llama-3.3-70B-Instruct"
        
        # LangChain settings
        self.temperature = 0.2
        self.max_tokens = 2048
        
        # Qdrant settings
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = "pitchpilot_memory"
        self.vector_dimension = 384
        
        # Agent settings
        self.max_iterations = 5
        self.reflection_threshold = 0.7
        self.memory_pruning_threshold = 0.5
        
        # Pitch deck settings
        self.default_slides = [
            "Title Slide",
            "Problem",
            "Solution",
            "Market Size",
            "Product",
            "Business Model",
            "Traction",
            "Competition",
            "Team",
            "Financials",
            "Ask"
        ]
