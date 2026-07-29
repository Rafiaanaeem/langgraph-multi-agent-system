from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from tools.weather_tool import get_current_weather
from config import Config

PROMPTS_DIR = Path("prompts")

llm = ChatGroq(
    model=Config.MODEL_NAME,
    api_key=Config.GROQ_API_KEY,
    temperature=0.0
)

weather_prompt_text = (PROMPTS_DIR / "weather_prompt.md").read_text(encoding="utf-8")
translation_prompt_text = (PROMPTS_DIR / "translation_prompt.md").read_text()
summary_prompt_text = (PROMPTS_DIR / "summary_prompt.md").read_text()
facts_prompt_text = (PROMPTS_DIR / "facts_prompt.md").read_text()
movie_prompt_text = (PROMPTS_DIR / "fifth_agent_prompt.md").read_text()

weather_agent = create_react_agent(
    model=llm,
    tools=[get_current_weather],
    prompt=weather_prompt_text
)

translation_chain = ChatPromptTemplate.from_messages([
    ("system", translation_prompt_text),
    ("human", "{user_input}")
]) | llm

summary_chain = ChatPromptTemplate.from_messages([
    ("system", summary_prompt_text),
    ("human", "{user_input}")
]) | llm

facts_chain = ChatPromptTemplate.from_messages([
    ("system", facts_prompt_text),
    ("human", "{user_input}")
]) | llm

movie_chain = ChatPromptTemplate.from_messages([
    ("system", movie_prompt_text),
    ("human", "{user_input}")
]) | llm


def update_queue(state: dict, current_node_name: str) -> dict:
    """
    Removes the finished agent from the queue and logs queue transitions.
    """
    queue = list(state.get("agent_queue", []))
    print(f" [QUEUE BEFORE - {current_node_name}]: {queue}")

    if queue and queue[0] == current_node_name:
        queue = queue[1:]

    next_agent = queue[0] if queue else ""
    updates = {
        "agent_queue": queue,
        "current_agent": next_agent
    }
    print(f" [QUEUE AFTER  - {current_node_name}]: {queue} | Next Agent: '{next_agent}'")
    return updates


def build_chained_input(state: dict) -> str:
    """
    Safely retrieves context for chained executions. If an agent ran previously,
    combines the original user prompt with the previous agent's output.
    """
    messages = state.get("messages", [])
    if not messages:
        return ""
    
    if len(messages) == 1:
        return messages[0].content
    
    original_request = messages[0].content
    latest_data = messages[-1].content
    return f"User Instruction: {original_request}\n\nContext/Data to Process:\n{latest_data}"


def weather_node(state: dict) -> dict:
    print("\n===== WEATHER AGENT STARTED =====")
    
    result = weather_agent.invoke(
        {"messages": state["messages"]},
        config={"recursion_limit": 5}
    )

    queue_updates = update_queue(state, "WEATHER")

    return {
        **queue_updates,
        "messages": [result["messages"][-1]],
        "last_agent": "Weather Agent",
    }


def translation_node(state: dict) -> dict:
    print("\n===== TRANSLATION AGENT STARTED =====")
    
    combined_input = build_chained_input(state)
    response = translation_chain.invoke({"user_input": combined_input})
    
    queue_updates = update_queue(state, "TRANSLATION")
    
    return {
        "messages": [response], 
        "last_agent": "Translation Agent",
        **queue_updates
    }


def summary_node(state: dict) -> dict:
    print("\n===== SUMMARY AGENT STARTED =====")
    
    combined_input = build_chained_input(state)
    response = summary_chain.invoke({"user_input": combined_input})
    
    queue_updates = update_queue(state, "SUMMARY")
    
    return {
        "messages": [response], 
        "last_agent": "Summary Agent",
        **queue_updates
    }


def facts_node(state: dict) -> dict:
    print("\n===== FACTS AGENT STARTED =====")
    
    combined_input = build_chained_input(state)
    response = facts_chain.invoke({"user_input": combined_input})
    
    queue_updates = update_queue(state, "FACTS")
    
    return {
        "messages": [response], 
        "last_agent": "Facts Agent",
        **queue_updates
    }


def movie_node(state: dict) -> dict:
    print("\n===== MOVIE AGENT STARTED =====")
    
    combined_input = build_chained_input(state)
    response = movie_chain.invoke({"user_input": combined_input})
    
    queue_updates = update_queue(state, "MOVIE")
    
    return {
        "messages": [response], 
        "last_agent": "Movie Agent",
        **queue_updates
    }