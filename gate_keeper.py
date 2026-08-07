from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import Config

gatekeeper_llm = ChatGroq(
    api_key=Config.GROQ_API_KEY,
    model=Config.MODEL_NAME,
    temperature=0, 
    max_tokens=10   
)

casual_llm = ChatGroq(
    api_key=Config.GROQ_API_KEY,
    model=Config.MODEL_NAME,
    temperature=0.7,
    max_tokens=100
)


SYSTEM_PROMPT="""You are ONLY a classifier.

Your job is to decide whether the user's request should be routed to a specialized AI agent.

Available agents:

1. WEATHER
- weather
- temperature
- forecast
- rain
- humidity
- climate

2. FACE
- recognize a person
- identify a person
- who is this
- who are these
- detect faces
- compare faces
- save person
- register person
- enroll person
- add person
- store person
- remember this face
- save this face
- this image
- attached image
- uploaded image

3. SUMMARY
- summarize
- summary
- shorten this
- brief this

4. TRANSLATION
- translate
- convert into
- translate this into

5. FACTS
- tell me facts
- random facts
- interesting facts

6. MOVIE
- recommend movies
- suggest movies
- movie recommendations

Rules:

If the request belongs to ANY of these tasks,
reply with ONLY

ROUTE

Nothing else.

Never answer the user.

Never greet the user.

Never explain.

Never continue the conversation.

If the request does NOT belong to any of the above tasks,
answer normally."""

triage_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{user_input}")
])

chain = triage_prompt | gatekeeper_llm


def check_casual_conversation(user_input: str) -> Optional[str]:
    """
    Acts as a smart gatekeeper before the LangGraph multi-agent system.
    
    Returns:
        Optional[str]: Direct response string for casual chat, or None to hand off to LangGraph.
    """
    try:
        response = chain.invoke({"user_input": user_input})
        classification = response.content.strip().upper().rstrip(".")
        
        print(f"🚪 [Gatekeeper Decision]: '{classification}' for input: '{user_input}'")

        if classification != "CASUAL":
            return None
        
        casual_reply = casual_llm.invoke(
            f"Respond briefly and politely to this greeting: {user_input}"
        )
        return casual_reply.content.strip()

    except Exception as e:
        print(f"⚠️ [Gatekeeper Error]: {e}")
        return None  # On error, safely fall back to LangGraph