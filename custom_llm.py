# custom_llm.py
import os
from typing import List, Optional, Any
from huggingface_hub import InferenceClient
from langchain_core.language_models import LLM
from langchain_core.outputs import Generation
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import GenerationChunk

class GroqHuggingFaceLLM(LLM):
    model: str
    provider: str = "groq"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 512

    def _call(self, prompt: str, stop=None, run_manager=None) -> str:
        client = InferenceClient(provider=self.provider, api_key=self.api_key or os.environ["HF_TOKEN"])
        completion = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return completion.choices[0].message["content"]

    def generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> Any:
        generations = []
        for prompt in prompts:
            result = self._call(prompt)
            generations.append([Generation(text=result)])
        return type("LLMResult", (object,), {"generations": generations})

    @property
    def _llm_type(self) -> str:
        return "custom_groq_huggingface"
