# custom_llm.py
import os
import requests
from typing import List, Optional, Any
from langchain_core.language_models import LLM
from langchain_core.outputs import Generation


class GeminiLLM(LLM):
    model: str = "gemini-1.5-flash"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048

    def _call(self, prompt: str, stop=None, run_manager=None, **kwargs) -> str:
        api_key = self.api_key or os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY environment variable.")
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={api_key}"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens,
            }
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(f"Gemini API error ({response.status_code}): {response.text}")

        data = response.json()
        
        try:
            # Extract the text from the response
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected response format from Gemini API: {data}") from e

    def generate(self, prompts: List[str], stop=None, callbacks=None, **kwargs) -> Any:
        generations = []
        for prompt in prompts:
            text = self._call(prompt)
            generations.append([Generation(text=text)])
        
        # Mocking LLMResult structure as expected by LangChain core in some versions
        class LLMResult:
            def __init__(self, generations):
                self.generations = generations
        
        return LLMResult(generations)

    @property
    def _llm_type(self) -> str:
        return "gemini_llm"
