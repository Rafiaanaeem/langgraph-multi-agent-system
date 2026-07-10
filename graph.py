from langgraph.graph import StateGraph, START, END
from state import AgentState
from agents.supervisor import supervisor_node

from agents.all_agents import (
    weather_node, 
    summary_node, 
    translation_node, 
    facts_node, 
    movie_node
)

def build_graph():
    """Builds and compiles the Multi-Agent LangGraph."""
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("WEATHER", weather_node)
    workflow.add_node("SUMMARY", summary_node)
    workflow.add_node("TRANSLATION", translation_node)
    workflow.add_node("FACTS", facts_node)
    workflow.add_node("MOVIE", movie_node)
    
    workflow.add_edge(START, "supervisor")
    

    def route_from_supervisor(state: AgentState) -> str:
        """Reads the 'next_node' variable set by the supervisor to determine the path."""
        return state.get("next_node")
        
  
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "WEATHER": "WEATHER",
            "SUMMARY": "SUMMARY",
            "TRANSLATION": "TRANSLATION",
            "FACTS": "FACTS",
            "MOVIE": "MOVIE"
        }
    )
    
    workflow.add_edge("WEATHER", END)
    workflow.add_edge("SUMMARY", END)
    workflow.add_edge("TRANSLATION", END)
    workflow.add_edge("FACTS", END)
    workflow.add_edge("MOVIE", END)
    
    return workflow.compile()

app = build_graph()