from fastapi import FastAPI, File, UploadFile, Form
from typing import List, Optional
from langchain_core.messages import HumanMessage
from graph import app as langgraph_app
from gate_keeper import check_casual_conversation

app = FastAPI()

@app.get("/")
def welcome_screen():
    return {"message": "Welcome to the Multi-Agent System!"}

@app.post("/chat")
async def chat_endpoint(
    user_input: str = Form(...), 
    files: Optional[List[UploadFile]] = File(None)
):
    processed_files = []
    if files:
        for f in files:
            content = await f.read()
            processed_files.append({
                "filename": f.filename or "uploaded_image.jpg",
                "bytes": content
            })

    gatekeeper_response = check_casual_conversation(user_input)
    if gatekeeper_response:
        return {
            "response": gatekeeper_response, 
            "last_agent": "Gatekeeper"
        }

    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "files": processed_files,
        "agent_queue": []
    }
    
    final_state = await langgraph_app.ainvoke(initial_state)
    
    ai_response = final_state["messages"][-1].content
    agent_name = final_state.get("last_agent", "Supervisor")

    return {
        "response": ai_response, 
        "last_agent": agent_name
    }