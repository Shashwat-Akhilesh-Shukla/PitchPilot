from typing import Dict, List, Any
from langchain.llms.base import BaseLLM

from memory.qdrant_memory import QdrantMemoryStore
from prompts.slide_design_prompts import SLIDE_DESIGN_PROMPT_TEMPLATE

class SlideDesignAgent:
    """Agent responsible for designing slides."""
    
    def __init__(self, llm: BaseLLM, memory: QdrantMemoryStore):
        self.llm = llm
        self.memory = memory
    
    def design_slides(
        self, 
        startup_info: Dict[str, str], 
        pitch_content: Dict[str, Any],
        slide_templates: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Design slides based on startup information and pitch content.
        
        Args:
            startup_info: Dictionary containing information about the startup
            pitch_content: Dictionary containing pitch content
            slide_templates: List of slide templates to include
            
        Returns:
            List of dictionaries containing slide content
        """
        slides = []
        
        for slide_template in slide_templates:
            # Create a prompt for slide design
            prompt = SLIDE_DESIGN_PROMPT_TEMPLATE.format(
                startup_name=startup_info["name"],
                slide_type=slide_template,
                relevant_content=self._get_relevant_content(pitch_content, slide_template),
                industry=startup_info["industry"]
            )
            
            # Get slide design from LLM
            design_response = self.llm.generate([prompt])
            design_text = design_response.generations[0][0].text
            
            # Parse the design response into structured data
            slide = self._parse_slide_design(design_text, slide_template)
            slides.append(slide)
            
            # Store slide design in memory
            self.memory.add_to_memory(
                text=design_text,
                metadata={"type": "slide_design", "startup": startup_info["name"], "slide": slide_template}
            )
        
        return slides
    
    def _get_relevant_content(self, pitch_content: Dict[str, Any], slide_type: str) -> str:
        """Get relevant content for a slide type."""
        # Map slide types to content sections
        content_map = {
            "Title Slide": "overview",
            "Problem": "problem",
            "Solution": "solution",
            "Market Size": "market_size",
            "Product": "product",
            "Business Model": "business_model",
            "Traction": "traction",
            "Competition": "competition",
            "Team": "team",
            "Financials": "financials",
            "Ask": "ask"
        }
        
        # Get the relevant content section
        section = content_map.get(slide_type, "overview")
        content = pitch_content.get(section, [])
        
        return "\n".join(content)

    def _parse_slide_design(self, design_text: str, slide_type: str) -> Dict[str, Any]:
        """Parse slide design from text into structured data."""
        lines = design_text.split("\n")
        
        slide = {
            "type": slide_type,
            "title": slide_type,
            "content": [],
            "visual_elements": []
        }
        
        current_section = "content"
        
        for line in lines:
            if line.startswith("Title:"):
                slide["title"] = line[6:].strip()
            elif line.startswith("Visual:"):
                current_section = "visual_elements"
                slide["visual_elements"].append(line[7:].strip())
            elif line.strip():
                if current_section == "content":
                    slide["content"].append(line)
                else:
                    slide["visual_elements"].append(line)
        
        return slide
