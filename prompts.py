"""
All prompt templates for the research paper analyser.

Keeping prompts separate from logic means you can:
1. Tweak wording without touching any Python logic
2. A/B test different prompts easily
3. See all your "instructions to the LLM" in one file

Both prompts ask for JSON output. We enforce structure by being
very explicit about the schema we expect.
"""

SEARCH_PROMPT = """You are a research assistant specializing in academic literature.

Given the research topic below, return exactly 5 real, peer-reviewed academic papers
that are highly relevant. Use your knowledge to find genuine papers with real authors
and publication venues.

TOPIC: {query}

IMPORTANT RULES:
- Return ONLY a valid JSON array, no markdown, no commentary, no backticks
- Each paper must be a real, published paper — do not fabricate titles or authors
- Avoid these already-seen papers: {rejected_titles}

Each object in the array must have these exact fields:
- "title": full paper title (string)
- "authors": comma-separated author names (string)
- "year": publication year (integer)
- "venue": journal or conference name (string)
- "abstract": 2-3 sentence summary of the paper's objective and approach (string)
- "conclusion": 1-2 sentence summary of the paper's key finding or result (string)

Return ONLY the JSON array. Nothing else."""


ANALYSIS_PROMPT = """You are an expert research analyst performing a comparative study.

Given these 5 academic papers as JSON, produce a structured comparative analysis.

PAPERS:
{papers_json}

Return ONLY a valid JSON object (no markdown, no backticks) with these exact fields:

- "summary": a 3-4 sentence synthesis that captures the overall landscape these papers
  cover, common themes, and where they diverge (string)
- "papers": an array of exactly 5 objects, each with:
    - "title": the paper's title (string)
    - "key_finding": one sentence describing the main result (string)
    - "tech_stack": comma-separated list of methods, tools, frameworks, or
      algorithms used (string)
    - "advantages": array of 2-3 strings listing strengths of this paper's approach
    - "disadvantages": array of 2-3 strings listing weaknesses or limitations

Return ONLY the JSON object. Nothing else."""
