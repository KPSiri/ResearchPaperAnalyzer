"""
Graph Definition — wires nodes into a LangGraph StateGraph.

This is the "blueprint" of the entire system. It defines:
1. What nodes exist
2. How they connect (edges)
3. Where the conditional branch is (the loop)
4. Where the graph starts and ends

VISUAL REPRESENTATION:

    ┌──────────┐
    │  search   │ ◄─── Entry point
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │  present  │      (user selects papers)
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │   check   │──── "analyse" ──→ ┌──────────┐
    └────┬─────┘                    │  analyse  │
         │                          └────┬─────┘
    "search"                              │
         │                               ▼
         └── (loops back             ┌───────┐
              to search)             │  END  │
                                     └───────┘

KEY LANGGRAPH CONCEPTS USED:
- StateGraph: a graph where nodes share a typed state dict
- add_node: registers a function as a named node
- add_edge: fixed transition from one node to the next
- add_conditional_edges: branching based on a routing function
- set_entry_point: which node runs first
- END: special sentinel that terminates the graph
"""

from langgraph.graph import StateGraph, END

from state import PaperState
from nodes.search_node import search_node
from nodes.present_node import present_node
from nodes.check_node import check_node, route_after_check
from nodes.analyse_node import analyse_node


def build_graph():
    """
    Construct and compile the paper analyser graph.

    Returns a compiled graph that you can invoke with an initial state.
    """

    # 1. Create the graph with our state schema
    graph = StateGraph(PaperState)

    # 2. Add all nodes
    #    Each string name is how we reference the node in edges
    graph.add_node("search", search_node)
    graph.add_node("present", present_node)
    graph.add_node("check", check_node)
    graph.add_node("analyse", analyse_node)

    # 3. Set the entry point — where the graph starts
    graph.set_entry_point("search")

    # 4. Add fixed edges (A always goes to B)
    graph.add_edge("search", "present")   # after search, always present
    graph.add_edge("present", "check")    # after present, always check
    graph.add_edge("analyse", END)        # after analyse, we're done

    # 5. Add the conditional edge — this creates the loop
    #    route_after_check() returns either "search" or "analyse"
    #    and the mapping dict says which node each string leads to
    graph.add_conditional_edges(
        "check",                    # source node
        route_after_check,          # routing function
        {                           # mapping: return value → target node
            "search": "search",
            "analyse": "analyse",
        },
    )

    # 6. Compile — turns the blueprint into a runnable object
    compiled = graph.compile()

    return compiled
