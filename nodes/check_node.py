"""
Check Node — the conditional router.

KEY LANGGRAPH CONCEPT: Conditional Edges
This node doesn't update state meaningfully. Instead, the graph
uses a separate routing function that reads the state and returns
a string like "search" or "analyse". That string maps to the next
node via the conditional edge defined in graph.py.

This is the node that creates the LOOP in our graph:
- Not enough papers? → route back to "search"
- Got 5? → route forward to "analyse"
"""

from state import PaperState


def check_node(state: PaperState) -> dict:
    """
    Just updates the phase label. The actual routing decision
    happens in the `route_after_check` function below.
    """
    selected = state.get("selected_papers", [])
    count = len(selected)

    if count >= 5:
        print(f"\n✅ All 5 papers collected! Moving to analysis...")
        return {"phase": "analyse"}
    else:
        print(f"\n🔄 Only {count}/5 papers selected. Searching for more...")
        return {"phase": "search"}


def route_after_check(state: PaperState) -> str:
    """
    Routing function used by the conditional edge.

    LangGraph calls this after check_node runs. The returned string
    must match one of the keys in the conditional edge mapping
    defined in graph.py.

    Returns:
        "search"  — loop back to search_node
        "analyse" — proceed to analyse_node
    """
    selected = state.get("selected_papers", [])

    if len(selected) >= 5:
        return "analyse"
    else:
        return "search"
