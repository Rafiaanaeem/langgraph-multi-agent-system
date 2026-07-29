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
# 1. IMPORT THE NEW FACE AGENT NODE
from agents.face_agent import face_recognition_node

def route_next_agent(state: AgentState) -> str:
    queue = state.get("agent_queue", [])
    if len(queue) > 0:
        return queue[0]  
    return END  

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("WEATHER", weather_node)
    workflow.add_node("SUMMARY", summary_node)
    workflow.add_node("TRANSLATION", translation_node)
    workflow.add_node("FACTS", facts_node)
    workflow.add_node("MOVIE", movie_node)
    
    # 2. ADD THE FACE NODE
    workflow.add_node("FACE", face_recognition_node)
    
    workflow.add_edge(START, "supervisor")
    
    routing_map = {
        "WEATHER": "WEATHER",
        "SUMMARY": "SUMMARY",
        "TRANSLATION": "TRANSLATION",
        "FACTS": "FACTS",
        "MOVIE": "MOVIE",
        "FACE": "FACE",   # 3. ADD FACE TO ROUTING MAP
        END: END
    }

    workflow.add_conditional_edges("supervisor", route_next_agent, routing_map)
    workflow.add_conditional_edges("WEATHER", route_next_agent, routing_map)
    workflow.add_conditional_edges("SUMMARY", route_next_agent, routing_map)
    workflow.add_conditional_edges("TRANSLATION", route_next_agent, routing_map)
    workflow.add_conditional_edges("FACTS", route_next_agent, routing_map)
    workflow.add_conditional_edges("MOVIE", route_next_agent, routing_map)
    
    # 4. ADD CONDITIONAL EDGE FOR FACE
    workflow.add_conditional_edges("FACE", route_next_agent, routing_map)
    
    return workflow.compile()

app = build_graph()