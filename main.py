import asyncio
import os
import traceback
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import uvicorn

from graph import app as graph_app
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

app = FastAPI(
    title="Multi-Agent Orchestrator API",
    description="LangGraph Staged Execution Engine with Groq & Face Recognition",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextChatRequest(BaseModel):
    message: str

class AgentOutputResponse(BaseModel):
    agent: str
    content: str

class PipelineResponse(BaseModel):
    status: str
    query: str
    outputs: List[AgentOutputResponse]
    last_agent: str
    plan: Optional[List[List[dict]]] = None

def sort_outputs_by_plan(outputs: List[dict], plan: Optional[List[List[dict]]]) -> List[dict]:
    """
    Sorts outputs deterministically based on the order defined in the supervisor plan,
    preventing race-condition order shifts from parallel execution.
    """
    if not plan:
        return outputs

    # Extract sequential agent order from plan stages
    plan_agent_order = [task["agent"].upper() for stage in plan for task in stage if "agent" in task]

    def get_sort_index(item):
        agent = item.get("agent", "").upper()
        if agent in plan_agent_order:
            return plan_agent_order.index(agent)
        return 999  # Fallback to end if agent is unknown

    return sorted(outputs, key=get_sort_index)


async def execute_graph(user_query: str, files_data: Optional[List[bytes]] = None) -> dict:
    """Invokes the LangGraph workflow with standard initial state."""
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "plan": [],
        "current_stage": 0,
        "context": "",
        "step_results": [],
        "final_outputs": [],
        "last_agent": "USER",
        "files": files_data or []
    }
    
    return await graph_app.ainvoke(initial_state)


# API ENDPOINTS
@app.get("/")
def health_check():
    """Health check endpoint to verify backend status."""
    return {"status": "online", "system": "Multi-Agent Orchestrator API"}


@app.post("/api/chat", response_model=PipelineResponse)
async def chat_text_endpoint(payload: TextChatRequest):
    """
    JSON Endpoint for text-only queries (Weather, Facts, Movie, Translation, Summary).
    """
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")
    
    try:
        final_state = await execute_graph(user_query=payload.message)
        
        plan = final_state.get("plan")
        raw_outputs = final_state.get("final_outputs", [])
        
      
        clean_outputs = [
            {"agent": item["agent"], "content": item["content"]}
            for item in raw_outputs
            if isinstance(item, dict) and item.get("agent") and item.get("agent") != "CLEAR"
        ]
        
        
        sorted_outputs = sort_outputs_by_plan(clean_outputs, plan)
        
        return PipelineResponse(
            status="success",
            query=payload.message,
            outputs=sorted_outputs,
            last_agent=final_state.get("last_agent", "UNKNOWN"),
            plan=plan if DEBUG_MODE else None
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")


@app.post("/api/chat/upload", response_model=PipelineResponse)
async def chat_file_endpoint(
    message: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Multipart Endpoint for queries containing image attachments (Face Recognition).
    """
    if not message.strip():
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")
    
    try:
        uploaded_bytes = []
        for file in files:
            content = await file.read()
            uploaded_bytes.append(content)
            
        final_state = await execute_graph(user_query=message, files_data=uploaded_bytes)
        
        plan = final_state.get("plan")
        raw_outputs = final_state.get("final_outputs", [])
        
        clean_outputs = [
            {"agent": item["agent"], "content": item["content"]}
            for item in raw_outputs
            if isinstance(item, dict) and item.get("agent") and item.get("agent") != "CLEAR"
        ]
        
        sorted_outputs = sort_outputs_by_plan(clean_outputs, plan)
        
        return PipelineResponse(
            status="success",
            query=message,
            outputs=sorted_outputs,
            last_agent=final_state.get("last_agent", "UNKNOWN"),
            plan=plan if DEBUG_MODE else None
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")


# LOCAL TERMINAL TESTER
async def cli_test():
    """Terminal runner for local testing without starting FastAPI."""
    test_query = "Give three facts about AI and weather of Islamabad, then summarize everything."
    print("\n================ LOCAL CLI TEST ================")
    print(f"Executing: '{test_query}'\n")
    
    res = await execute_graph(test_query)
    
    print("\n================ FINAL RESULTS ================")
    for out in res.get("final_outputs", []):
        if isinstance(out, dict) and out.get("agent") != "CLEAR":
            print(f"\n[{out['agent']} Output]:\n{out['content']}")
    print("===============================================\n")


if __name__ == "__main__":
    
    RUN_CLI_TEST = False

    if RUN_CLI_TEST:
        asyncio.run(cli_test())
    else:
        print("Starting FastAPI Server on http://0.0.0.0:8000...")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)