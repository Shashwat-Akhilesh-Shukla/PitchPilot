# custom_llm.py
import os
import requests
from typing import List, Optional, Any
from langchain_core.language_models import LLM
from langchain_core.outputs import Generation


class PerplexityLLM(LLM):
    model: str = "sonar"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 512

    def _call(self, prompt: str, stop=None, run_manager=None, **kwargs) -> str:
        url = "https://api.perplexity.ai/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key or os.environ['PPLX_API_KEY']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(f"Perplexity API error: {response.text}")

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def generate(self, prompts: List[str], stop=None, callbacks=None, **kwargs) -> Any:
        generations = []
        for prompt in prompts:
            text = self._call(prompt)
            generations.append([Generation(text=text)])
        return type("LLMResult", (object,), {"generations": generations})

    @property
    def _llm_type(self) -> str:
        return "perplexity_llm"
