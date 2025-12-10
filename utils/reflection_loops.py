from typing import Dict, Any
import json
from langchain_core.language_models import BaseLanguageModel

class ReflectionSystem:
    """System for reflection loops to improve content."""
    
    def __init__(self, llm: BaseLanguageModel, threshold: float = 0.7):
        self.llm = llm
        self.threshold = threshold
    
    def improve_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        max_iterations = 3
        current_content = content
        
        for _ in range(max_iterations):
            reflections = self._generate_reflections(current_content)
            
            if reflections["quality_score"] >= self.threshold:
                break
            
            current_content = self._apply_improvements(current_content, reflections)
        
        return current_content
    
    def _generate_reflections(self, content: Dict[str, Any]) -> Dict[str, Any]:

        reflection_prompt = f"""
Evaluate the following pitch deck content for quality, clarity, and persuasiveness:

{json.dumps(content, indent=2)}

Give:
Score: <value between 0.0 and 1.0>
And specific suggestions.
"""
        raw = self.llm.invoke(reflection_prompt)
        reflection_text = raw.content if hasattr(raw, "content") else raw
        
        quality_score = 0.7
        for line in reflection_text.split("\n"):
            if "Score:" in line:
                try:
                    quality_score = float(line.split("Score:")[1].strip())
                except:
                    pass
        
        return {
            "quality_score": quality_score,
            "suggestions": reflection_text
        }
    
    def _apply_improvements(self, content: Dict[str, Any], reflections: Dict[str, Any]) -> Dict[str, Any]:

        improvement_prompt = f"""
Improve the following pitch deck content based on these suggestions.

Content:
{json.dumps(content, indent=2)}

Suggestions:
{reflections["suggestions"]}

Return improved content strictly as JSON.
"""
        raw = self.llm.invoke(improvement_prompt)
        improvement_text = raw.content if hasattr(raw, "content") else raw
        
        try:
            start_idx = improvement_text.find("{")
            end_idx = improvement_text.rfind("}") + 1
            json_str = improvement_text[start_idx:end_idx]
            improved_content = json.loads(json_str)
            return improved_content
        except:
            return content
