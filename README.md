
<h1 align="center"><strong>PITCHPILOT</strong></h1>


**PitchPilot** is an advanced, fully automated AI system for generating world-class startup pitch decks—complete with tailored research, competitor analysis, content drafting, slide design, and business visuals. Leveraging state-of-the-art LLMs, semantic memory, and multi-agent orchestration, PitchPilot delivers data-driven and visually impactful presentations to supercharge your fundraising journey.



## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Workflow](#workflow)
- [Extensibility](#extensibility)
- [Project Structure](#project-structure)
- [FAQ](#faq)
- [License](#license)
- [Acknowledgments](#acknowledgments)

***

## Features

- **End-to-End Pitch Deck Creation**  
  Goes beyond simple text: from research to slide export, completely automated.

- **Modular AI Agents**  
  Specialized agents for research, competitor analysis, pitch writing, slide design, and visual content generation.

- **Semantic Memory & Contextual Recall**  
  Qdrant vector memory enables cross-slide and historical knowledge recall, keeping outputs focused and consistent.

- **LLM-Driven Reflection Loops**  
  Autonomously reviews and improves content through multi-step LLM feedback cycles.

- **Automated Visuals**  
  Transforms text prompts into matplotlib charts or professional business illustrations, seamlessly embedding them in slides.

- **Professional PowerPoint Export**  
  Exports high-quality `.pptx` files, leveraging smart slide templates and advanced formatting.

***

## Getting Started


```
git clone https://github.com/Shashwat-Akhilesh-Shukla/PitchPilot
```

```
cd pitchpilot
```

```
python -m venv venv
```

```
source venv/bin/activate  # or venv\Scripts\activate (Windows)
```

```
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in your root directory:

```
HF_TOKEN=your_huggingface_api_token
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key  # optional
```

### Templates

Place your `.pptx` slide templates in the `templates/` directory.
At least one generic template is required.

***

## Configuration

All settings (LLM, memory, agent parameters, templates) are managed via `config.py` or via environment variables.
Key parameters:

- LLM model and temperature
- Qdrant collection and dimension
- Default slide sequence
- Reflection and pruning thresholds

***

## Workflow

PitchPilot's workflow is managed via `main.py` and the orchestrator:

1. **Startup Info Input**: Supply structured startup data.
2. **Market Research**: Agent combines LLM insight + semantic memory.
3. **Competitor Analysis**: Market mapping, side-by-side rival scoring.
4. **Pitch Content Drafting**: Bullet-driven, slide-by-slide content, tightly data-bound.
5. **Reflection and Enhancement**: Multi-step improvement via LLM self-critique.
6. **Slide Design**: Agent drafts impactful titles, layouts, and visuals.
7. **Visual Generation**: Business-style images and charts via AI/LLM.
8. **PPTX Export**: Assembles a beautiful, purpose-built deck with tight bulleting—and visuals, in your chosen template.

***

## Extensibility

- **Plug in other LLMs** by extending `custom_llm.py`.
- **Add more slide templates** by modifying `config.py`.
- **Improve memory** by integrating advanced vector/memory models in `qdrant_memory.py`.
- **Customize slide design** or visual types via prompt templates.
- **Integrate more agents** for other business tasks (financial modeling, narrative scoring, etc.).

***

## Project Structure

```
.
├── agents/
│   ├── orchestrator.py
│   ├── research_agent.py
│   ├── competitor_analysis_agent.py
│   ├── pitch_creation_agent.py
│   ├── slide_design_agent.py
│   └── visual_generation_agent.py
├── memory/
│   └── qdrant_memory.py
├── prompts/
│   ├── competitor_analysis_prompts.py
│   ├── pitch_creation_prompts.py
│   ├── research_prompts.py
│   └── slide_design_prompts.py
├── utils/
│   ├── context_prioritization.py
│   ├── reflection_loops.py
│   ├── memory_pruning.py
│   └── presentation_exporter.py
├── config.py
├── custom_llm.py
├── main.py
└── templates/
```

***

## FAQ

**Q: What models do you support?**  
A: PitchPilot works with any Hugging Face compatible LLM (default: Llama-3-70B-Instruct). The architecture allows easy extension to others.

**Q: Is my data stored or logged?**  
A: All pitch and research data is only stored in your Qdrant vector database or as local PPTX files.

**Q: How do visuals work?**  
A: For charts: the agent asks LLM for matplotlib code, validates it, runs it, and saves a PNG. For illustrations: LLM generates a prompt piped to image APIs or Perplexity's image models.

**Q: Can I add my own slides or prompt designs?**  
A: Yes! Prompt templates (in `/prompts/`) and slide lists (`config.py`) are fully customizable.

***

## License

**Proprietary / Internal**  
(Contact authors for licensing and collaboration.)

***

## Acknowledgments

- Powered by [LangChain](https://www.langchain.com/), [Qdrant](https://qdrant.tech/), [Hugging Face](https://huggingface.co/), and the open-source community.
- Special thanks to all contributors and testers.

***

**PitchPilot**: Automate your next pitch. Impress at scale.
