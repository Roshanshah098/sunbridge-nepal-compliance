# graph.py
from langgraph.graph import StateGraph, START, END
from nodes.ingest import ingest_node

from nodes.extract import extract_node
from nodes.reconcile import reconcile_node
from nodes.generate import generate_node
from state import ComplianceState


def build_graph():
    graph = StateGraph(ComplianceState)

    graph.add_node("ingest", ingest_node)
    graph.add_node("extract", extract_node)
    graph.add_node("reconcile", reconcile_node)
    graph.add_node("generate", generate_node)

    graph.add_edge(START, "ingest")
    graph.add_edge("ingest", "extract")
    graph.add_edge("extract", "reconcile")
    graph.add_edge("reconcile", "generate")
    graph.add_edge("generate", END)

    return graph.compile()


if __name__ == "__main__":
    pipeline = build_graph()
    result = pipeline.invoke({})
    print(result["report"])
