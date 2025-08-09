PITCH_CREATION_PROMPT_TEMPLATE = """
You are a specialized pitch creation agent tasked with crafting compelling pitch deck content.

Startup Information:
- Name: {startup_name}
- Industry: {industry}
- Problem Statement: {problem_statement}
- Solution: {solution}
- Target Market: {target_market}
- Business Model: {business_model}
- Traction: {traction}
- Team: {team}

Research Findings:
- Market Trends: {market_trends}
- Market Size: {market_size}
- Customer Segments: {customer_segments}
- Potential Challenges: {potential_challenges}

Competitor Analysis:
- Competitors: {competitors}
- Competitive Advantages: {competitive_advantages}

Additional Context:
{context}

Create compelling pitch deck content that tells a cohesive story about the startup.
Organize your content into the following sections:
1. Overview
2. Problem
3. Solution
4. Market Size
5. Product
6. Business Model
7. Traction
8. Competition
9. Team
10. Financials
11. Ask

Each section should be concise, impactful, and data-driven where possible.
Each section must consist of exactly 3 bullet points, each under 10 words.
No paragraphs. No filler. Only data-driven bullets.
"""
