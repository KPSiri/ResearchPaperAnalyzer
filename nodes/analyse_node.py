"""
Analyse Node — generates the final comparative analysis.

This is the terminal computation node. After it runs, the graph
reaches END and main.py reads the analysis_result from final state.

It calls the analysis agent with the 5 selected papers and writes
the structured comparison (summary, per-paper findings, tech stacks,
pros/cons) into state.
"""

from state import PaperState
from agents.analysis_agent import analyse_papers


def analyse_node(state: PaperState) -> dict:
    """
    Run the comparative analysis on the 5 selected papers.
    """
    selected = state.get("selected_papers", [])

    print("\n🧠 Analysing all 5 papers — generating comparative table...")
    print("   This may take a moment.\n")

    try:
        result = analyse_papers(selected)
        print("   ✓ Analysis complete!")
    except Exception as e:
        print(f"   ✗ Analysis failed: {e}")
        result = {
            "summary": f"Analysis failed: {e}",
            "papers": [],
        }

    return {
        "analysis_result": result,
        "phase": "done",
    }
