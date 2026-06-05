"""
Analysis Agent — produces the comparative analysis of 5 papers.

Same "thin wrapper" pattern as the search agent. This one:
1. Accepts a list of 5 paper dicts
2. Formats the analysis prompt
3. Calls Gemini
4. Parses the JSON response into a structured comparison
5. Returns it

This is called exactly once, after the user has selected 5 papers.
"""

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from prompts import ANALYSIS_PROMPT


def create_analysis_agent() -> ChatGoogleGenerativeAI:
    """
    Creates the Gemini LLM instance for analysis.

    temperature=0.2 keeps it mostly factual while allowing
    some interpretive depth in the summary and advantages/disadvantages.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0.2,
    )


def analyse_papers(papers: list[dict]) -> dict:
    """
    Produce a structured comparative analysis of 5 papers.

    Args:
        papers: list of 5 paper dicts (title, authors, year, etc.)

    Returns:
        A dict with:
        - summary: overall synthesis string
        - papers: list of 5 dicts each with title, key_finding,
                  tech_stack, advantages, disadvantages
    """
    llm = create_analysis_agent()

    # Serialize the papers into the prompt
    papers_json = json.dumps(papers, indent=2)
    prompt = ANALYSIS_PROMPT.format(papers_json=papers_json)

    # Call Gemini
    response = llm.invoke(prompt)
    #raw_text = response.content.strip()

    content = response.content
    if isinstance(content, list):
        raw_text = "".join(
        block if isinstance(block, str) else block.get("text", "")
        for block in content
        )
    else:
        raw_text = content
        raw_text = raw_text.strip()

    # Clean up markdown fencing if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    # Parse JSON
    result = json.loads(raw_text)

    if not isinstance(result, dict):
        raise ValueError("Expected a JSON object from LLM, got something else")

    return result