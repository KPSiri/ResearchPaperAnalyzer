"""
Present Node — displays papers and collects user selections.

This is the ONLY node that interacts with the user.
All other nodes are pure computation / LLM calls.

It shows the latest batch of unseen papers (not previously selected
or rejected) and asks the user to pick which ones to keep.

KEY DESIGN CHOICE:
We only show papers the user hasn't seen yet. If they're on search
round 3, they only see the 5 new papers from round 3 — not all 15.
Already-selected papers are safe in state["selected_papers"].
"""

from state import PaperState


def present_node(state: PaperState) -> dict:
    """
    Show the latest papers and let the user accept or reject each one.
    """
    selected = state.get("selected_papers", [])
    rejected_titles = state.get("rejected_titles", [])
    all_papers = state.get("all_papers", [])

    # Figure out which papers are new (not yet selected or rejected)
    selected_titles = {p["title"] for p in selected}
    new_papers = [
        p for p in all_papers
        if p["title"] not in selected_titles and p["title"] not in rejected_titles
    ]

    if not new_papers:
        print("\n⚠  No new papers to show. Will search again.")
        return {"phase": "check"}

    need = 5 - len(selected)
    print(f"\n📄 Here are the papers found ({len(selected)}/5 selected so far, need {need} more):\n")
    print("=" * 70)

    newly_selected = []
    newly_rejected_titles = []

    for i, paper in enumerate(new_papers, 1):
        print(f"\n--- Paper {i} of {len(new_papers)} ---")
        print(f"📌 Title:      {paper.get('title', 'Unknown')}")
        print(f"👥 Authors:    {paper.get('authors', 'Unknown')}")
        print(f"📅 Year:       {paper.get('year', 'Unknown')}")
        print(f"🏛  Venue:      {paper.get('venue', 'Unknown')}")
        print(f"\n📝 Abstract:   {paper.get('abstract', 'N/A')}")
        print(f"\n🎯 Conclusion: {paper.get('conclusion', 'N/A')}")
        print()

        # Check if we still need more papers
        current_total = len(selected) + len(newly_selected)
        if current_total >= 5:
            print("   (Already have 5 — skipping remaining papers)")
            # Reject the rest
            newly_rejected_titles.append(paper["title"])
            continue

        # Ask the user
        while True:
            choice = input(f"   Include this paper? (y/n): ").strip().lower()
            if choice in ("y", "yes"):
                newly_selected.append(paper)
                print("   ✓ Selected!")
                break
            elif choice in ("n", "no"):
                newly_rejected_titles.append(paper["title"])
                print("   ✗ Skipped.")
                break
            else:
                print("   Please enter 'y' or 'n'")

    # Merge into state
    updated_selected = selected + newly_selected
    updated_rejected = rejected_titles + newly_rejected_titles

    print(f"\n📊 Status: {len(updated_selected)}/5 papers selected")

    return {
        "selected_papers": updated_selected,
        "rejected_titles": updated_rejected,
        "phase": "check",
    }
