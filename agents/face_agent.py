from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from config import Config
from agents.tools import AddTool, SearchTool
from agents.all_agents import update_queue
from models.model_loader import arcface
from services.chroma_service import chroma_db
collection = chroma_db.collection
add_tool = AddTool(face_app=arcface, collection=collection)
search_tool = SearchTool(face_app=arcface, collection=collection)

llm = ChatGroq(
    model=Config.MODEL_NAME,
    api_key=Config.GROQ_API_KEY,
    temperature=0
)

class FaceIntentOutput(BaseModel):
    intent: str = Field(
        description="Output 'ADD' if user wants to enroll, register, save, or add a face. Output 'SEARCH' if they want to identify, recognize, search, or ask 'who is this'."
    )
    person_name: str | None = Field(
        default=None, 
        description="The full name of the person to enroll/save. Return null if SEARCH or if no name is present."
    )

parser = llm.with_structured_output(FaceIntentOutput)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract the face recognition intent ('ADD' or 'SEARCH') and target person's name if enrolling."),
    ("human", "Instruction: {instruction}")
])

chain = prompt | parser

async def face_recognition_node(state: dict) -> dict:
    """
    LangGraph Node for Face Recognition.
    Reads instruction and files from state, determines intent, and executes tool.
    """
    print("🤖 [Face Agent] Analyzing request...")
    
    instruction = state["messages"][-1].content
    files = state.get("files") or []

    # Determine Intent using LLM
    try:
        parsed_result = await chain.ainvoke({"instruction": instruction})
        action = parsed_result.intent.upper()
        person_name = parsed_result.person_name
    except Exception as e:
        print(f" LLM Parsing error: {e}")
        action, person_name = "SEARCH", None

    # Route to Tool
    if action == "ADD":
        if not person_name:
            result_msg = "Please provide the person's name in your request to enroll them (e.g., 'Enroll this person as John Doe')."
        elif not files:
            result_msg = "Please attach an image to enroll the person."
        else:
            result = await add_tool.execute(person_name=person_name, files=files)
            result_msg = result.get("message", str(result))
            
    else:  # SEARCH
        if not files:
            result_msg = "Please attach an image so I can identify the person."
        else:
            result = await search_tool.execute(files=files)
            result_msg = format_search_results(result)

    queue_updates = update_queue(state, "FACE")

    return {
        "messages": [AIMessage(content=result_msg)],
        "last_agent": "Face Recognition Agent",
        **queue_updates
    }


def format_search_results(result: dict) -> str:
    """Helper to turn search JSON into clean chat responses."""
    if not result.get("success"):
        return result.get("message", "Search failed.")
        
    responses = []
    for res in result.get("results", []):
        filename = res.get("filename", "image")
        matches = res.get("matches", [])
        
        if not matches:
            responses.append(f"No faces detected in `{filename}`.")
            continue
            
        for idx, match in enumerate(matches):
            name = match['person_name']
            conf = match['similarity_percent']
            if name == "Unknown":
                responses.append(f"Face #{idx+1} in `{filename}`: **Unknown Person** (No match in database).")
            else:
                responses.append(f"Face #{idx+1} in `{filename}`: Identified as **{name}** ({conf}% match).")
            
    return "\n".join(responses)