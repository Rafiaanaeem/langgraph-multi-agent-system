import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

class SubTask(BaseModel):
    agent: str = Field(
        description="The exact name of the target agent (e.g. WEATHER, FACTS, TRANSLATION, SUMMARY, MOVIE, FACE)"
    )
    query: str = Field(
        description="The specific prompt or instruction for this agent"
    )

class Stage(BaseModel):
    tasks: List[SubTask]


class ExecutionPlan(BaseModel):
    steps: List[Stage]
def get_supervisor_plan(user_query: str, prompt_path: str = "prompts/supervisor_prompt.md") -> ExecutionPlan:
    """Generates a structured multi-stage execution plan using Groq."""
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    else:
        system_prompt = "You are an AI multi-agent supervisor. Create a structured plan for the query."

    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        temperature=0.0
    )

    structured_llm = llm.with_structured_output(
        ExecutionPlan,
        method="function_calling"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]

    plan_result: ExecutionPlan = structured_llm.invoke(messages)

    print(f"\n[DEBUG] Generated Execution Plan:\n{plan_result}\n")
    return plan_result

def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph supervisor node. Extracts user input from graph state,
    generates the execution plan, and updates the graph state.
    """
    user_query = state.get("query", "")
    if not user_query and state.get("messages"):
        last_msg = state["messages"][-1]
        user_query = getattr(last_msg, "content", str(last_msg))

    plan = get_supervisor_plan(user_query)

    raw_steps = [
    [task.model_dump() for task in stage.tasks]
    for stage in plan.steps
]
    return {
        "plan": raw_steps,
        "current_stage": 0,
        "outputs": [],
        "last_agent": "SUPERVISOR"
    }