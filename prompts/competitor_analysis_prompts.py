COMPETITOR_ANALYSIS_PROMPT_TEMPLATE = """
You are a specialized competitor analysis agent tasked with analyzing the competitive landscape.

Startup Information:
- Name: {startup_name}
- Industry: {industry}
- Problem Statement: {problem_statement}
- Solution: {solution}

Market Trends:
{market_trends}

Please analyze the competitive landscape for this startup. For each identified competitor:
1. Provide a brief overview of their business
2. Analyze their strengths and weaknesses
3. Compare their solution to the startup's solution
4. Identify opportunities for differentiation

Also, identify key competitive advantages that the startup can leverage.
"""
