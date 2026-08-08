from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from tools.weather_tool import get_current_weather
from config import Config
from state import SubTaskState 
import re
from tools.weather_tool import get_current_weather

PROMPTS_DIR = Path("prompts")

llm = ChatGroq(
    model=Config.MODEL_NAME,
    api_key=Config.GROQ_API_KEY,
    temperature=0.0
)

weather_prompt_text = (PROMPTS_DIR / "weather_prompt.md").read_text(encoding="utf-8")
translation_prompt_text = (PROMPTS_DIR / "translation_prompt.md").read_text(encoding="utf-8")
summary_prompt_text = (PROMPTS_DIR / "summary_prompt.md").read_text(encoding="utf-8")
facts_prompt_text = (PROMPTS_DIR / "facts_prompt.md").read_text(encoding="utf-8")
movie_prompt_text = (PROMPTS_DIR / "fifth_agent_prompt.md").read_text(encoding="utf-8")


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

def build_input(state: SubTaskState, is_processing: bool = False) -> str:
    """
    Constructs the input string.
    If it's a processing agent (Translation/Summary), it includes the merged context.
    """
    query = state.get("query", "")
    context = state.get("context", "")
    
    if is_processing and context:
        return f"--- DATA TO PROCESS (FROM PREVIOUS STAGE) ---\n{context}\n\n--- USER INSTRUCTION ---\n{query}"
    return f"USER INSTRUCTION:\n{query}"

def format_agent_output(state: SubTaskState, agent_name: str, content: str) -> dict:
    """
    Routes the output to 'final_outputs' if this is the last stage,
    otherwise routes it to 'step_results' to be merged.
    """
    if state.get("is_final", False):
        return {"final_outputs": [{"agent": agent_name, "content": content}]}
    else:
        return {"step_results": [f"[{agent_name} Output]:\n{content}"]}





def weather_node(state: SubTaskState) -> dict:
    print("\n===== WEATHER AGENT EXECUTING =====")
    query = state.get("query", "").strip()
    city = "Islamabad"
    patterns = [
        r"weather\s+(?:of|in)\s+(.+)",
        r"(?:of|in)\s+(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            break
    city = city.replace("?", "").replace(".", "").strip()
    print(f"[Weather Node] City = {city}")
    weather_result = get_current_weather.invoke({"city": city})
    return format_agent_output(
        state,
        "WEATHER",
        weather_result
    )
def translation_node(state: SubTaskState) -> dict:
    print("\n===== TRANSLATION AGENT EXECUTING =====")
    user_input = build_input(state, is_processing=True)
    response = translation_chain.invoke({"user_input": user_input})
    return format_agent_output(state, "TRANSLATION", response.content)


def summary_node(state: SubTaskState) -> dict:
    print("\n===== SUMMARY AGENT EXECUTING =====")
    user_input = build_input(state, is_processing=True)
    response = summary_chain.invoke({"user_input": user_input})
    return format_agent_output(state, "SUMMARY", response.content)


def facts_node(state: SubTaskState) -> dict:
    print("\n===== FACTS AGENT EXECUTING =====")
    user_input = build_input(state, is_processing=False)
    response = facts_chain.invoke({"user_input": user_input})
    return format_agent_output(state, "FACTS", response.content)


def movie_node(state: SubTaskState) -> dict:
    print("\n===== MOVIE AGENT EXECUTING =====")
    user_input = build_input(state, is_processing=False)
    response = movie_chain.invoke({"user_input": user_input})
    return format_agent_output(state, "MOVIE", response.content)