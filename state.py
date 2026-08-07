from typing import Annotated, List, TypedDict, Dict, Optional
import operator
from langchain_core.messages import BaseMessage
def manage_list(left: list, right: list):
    if not right:
        return left

    if isinstance(right, list) and right and right[0] == "CLEAR":
        return []

    return left + right

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    files: Optional[List[bytes]]
    plan: List[List[Dict[str, str]]]
    current_stage: int
    context: str
    step_results: Annotated[List[str], manage_list]
    final_outputs: Annotated[List[Dict[str, str]], manage_list]
    last_agent: str


class SubTaskState(TypedDict):
    messages: List[BaseMessage]
    context: str
    query: str
    agent_name: str
    is_final: bool
    last_agent: str