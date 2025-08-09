# agents/visual_generation_agent.py
import os
import io
import ast
import time
import traceback
from typing import List, Optional
from langchain.llms.base import BaseLLM
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt

class VisualGenerationAgent:
    """
    Agent that takes visual descriptions, calls an LLM to write safe matplotlib code,
    executes it, and returns generated image file paths.
    """

    def __init__(self, llm: BaseLLM, output_dir: str = "generated_visuals"):
        self.llm = llm
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_visual_from_description(self, description: str, slide_index: int) -> Optional[str]:
        """
        Given a textual description of a visual, generate a matplotlib plot and save it.
        
        Returns path to saved image, or None on failure.
        """
        # Step 1: Ask LLM for matplotlib code
        prompt = (
            f"Write Python matplotlib code to generate a clear, professional business-style chart/illustration "
            f"based on the following description:\n\n"
            f"'{description}'\n\n"
            f"Requirements:\n"
            f"- Must run headlessly (Agg backend)\n"
            f"- No file save in the code, just create the plot\n"
            f"- Use plt.figure() and plt.show() at the end\n"
        )

        try:
            code_response = self.llm.generate([prompt])
            code_text = code_response.generations[0][0].text.strip()

            # Step 2: Extract code block if wrapped in markdown
            if "```" in code_text:
                code_text = "\n".join(line for line in code_text.splitlines() if not line.strip().startswith("```"))

            # Step 3: Validate with AST to avoid unsafe operations
            if not self._is_code_safe(code_text):
                print(f"[VisualGen] Unsafe code detected for slide {slide_index}")
                return None

            # Step 4: Execute the code in a restricted environment
            fig = plt.figure()
            exec_globals = {"plt": plt}
            exec_locals = {}
            exec(code_text, exec_globals, exec_locals)

            # Step 5: Save image
            filename = f"slide_{slide_index}_{int(time.time())}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, bbox_inches='tight')
            plt.close(fig)

            return filepath

        except Exception as e:
            print(f"[VisualGen] Error generating visual: {e}")
            traceback.print_exc()
            return None

    def _is_code_safe(self, code: str) -> bool:
        """
        Naive safety check: disallow imports, file I/O, and OS/system calls.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return False
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("open", "exec", "eval", "__import__", "os", "subprocess"):
                    return False
        return True
