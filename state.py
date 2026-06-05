"""
Shared state schema for the research paper analyser graph.

This TypedDict is the SINGLE object that flows through every node.
Each node receives the full state, does its work, and returns
only the fields it wants to update (partial update pattern).

Fields:
- query: the user's research topic
- all_papers: every paper fetched across all search rounds
- selected_papers: papers the user approved (goal: 5)
- rejected_titles: titles to exclude in future searches
- analysis_result: the final comparison output from the analysis agent
- search_round: tracks how many times we've searched (for the loop)
- phase: current phase label for display purposes
"""

from typing import TypedDict


class PaperState(TypedDict):
    query: str
    all_papers: list[dict]
    selected_papers: list[dict]
    rejected_titles: list[str]
    analysis_result: dict
    search_round: int
    phase: str