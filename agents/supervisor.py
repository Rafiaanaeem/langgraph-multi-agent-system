from pathlib import Path

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import Config


PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "supervisor_prompt.md"
SUPERVISOR_PROMPT = PROMPT_PATH.read_text()

VALID_AGENTS = {
    "WEATHER",
    "SUMMARY",
    "TRANSLATION",
    "FACTS",
    "MOVIE",
    "FACE"
}


def supervisor_node(state: dict) -> dict:
    """
    Planner Node

    Reads the user request and creates an execution queue.

    Example outputs:
    WEATHER
    FACE
    FACTS,SUMMARY
    """

    llm = ChatGroq(
        model=Config.MODEL_NAME,
        api_key=Config.GROQ_API_KEY,
        temperature=0
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_PROMPT),
        ("human", "{user_input}")
    ])

    chain = prompt | llm | StrOutputParser()

    user_message = state["messages"][-1].content

    response = chain.invoke({
        "user_input": user_message
    }).strip().upper()

    if response == "UNSUPPORTED":
        return {
            "agent_queue": [],
            "current_agent": "",
            "last_agent": "SUPERVISOR"
        }

    agent_queue = [
        agent.strip()
        for agent in response.split(",")
        if agent.strip()
    ]

    for agent in agent_queue:
        if agent not in VALID_AGENTS:
            raise ValueError(
                f"Supervisor returned invalid agent: {agent}"
            )

    return {
        "agent_queue": agent_queue,
        "current_agent": agent_queue[0],
        "last_agent": ""
    }