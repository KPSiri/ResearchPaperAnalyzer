"""
Main entry point — run this file to start the analyser.

Usage:
    python main.py

Flow:
1. Loads your GOOGLE_API_KEY from .env
2. Asks for a research topic
3. Invokes the LangGraph with an initial state
4. The graph handles everything: search → present → check → loop/analyse
5. When the graph finishes, we read the final state and display the table
"""

import json

from dotenv import load_dotenv
from tabulate import tabulate

from graph import build_graph


def display_results(final_state: dict) -> None:
    """
    Takes the final graph state and prints a formatted comparison table.
    """
    result = final_state.get("analysis_result", {})
    summary = result.get("summary", "No summary available.")
    papers = result.get("papers", [])

    print("\n" + "=" * 70)
    print("📊  COMPARATIVE ANALYSIS")
    print("=" * 70)

    # Overall summary
    print(f"\n📝 Summary:\n{summary}\n")

    if not papers:
        print("No paper analysis data available.")
        return

    # Build the table rows
    table_rows = []
    for p in papers:
        advantages = p.get("advantages", [])
        disadvantages = p.get("disadvantages", [])

        # Format pros/cons as bullet lists
        pros_str = "\n".join(f"+ {a}" for a in advantages) if advantages else "—"
        cons_str = "\n".join(f"- {d}" for d in disadvantages) if disadvantages else "—"

        table_rows.append([
            p.get("title", "Unknown")[:50],     # truncate long titles
            p.get("key_finding", "—")[:60],
            p.get("tech_stack", "—"),
            pros_str,
            cons_str,
        ])

    # Print the table
    headers = ["Paper", "Key Finding", "Tech Stack", "Advantages", "Disadvantages"]
    print(tabulate(
        table_rows,
        headers=headers,
        tablefmt="grid",
        maxcolwidths=[25, 30, 20, 25, 25],
    ))

    # Also print each paper in detail for readability
    print("\n" + "-" * 70)
    print("📑 DETAILED BREAKDOWN")
    print("-" * 70)

    for i, p in enumerate(papers, 1):
        print(f"\n[{i}] {p.get('title', 'Unknown')}")
        print(f"    Finding:    {p.get('key_finding', '—')}")
        print(f"    Tech Stack: {p.get('tech_stack', '—')}")
        print(f"    Advantages:")
        for a in p.get("advantages", []):
            print(f"      ✓ {a}")
        print(f"    Disadvantages:")
        for d in p.get("disadvantages", []):
            print(f"      ✗ {d}")

    print("\n" + "=" * 70)
    print("✅ Analysis complete!")
    print("=" * 70)


def main():
    # Load environment variables (GOOGLE_API_KEY)
    load_dotenv()

    print("=" * 70)
    print("🔬  RESEARCH PAPER ANALYSER")
    print("    Powered by Gemini + LangGraph")
    print("=" * 70)

    # Get the research topic from the user
    query = input("\nEnter your research topic: ").strip()

    if not query:
        print("No topic entered. Exiting.")
        return

    # Build the graph
    graph = build_graph()

    # Create the initial state — every field must be initialised
    initial_state = {
        "query": query,
        "all_papers": [],
        "selected_papers": [],
        "rejected_titles": [],
        "analysis_result": {},
        "search_round": 0,
        "phase": "search",
    }

    # Run the graph — this blocks until it reaches END
    # The graph handles all the looping internally
    final_state = graph.invoke(initial_state)

    # Display the results
    display_results(final_state)


if __name__ == "__main__":
    main()