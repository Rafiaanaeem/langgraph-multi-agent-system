from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import Config

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "supervisor_prompt.md"
SUPERVISOR_PROMPT = PROMPT_PATH.read_text()

def supervisor_node(state: dict) -> dict:
    llm = ChatGroq(
        model=Config.MODEL_NAME,
        api_key=Config.GROQ_API_KEY,
        temperature=0 
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_PROMPT),
        ("human", "{user_input}")
    ])
    
    user_message = state["messages"][-1].content
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"user_input": user_message})
    
    next_agent = response.strip().upper()
    
    return {"next_node": next_agent}