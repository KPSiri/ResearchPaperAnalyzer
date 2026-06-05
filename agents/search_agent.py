"""
Search Agent — finds academic papers using Gemini.

This agent is a "thin LLM wrapper". Its responsibilities:
1. Accept a query + list of titles to avoid
2. Format the search prompt with those inputs
3. Call Gemini
4. Parse the JSON response into a list of paper dicts
5. Return the structured result

It does NOT manage state. It does NOT decide what happens next.
That's the graph's job. This separation keeps the agent testable
and reusable — you could call it from anywhere, not just LangGraph.
"""

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from prompts import SEARCH_PROMPT


def create_search_agent() -> ChatGoogleGenerativeAI:
    """
    Creates and returns the Gemini LLM instance for searching.

    We use gemini-2.0-flash because:
    - It's fast (we call this multiple times in the loop)
    - It's cheap
    - It's good enough for structured JSON extraction
    - temperature=0.3 adds slight variety across search rounds
      while keeping output mostly deterministic
    """
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0.3,
    )


def search_papers(query: str, rejected_titles: list[str]) -> list[dict]:
    """
    Search for 5 papers on the given topic, excluding already-seen titles.

    Args:
        query: the research topic from the user
        rejected_titles: paper titles to skip (already shown to user)

    Returns:
        A list of up to 5 paper dicts, each with:
        title, authors, year, venue, abstract, conclusion
    """
    llm = create_search_agent()

    # Format the prompt with the user's query and exclusion list
    rejected_str = "; ".join(rejected_titles) if rejected_titles else "None"
    prompt = SEARCH_PROMPT.format(query=query, rejected_titles=rejected_str)

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

    # Clean up common LLM quirks: sometimes they wrap JSON in ```json blocks
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    # Parse JSON
    papers = json.loads(raw_text)

    # Safety check: ensure it's a list and cap at 5
    if not isinstance(papers, list):
        raise ValueError("Expected a JSON array from LLM, got something else")

    return papers[:5]