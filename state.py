from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    The shared memory structure for our Multi-Agent LangGraph.
    Every node will receive this state and return updates to it.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    
    next_node: str
    last_agent: str 