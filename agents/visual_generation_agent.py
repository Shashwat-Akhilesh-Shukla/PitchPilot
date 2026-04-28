# agents/visual_generation_agent.py
import os
import io
import ast
import time
import traceback
from typing import List, Optional
from langchain_core.language_models import LLM
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
from utils.image_fetcher import fetch_web_images

class VisualGenerationAgent:
    """
    Agent that takes visual descriptions, calls an LLM to write safe matplotlib code,
    executes it, and returns generated image file paths.
    """

    def __init__(self, llm: LLM, output_dir: str = "generated_visuals"):
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
            f"- Use 'plt.title()' and other labeling for clarity\n"
            f"- DO NOT use 'plt.show()'\n"
        )

        try:
            code_text = self.llm.invoke(prompt)

            # Step 2: Extract code block if wrapped in markdown
            if "```" in code_text:
                lines = code_text.splitlines()
                # Find start and end of code block
                start = -1
                end = -1
                for i, line in enumerate(lines):
                    if line.strip().startswith("```python"):
                        start = i
                    elif line.strip().startswith("```") and start != -1:
                        end = i
                        break
                
                if start != -1 and end != -1:
                    code_text = "\n".join(lines[start+1:end])
                else:
                    code_text = "\n".join(line for line in code_text.splitlines() if not line.strip().startswith("```"))

            # Step 3: Validate with AST to avoid unsafe operations
            if not self._is_code_safe(code_text):
                print(f"[VisualGen] Unsafe code detected for slide {slide_index}")
                return None

            # Step 4: Execute the code in a restricted environment
            # Reset matplotlib to ensure a clean state
            plt.close('all')
            exec_globals = {"plt": plt}
            exec_locals = {}
            exec(code_text, exec_globals, exec_locals)

            # Step 5: Save image
            # If the code didn't create a figure, or we want to capture whatever was plotted last
            fig = plt.gcf()
            if not fig.get_axes():
                print(f"[VisualGen] No axes found in figure for slide {slide_index}")
                return None
                
            filename = f"slide_{slide_index}_{int(time.time())}.png"
            filepath = os.path.join(self.output_dir, filename)
            fig.savefig(filepath, bbox_inches='tight', dpi=150)
            plt.close('all')

            return filepath

        except Exception as e:
            print(f"[VisualGen] Error generating visual: {e}")
            traceback.print_exc()
            return None

    def fetch_web_image_from_description(self, description: str, slide_index: int) -> Optional[str]:
        """
        Search and download a relevant image from the web based on description.
        """
        print(f"[VisualGen] Searching web for: {description}")
        images = fetch_web_images(description, max_images=1)
        if images:
            return images[0]
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
