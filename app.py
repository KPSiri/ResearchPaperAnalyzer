"""
Streamlit UI for the Research Paper Analyser.

Why not use the LangGraph here?
-------------------------------
LangGraph's present_node uses input() which blocks — that doesn't
work in Streamlit because Streamlit reruns the ENTIRE script on
every button click / checkbox toggle. So instead we:
1. Reuse the same agents (search_agent, analysis_agent)
2. Reuse the same prompts (prompts.py)
3. Replace the graph's state management with st.session_state
4. Replace the graph's conditional loop with Streamlit's rerun cycle

The agents don't care who calls them — that's the benefit of
keeping them as thin wrappers with no state.

Run with:
    streamlit run app.py
"""

import json
import streamlit as st
from dotenv import load_dotenv

from agents.search_agent import search_papers
from agents.analysis_agent import analyse_papers

load_dotenv()

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(page_title="Research Paper Analyser", page_icon="🔬", layout="wide")
st.title("🔬 Research Paper Analyser")
st.caption("Search → Select 5 papers → Get a comparative analysis")

# ── Initialise session state ─────────────────────────────────────
if "phase" not in st.session_state:
    st.session_state.phase = "search"
    st.session_state.query = ""
    st.session_state.all_papers = []
    st.session_state.latest_batch = []
    st.session_state.selected_titles = set()
    st.session_state.rejected_titles = []
    st.session_state.search_round = 0
    st.session_state.analysis_result = None
    st.session_state.error = None


def reset():
    """Clear everything and go back to search."""
    for key in ["all_papers", "rejected_titles"]:
        st.session_state[key] = []
    st.session_state.latest_batch = []
    st.session_state.selected_titles = set()
    st.session_state.search_round = 0
    st.session_state.analysis_result = None
    st.session_state.error = None
    st.session_state.phase = "search"


def do_search():
    """Call the search agent and move to the select phase."""
    query = st.session_state.query_input.strip()
    if not query:
        st.session_state.error = "Please enter a research topic."
        return

    st.session_state.query = query
    st.session_state.error = None
    st.session_state.search_round += 1

    try:
        new_papers = search_papers(query, st.session_state.rejected_titles)
        st.session_state.all_papers.extend(new_papers)
        st.session_state.latest_batch = new_papers
        st.session_state.phase = "select"
    except Exception as e:
        st.session_state.error = f"Search failed: {e}"


def fetch_more():
    """Search again for more papers, excluding already-seen ones."""
    all_titles = [p["title"] for p in st.session_state.all_papers]
    selected = st.session_state.selected_titles
    newly_rejected = [
        t for t in all_titles
        if t not in selected and t not in st.session_state.rejected_titles
    ]
    st.session_state.rejected_titles.extend(newly_rejected)
    st.session_state.search_round += 1

    try:
        new_papers = search_papers(st.session_state.query, st.session_state.rejected_titles)
        st.session_state.all_papers.extend(new_papers)
        st.session_state.latest_batch = new_papers
    except Exception as e:
        st.session_state.error = f"Search failed: {e}"


def do_analyse():
    """Call the analysis agent on the selected papers."""
    selected = [
        p for p in st.session_state.all_papers
        if p["title"] in st.session_state.selected_titles
    ]
    st.session_state.phase = "analyse"
    try:
        result = analyse_papers(selected)
        st.session_state.analysis_result = result
        st.session_state.phase = "results"
    except Exception as e:
        st.session_state.error = f"Analysis failed: {e}"
        st.session_state.phase = "select"


# ── SEARCH PHASE ─────────────────────────────────────────────────
if st.session_state.phase == "search":
    st.text_input(
        "Enter your research topic",
        placeholder="e.g. Transformer attention mechanisms, federated learning privacy…",
        key="query_input",
    )
    st.button("🔍 Search for papers", on_click=do_search)

    if st.session_state.error:
        st.error(st.session_state.error)


