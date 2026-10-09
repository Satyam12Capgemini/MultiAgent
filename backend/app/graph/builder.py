from langgraph.graph import StateGraph, END
from app.graph.state import TicketState
from app.graph.nodes.guard import guard_node
from app.graph.nodes.classify import classify_node
from app.graph.nodes.billing import billing_node
from app.graph.nodes.tech import tech_node
from app.graph.nodes.general import general_node
from app.graph.nodes.critic import critic_node
from app.graph.nodes.escalate import escalate_node
from app.graph.nodes.finalize import finalize_node
from app.graph.routing import route_after_classify, route_after_critic

def build_support_graph():
    builder = StateGraph(TicketState)

    # 1. Add Nodes
    builder.add_node("guard", guard_node)
    builder.add_node("classify", classify_node)
    builder.add_node("billing_agent", billing_node)
    builder.add_node("tech_agent", tech_node)
    builder.add_node("general_agent", general_node)
    builder.add_node("critic", critic_node)
    builder.add_node("escalate", escalate_node)
    builder.add_node("finalize", finalize_node)

    # 2. Add Entry Point & Main Edges
    builder.set_entry_point("guard")
    builder.add_edge("guard", "classify")

    # 3. Conditional Routing after Classify
    builder.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "billing": "billing_agent",
            "tech": "tech_agent",
            "general": "general_agent",
            "escalate": "escalate",
        }
    )

    # 4. Connect Specialist Agents to Critic
    builder.add_edge("billing_agent", "critic")
    builder.add_edge("tech_agent", "critic")
    builder.add_edge("general_agent", "critic")

    # 5. Conditional Routing after Critic (Loop control)
    builder.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "retry_billing": "billing_agent",
            "retry_tech": "tech_agent",
            "retry_general": "general_agent",
            "finalize": "finalize",
            "escalate": "escalate",
        }
    )

    # 6. Terminal Edges
    builder.add_edge("finalize", END)
    builder.add_edge("escalate", END)

    return builder.compile()

support_graph = build_support_graph()
