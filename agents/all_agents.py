from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from tools.weather_tool import get_current_weather
from config import Config

llm = ChatGroq(
    model=Config.MODEL_NAME,
    api_key=Config.GROQ_API_KEY,
    temperature=0.3
)

PROMPTS_DIR = Path("prompts")

# --- WEATHER AGENT ---
def weather_node(state: dict) -> dict:
    weather_prompt = (PROMPTS_DIR / "weather_prompt.md").read_text()
    agent = create_react_agent(model=llm, tools=[get_current_weather], prompt=weather_prompt)
    result = agent.invoke({"messages": state["messages"]})
    
    return {
        "messages": [result["messages"][-1]], 
        "last_agent": "Weather Agent" 
    }

# --- SUMMARY AGENT ---
def summary_node(state: dict) -> dict:
    summary_prompt = (PROMPTS_DIR / "summary_prompt.md").read_text()
    prompt = ChatPromptTemplate.from_messages([("system", summary_prompt), ("human", "{user_input}")])
    chain = prompt | llm
    user_message = state["messages"][-1].content
    response = chain.invoke({"user_input": user_message})
    
    return {
        "messages": [response], 
        "last_agent": "Summary Agent"  
    }

def translation_node(state: dict) -> dict:
    translation_prompt = (PROMPTS_DIR / "translation_prompt.md").read_text()
    prompt = ChatPromptTemplate.from_messages([("system", translation_prompt), ("human", "{user_input}")])
    chain = prompt | llm
    user_message = state["messages"][-1].content
    response = chain.invoke({"user_input": user_message})
    
    return {
        "messages": [response], 
        "last_agent": "Translation Agent"  
    }

def facts_node(state: dict) -> dict:
    facts_prompt = (PROMPTS_DIR / "facts_prompt.md").read_text()
    prompt = ChatPromptTemplate.from_messages([("system", facts_prompt), ("human", "{user_input}")])
    chain = prompt | llm
    user_message = state["messages"][-1].content
    response = chain.invoke({"user_input": user_message})
    
    return {
        "messages": [response], 
        "last_agent": "Facts Agent"  
    }

def movie_node(state: dict) -> dict:
    movie_prompt = (PROMPTS_DIR / "fifth_agent_prompt.md").read_text()
    prompt = ChatPromptTemplate.from_messages([("system", movie_prompt), ("human", "{user_input}")])
    chain = prompt | llm
    user_message = state["messages"][-1].content
    response = chain.invoke({"user_input": user_message})
    
    return {
        "messages":[response], 
        "last_agent": "Movie Agent"  
    }