# ── SELECT PHASE ─────────────────────────────────────────────────
elif st.session_state.phase == "select":
    selected_count = len(st.session_state.selected_titles)
    st.info(f"**{selected_count} / 5** papers selected  •  Search round {st.session_state.search_round}")

    if st.session_state.error:
        st.error(st.session_state.error)

    # Show already-selected papers first
    if st.session_state.selected_titles:
        st.subheader("✅ Your selections")
        for i, paper in enumerate(st.session_state.all_papers):
            title = paper.get("title", "Untitled")
            if title not in st.session_state.selected_titles:
                continue
            col1, col2 = st.columns([0.05, 0.95])
            with col1:
                checked = st.checkbox(
                    "sel", value=True, key=f"sel_{i}", label_visibility="collapsed"
                )
            if not checked:
                st.session_state.selected_titles.discard(title)
            with col2:
                with st.expander(f"**{title}**  ({paper.get('year', '?')} • {paper.get('venue', '?')})"):
                    st.markdown(f"**Authors:** {paper.get('authors', 'Unknown')}")
                    st.markdown(f"**Abstract:** {paper.get('abstract', 'N/A')}")
                    st.markdown(f"**Conclusion:** {paper.get('conclusion', 'N/A')}")

    # Show only the latest batch of new papers
    new_papers = [
        p for p in st.session_state.latest_batch
        if p.get("title", "") not in st.session_state.selected_titles
    ]

    if new_papers:
        st.subheader("📄 New papers — select the ones you want")
        for i, paper in enumerate(new_papers):
            title = paper.get("title", "Untitled")
            col1, col2 = st.columns([0.05, 0.95])
            with col1:
                checked = st.checkbox(
                    "sel",
                    value=False,
                    key=f"new_{st.session_state.search_round}_{i}",
                    label_visibility="collapsed",
                )
            if checked and title not in st.session_state.selected_titles:
                if len(st.session_state.selected_titles) < 5:
                    st.session_state.selected_titles.add(title)
                else:
                    st.warning("Already have 5 selected — deselect one first.")
            with col2:
                with st.expander(f"**{title}**  ({paper.get('year', '?')} • {paper.get('venue', '?')})"):
                    st.markdown(f"**Authors:** {paper.get('authors', 'Unknown')}")
                    st.markdown(f"**Abstract:** {paper.get('abstract', 'N/A')}")
                    st.markdown(f"**Conclusion:** {paper.get('conclusion', 'N/A')}")

    st.divider()
    selected_count = len(st.session_state.selected_titles)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if selected_count >= 5:
            st.button("🧠 Analyse these 5 papers", on_click=do_analyse, type="primary")
        else:
            st.button("🧠 Analyse", disabled=True)
    with col_b:
        st.button("🔄 Fetch more papers", on_click=fetch_more)
    with col_c:
        st.button("🗑️ Start over", on_click=reset)


# ── ANALYSE PHASE (loading) ──────────────────────────────────────
elif st.session_state.phase == "analyse":
    st.info("Generating comparative analysis… this may take a moment.")
    do_analyse()
    st.rerun()


# ── RESULTS PHASE ────────────────────────────────────────────────
elif st.session_state.phase == "results":
    result = st.session_state.analysis_result

    if not result:
        st.error("No analysis result available.")
    else:
        st.subheader("📊 Comparative Analysis")
        st.write(result.get("summary", ""))

        papers_data = result.get("papers", [])

        if papers_data:
            table_rows = []
            for p in papers_data:
                pros = p.get("advantages", [])
                cons = p.get("disadvantages", [])
                table_rows.append({
                    "Paper": p.get("title", "—"),
                    "Key Finding": p.get("key_finding", "—"),
                    "Tech Stack": p.get("tech_stack", "—"),
                    "Advantages": " • ".join(pros) if pros else "—",
                    "Disadvantages": " • ".join(cons) if cons else "—",
                })

            st.dataframe(table_rows, use_container_width=True)

            st.divider()
            st.subheader("📑 Detailed Breakdown")

            for i, p in enumerate(papers_data, 1):
                with st.expander(f"**{i}. {p.get('title', 'Unknown')}**"):
                    st.markdown(f"**Key Finding:** {p.get('key_finding', '—')}")
                    st.markdown(f"**Tech Stack:** {p.get('tech_stack', '—')}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Advantages**")
                        for a in p.get("advantages", []):
                            st.markdown(f"✅ {a}")
                    with col2:
                        st.markdown("**Disadvantages**")
                        for d in p.get("disadvantages", []):
                            st.markdown(f"❌ {d}")

    st.divider()
    st.button("🔬 New Search", on_click=reset)