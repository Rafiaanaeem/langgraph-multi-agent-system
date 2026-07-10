# Multi-Agent LLM Orchestrator with State Tracking

A multi-agent AI system built using LangGraph and FastAPI. This system utilizes a supervisor-worker architecture to intelligently route user queries to specialized AI agents while maintaining strict state tracking across the conversation.

1. Key Features

* **State-Driven Orchestration:** Uses LangGraph to manage complex agent workflows and state transitions.
* **Supervisor Routing:** A central supervisor node evaluates user intent and dynamically routes the request to the most suitable specialized agent.
* **Strict State Tracking:** Implements a custom AgentState using TypedDict to track the conversation history and specifically monitor the last_agent, ensuring transparency of which node processed the request.
* **Rule-Based Gatekeeper:** Intercepts small talk and casual conversation before invoking the LLM graph, saving tokens, time, and computational resources.
* **FastAPI Backend:** Fully asynchronous and robust REST API with automatic interactive documentation (Swagger UI).
* **Specialized Worker Agents:** Includes targeted agents for Weather data retrieval, Movie recommendations, Cross-lingual text translation, and Knowledge summarization.

2. Tech Stack

* **Framework:** FastAPI, Uvicorn
* **AI & Orchestration:** LangChain, LangGraph
* **Data Validation:** Pydantic
* **Language:** Python 3.9+

3. Create a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

4. Install Dependencies
pip install fastapi uvicorn pydantic langchain langchain-core langgraph

5. Set Environment Variables
Create a .env file in the root directory and add your required API keys:
OPENAI_API_KEY=your_api_key_here
WEATHER_API_KEY=your_api_key_here

6. Run the Server
uvicorn main:app --reload