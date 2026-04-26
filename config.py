import os

class PitchPilotConfig:
    """Configuration for the PitchPilot application."""
    
    def __init__(self):
        # LLM settings
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = "gemini-1.5-flash"
        
        # LangChain settings
        self.temperature = 0.2
        self.max_tokens = 2048
        
        # Pinecone settings
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.collection_name = "pitchpilot-memory"
        self.vector_dimension = 384
        self.pinecone_cloud = "aws"
        self.pinecone_region = "us-east-1"
        
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
