import inspect
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from state import AgentState, SubTaskState
from agents.supervisor import supervisor_node
from agents.face_agent import face_node
from agents.all_agents import (
    weather_node, 
    summary_node, 
    translation_node, 
    facts_node, 
    movie_node
)

def with_logging(agent_name: str, node_func):
    """
    Wrapper decorator for worker nodes.
    Handles logging and transparently supports both sync and async agents.
    """
    async def wrapped_node(state: SubTaskState) -> dict:
        print(f"\n\033[1m\033[96m🚀 [AGENT STARTED] [{agent_name}]\033[0m")
        print(f"  Instruction: \"{state.get('query')}\"")
        
    
        if inspect.iscoroutinefunction(node_func):
            result = await node_func(state)
        else:
            result = node_func(state)
            
        
        response_text = ""
        if isinstance(result, dict):
            if "final_outputs" in result and result["final_outputs"]:
                response_text = result["final_outputs"][-1].get("content", "")
            elif "step_results" in result and result["step_results"]:
                response_text = result["step_results"][-1]

        print(f"\033[1m\033[92m✅ [AGENT COMPLETED] [{agent_name}]\033[0m")
        if response_text:
            snippet = response_text.replace('\n', ' ')
            preview = snippet[:150] + "..." if len(snippet) > 150 else snippet
            print(f"  \033[93mReturned Response:\033[0m {preview}")
        print("─" * 50)
        
        return result

    return wrapped_node


def route_stage(state: AgentState):
    """
    Dispatcher Router: Evaluates state['current_stage'] against state['plan'].
    - If stage >= len(plan): Terminates workflow (returns END).
    - Otherwise: Spawns parallel workers for the current stage via Send API.
    """
    plan = state.get("plan", [])
    current_stage = state.get("current_stage", 0)

    if not plan or current_stage >= len(plan):
        print("\033[1m\033[94m🏁 [GRAPH] All pipeline stages complete. Exiting.\033[0m\n")
        return END

    stage_tasks = plan[current_stage]
    is_final_stage = (current_stage == len(plan) - 1)

    print(f"\n\033[1m\033[95m⚡ [STAGE DISPATCHER] Executing Stage {current_stage + 1}/{len(plan)} ({len(stage_tasks)} task(s) | Final Stage: {is_final_stage})\033[0m")

    context_str = state.get("context", "")
    sends = []

    
    for task in stage_tasks:
        agent_name = task["agent"]
        query = task.get("query", "")

        subtask_payload: SubTaskState = {
            "query": query,
            "context": context_str,
            "agent_name": agent_name,
            "is_final": is_final_stage,
            "files": state.get("files") or [],
            "messages": state.get("messages", [])
        }

        print(f"  ➔ [Send API] Dispatching to [{agent_name}]: \"{query}\"")
        sends.append(Send(agent_name, subtask_payload))

    return sends


def merge_node(state: AgentState) -> dict:
    """
    Fan-In Synchronization Node:
    Executes after ALL worker nodes in a stage complete.
    - Merges step_results into a unified context string for downstream stages.
    - Triggers state['step_results'] reset via the 'CLEAR' signal.
    - Increments state['current_stage'].
    """
    print("\n\033[1m\033[93m🔄 [MERGE NODE] Aggregating stage outputs and advancing stage...\033[0m")
    
    step_results = state.get("step_results", [])
    
    valid_results = [r for r in step_results if isinstance(r, str) and r != "CLEAR"]
    
    if valid_results:
        merged_context = "\n\n".join(valid_results)
        print(f"  Combined {len(valid_results)} step result(s) into context for next stage.")
        print(f"\n\033[90m--- MERGED CONTEXT PREVIEW ---\n{merged_context}\n------------------------------\033[0m")
    else:
        merged_context = state.get("context", "")
        print("  No new intermediate step results to merge.")

    current_stage = state.get("current_stage", 0)

    return {
        "context": merged_context,
        "current_stage": current_stage + 1,
        "step_results": ["CLEAR"]  
    }


def build_graph():
    workflow = StateGraph(AgentState)


    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("merge_node", merge_node)
    workflow.add_node("WEATHER", with_logging("WEATHER", weather_node))
    workflow.add_node("SUMMARY", with_logging("SUMMARY", summary_node))
    workflow.add_node("TRANSLATION", with_logging("TRANSLATION", translation_node))
    workflow.add_node("FACTS", with_logging("FACTS", facts_node))
    workflow.add_node("MOVIE", with_logging("MOVIE", movie_node))
    workflow.add_node("FACE", with_logging("FACE", face_node))
    workflow.add_edge(START, "supervisor")

    target_nodes = ["WEATHER", "SUMMARY", "TRANSLATION", "FACTS", "MOVIE", "FACE", END]

   
    workflow.add_conditional_edges("supervisor", route_stage, target_nodes)
    workflow.add_edge("WEATHER", "merge_node")
    workflow.add_edge("SUMMARY", "merge_node")
    workflow.add_edge("TRANSLATION", "merge_node")
    workflow.add_edge("FACTS", "merge_node")
    workflow.add_edge("MOVIE", "merge_node")
    workflow.add_edge("FACE", "merge_node")

    workflow.add_conditional_edges("merge_node", route_stage, target_nodes)

    return workflow.compile()
# compiling the graph
app = build_graph()