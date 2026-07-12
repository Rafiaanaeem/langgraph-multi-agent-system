from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from config import Config

def check_casual_conversation(user_input: str) -> Optional[str]:
    """
    Acts as a smart gatekeeper before the LangGraph multi-agent system.
    Uses an LLM to determine if the query is casual talk or a specialized task.
    
    Args:
        user_input (str): The raw message from the user.
        
    Returns:
        Optional[str]: The LLM's conversational response, or None if the request 
                       needs to be routed to the Multi-Agent graph.
    """

    llm = ChatGroq(
        api_key=Config.GROQ_API_KEY,
        model=Config.MODEL_NAME,
        temperature=0.3, 
        max_tokens=150   
    )

    triage_prompt = PromptTemplate(
        input_variables=["user_input"],
        template="""You are the conversational gatekeeper for an advanced Multi-Agent AI System.
Your job is to evaluate the user's input and decide how it should be handled.

The system has specialized agents for ONLY these tasks:
1. Weather updates
2. Text summarization
3. Language translation
4. Random facts generation
5. Movie recommendations

RULES:
- If the user asks for ANY of the specialized tasks above, you MUST reply with exactly the word "ROUTE" and absolutely nothing else.
- If the user says a greeting, asks a general question, makes small talk, or asks about something unrelated to the specialized tasks 
-(e.g., "Hi", "Tell me a joke", "Who is Einstein?", "How are you?"), respond to 
-them directly in a polite, engaging, and concise manner.

User Input: {user_input}
Response:"""
    )

    chain = triage_prompt | llm
    
    try:
        response = chain.invoke({"user_input": user_input})
        content = response.content.strip()
        
        if content.upper() == "ROUTE":
            return None
            
        return content
        
    except Exception as e:
        print(f"[ERROR] Gatekeeper failed: {e}")
        return None

