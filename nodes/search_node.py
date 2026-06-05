"""
Search Node — calls the search agent and updates state.

KEY LANGGRAPH CONCEPT:
Every node is a function that receives the FULL state dict
and returns a PARTIAL dict — only the fields it wants to update.
LangGraph merges the returned fields into the existing state.

This node:
1. Reads: query, rejected_titles, search_round
2. Calls: search_agent.search_papers()
3. Writes: all_papers (appended), search_round (incremented), phase
"""

from state import PaperState
from agents.search_agent import search_papers


def search_node(state: PaperState) -> dict:
    """
    Fetch 5 new papers and add them to the running list.
    """
    query = state["query"]
    rejected = state.get("rejected_titles", [])
    current_round = state.get("search_round", 0) + 1

    print(f"\n🔍 Search round {current_round} — looking for papers on: '{query}'")
    print("   (Excluding {} previously seen titles)".format(len(rejected)))

    try:
        new_papers = search_papers(query, rejected)
        print(f"   ✓ Found {len(new_papers)} papers")
    except Exception as e:
        print(f"   ✗ Search failed: {e}")
        new_papers = []

    # Append new papers to the running list (don't overwrite previous rounds)
    existing = state.get("all_papers", [])

    return {
        "all_papers": existing + new_papers,
        "search_round": current_round,
        "phase": "present",
    }
