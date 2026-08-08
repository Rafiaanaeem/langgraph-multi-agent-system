from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from config import Config
from state import SubTaskState
from agents.tools import AddTool, SearchTool
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
        description="Output 'ADD' or 'SEARCH'."
    )
    person_name: str | None = Field(
        default=None, 
        description="The full name of the person to enroll/save. Return null if SEARCH or if no name is present."
    )

parser = llm.with_structured_output(FaceIntentOutput)

# Much stronger system prompt for precise intent classification
INTENT_SYSTEM_PROMPT = """You are an intent classifier.
Classify the request into exactly ONE intent.

ADD
Use when the user wants to:
- save
- register
- add
- enroll
- store
- insert
- create a new person

SEARCH
Use when the user wants to:
- identify
- recognize
- find
- search
- who is this
- whose face
- detect the person

If ADD, extract the complete person name.
If SEARCH, person_name must be null.

Never explain. Only produce structured output."""

prompt = ChatPromptTemplate.from_messages([
    ("system", INTENT_SYSTEM_PROMPT),
    ("human", "Instruction: {instruction}")
])

chain = prompt | parser


def format_search_results(result: dict) -> str:
    """Helper to turn search JSON into clean chat responses."""
    if not result.get("success"):
        return result.get("message", "Search failed.")
        
    responses = []
    for res in result.get("results", []):
        filename = res.get("filename", "image")
        matches = res.get("matches", [])
        
        responses.append(f"**Image: {filename}**\n")
        
        if not matches:
            responses.append("No faces detected.\n")
            continue
            
        for idx, match in enumerate(matches):
            name = match['person_name']
            conf = match['similarity_percent']
            if name == "Unknown":
                responses.append(f"Face {idx+1}: **Unknown**\n")
            else:
                responses.append(f"Face {idx+1}: **{name}** ({conf}%)\n")
            
    return "\n".join(responses)


def format_agent_output(state: SubTaskState, agent_name: str, content: str) -> dict:
    """Standardized response formatter for global state management."""
    if state.get("is_final", False):
        return {
            "final_outputs": [{"agent": agent_name, "content": content}],
            "last_agent": agent_name
        }
    else:
        return {
            "step_results": [f"[{agent_name} Output]:\n{content}"],
            "last_agent": agent_name
        }


async def face_node(state: SubTaskState) -> dict:
    """
    LangGraph Node for Face Recognition.
    Reads subtask query and files from state, determines intent, and executes tools.
    """
    instruction = state.get("query", "")
    files = state.get("files") or []

    print(f"\n========== FACE ==========\nQuery: {instruction}\nFiles attached: {len(files)}\n")

    # Determine Intent using LLM
    try:
        parsed_result = await chain.ainvoke({"instruction": instruction})
        action = parsed_result.intent.upper()
        person_name = parsed_result.person_name
        
        # Clean up the parsed name
        if person_name:
            person_name = person_name.strip()
            
    except Exception as e:
        print(f" LLM Parsing error: {e}")
        # Safe fallback instead of blindly defaulting to SEARCH
        return format_agent_output(
            state, 
            "FACE", 
            "I couldn't determine whether you want to enroll or search. Please rephrase your request."
        )

    # Route to Tool
    if action == "ADD":
        if not person_name:
            result_msg = "Please provide the person's name in your request to enroll them (e.g., 'Enroll this person as John Doe')."
        elif not files:
            result_msg = "Please attach an image to enroll the person."
        else:
            result: dict = await add_tool.execute(person_name=person_name, files=files)
            if result.get("success"):
                result_msg = result["message"]
            else:
                result_msg = result.get("message", "Operation failed.")
            
    else:  # SEARCH
        if not files:
            result_msg = "Please attach an image so I can identify the person."
        else:
            result: dict = await search_tool.execute(files=files)
            result_msg = format_search_results(result)

    return format_agent_output(state, "FACE", result_msg)