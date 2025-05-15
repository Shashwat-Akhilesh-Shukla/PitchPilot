from typing import Dict, Any
import json
from langchain.llms.base import BaseLLM

class ReflectionSystem:
    """System for reflection loops to improve content."""
    
    def __init__(self, llm: BaseLLM, threshold: float = 0.7):
        self.llm = llm
        self.threshold = threshold
    
    def improve_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Improve content through reflection loops.
        
        Args:
            content: The content to improve
            
        Returns:
            Improved content
        """
        max_iterations = 3
        current_content = content
        
        for i in range(max_iterations):
            # Generate reflections on the current content
            reflections = self._generate_reflections(current_content)
            
            # Check if we've reached the quality threshold
            if reflections["quality_score"] >= self.threshold:
                break
            
            # Apply improvements based on reflections
            current_content = self._apply_improvements(current_content, reflections)
        
        return current_content
    
    def _generate_reflections(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate reflections on content."""
        # This is a simplified implementation
        # In a real system, this would use the LLM to evaluate the content
        reflection_prompt = f"""
        Please evaluate the following pitch deck content for quality, clarity, and persuasiveness:
        
        {json.dumps(content, indent=2)}
        
        Provide a score from 0.0 to 1.0, where 1.0 is excellent.
        Also provide specific suggestions for improvement.
        """
        
        reflection_response = self.llm.generate([reflection_prompt])
        reflection_text = reflection_response.generations[0][0].text
        
        # Parse the reflection response
        lines = reflection_text.split("\n")
        quality_score = 0.7  # Default value
        
        for line in lines:
            if "Score:" in line:
                try:
                    quality_score = float(line.split("Score:")[1].strip())
                except:
                    pass
        
        return {
            "quality_score": quality_score,
            "suggestions": reflection_text
        }
    
    def _apply_improvements(
        self, 
        content: Dict[str, Any], 
        reflections: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply improvements based on reflections."""
        # This is a simplified implementation
        improvement_prompt = f"""
        Please improve the following pitch deck content based on these suggestions:
        
        Content:
        {json.dumps(content, indent=2)}
        
        Suggestions:
        {reflections["suggestions"]}
        
        Provide the improved content in the same format.
        """
        
        improvement_response = self.llm.generate([improvement_prompt])
        improvement_text = improvement_response.generations[0][0].text
        
        # Try to parse the improved content
        try:
            # Extract JSON from the response
            start_idx = improvement_text.find("{")
            end_idx = improvement_text.rfind("}") + 1
            json_str = improvement_text[start_idx:end_idx]
            
            improved_content = json.loads(json_str)
            return improved_content
        except:
            # If parsing fails, return the original content
            return content
