import os
from dotenv import load_dotenv
from langchain.callbacks import StdOutCallbackHandler

from agents.orchestrator import PitchPilotOrchestrator
from config import PitchPilotConfig

# Load environment variables
load_dotenv()

def main():
    """Main entry point for the PitchPilot application."""
    # Initialize configuration
    config = PitchPilotConfig()
    
    # Create callback handler for logging
    callbacks = [StdOutCallbackHandler()]
    
    # Initialize the orchestrator
    orchestrator = PitchPilotOrchestrator(
        config=config,
        callbacks=callbacks
    )
    
    # Run the pitch deck generation process
    startup_info = {
        "name": "Example Startup",
        "industry": "FinTech",
        "problem_statement": "Small businesses struggle with cash flow management.",
        "solution": "AI-powered cash flow prediction and management platform.",
        "target_market": "Small to medium-sized businesses in the US.",
        "business_model": "SaaS subscription, $49/month/user.",
        "traction": "500 beta users, 15% MoM growth.",
        "team": "3 co-founders with fintech and ML backgrounds."
    }
    
    pitch_deck = orchestrator.generate_pitch_deck(startup_info)
    
    # Save or return the generated pitch deck
    print(f"Pitch deck generated successfully: {pitch_deck['title']}")
    
    # Example of accessing specific slides
    print(f"Generated {len(pitch_deck['slides'])} slides")
    
if __name__ == "__main__":
    main()
