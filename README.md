Multi-Agent AI System
A modular, state-of-the-art Multi-Agent AI System built using LangGraph, FastAPI, Streamlit, and LangChain. This system intelligently routes user requests to specialized AI agents through a Supervisor Agent, while a Gatekeeper Agent handles general conversations without unnecessarily invoking the complex multi-agent workflow.

Key Features:

1. Intelligent Supervisor Routing: Automatically detects user intent and routes tasks to the correct specialist.
2. Casual Conversation Gatekeeper: Handles greetings, jokes, and general chat instantly to save processing time.
3. Face Recognition Agent: Enroll, identify, and detect multiple faces using ArcFace and ChromaDB.
4. Specialized Specialists: Real-Time Weather, Language Translation, Text Summarization, Random Facts, and Movie Recommendations.
5. Image Upload Support: Seamlessly process images alongside text prompts.
FastAPI Backend: Robust, asynchronous API for agent orchestration.
6. Modern Streamlit Interface: Features a custom, ChatGPT-style unified chat bar and dynamic agent badges.

System Architecture
Unlike traditional linear chains, this system uses a Hub-and-Spoke routing architecture powered by LangGraph.

                          User
                            │
                            ▼
              Streamlit Frontend (Custom UI)
                            │ 
                            ▼
                     FastAPI Backend
                            │
                            ▼
                    Gatekeeper Agent
                   /                \
        Casual Chat                  Complex/Specific Task
             │                               │
             ▼                               ▼
       Direct AI Response             Supervisor Agent
                                             │
             ┌──────────┬──────────┬─────────┼─────────┬──────────┐
             ▼          ▼          ▼         ▼         ▼          ▼
          Weather  Translation  Summary    Facts     Movies  Face Recognition


Agent Profiles
1. The Gatekeeper
Intercepts incoming messages. If the user says "Hi", "How are you?", or "Tell me a joke", the Gatekeeper responds directly. If the prompt requires a specific tool or deep processing, it passes the request to the Supervisor.

2. The Supervisor
The brain of the multi-agent network. It evaluates complex queries, decides which specialized agent is needed (or if multiple are needed), and delegates the task.

3. The Specialized Agents
Weather Agent: Fetches real-time weather data (temperature, feels-like, wind speed) using the OpenWeatherMap API.

Translation Agent: Translates complex texts and paragraphs between languages accurately.

Summary Agent: Condenses long articles or documents into concise, readable summaries.

Facts Agent: Generates interesting, well-researched, and informative facts on demand.

Movie Recommendation Agent: Suggests movies based on genre, release year, and user preferences.

Face Recognition Agent: Handles all computer vision tasks (see deep-dive below).

Face Recognition Deep-Dive
The Face Recognition agent combines InsightFace (ArcFace) for generating facial embeddings and ChromaDB for vector storage.

Face Enrollment: Stores a person's facial embedding in the vector database.

Prompt: "Save this person as Tony Stark" + [Attach Image]

Face Identification: Identifies a known person from an uploaded image.

Prompt: "Who is this person?" + [Attach Image]

Multiple Face Detection: Identifies all known faces within a group photo.

Prompt: "Who are these people?" + [Attach Group Image]

Unknown Face Handling: If no matching embedding exists in ChromaDB, the system gracefully returns "Unknown Person (No match in database)".

Technology Stack

Backend & Orchestration:
Python 3.10+
FastAPI
LangGraph & LangChain
Groq API (LLM Inference)
Computer Vision & Database:
InsightFace / ArcFace
OpenCV
ChromaDB (Vector Database)

Frontend UI:
Streamlit (with custom CSS/JS for a ChatGPT-style interface)
External APIs:
OpenWeatherMap API

Installation & Setup
1. Clone the repository:

Bash
git clone <repository-url>
cd multi_agent_system

2. Create and activate a virtual environment:
Bash
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

3. Install required dependencies:
Bash
pip install -r requirements.txt

4. Configure Environment Variables:
Create a .env file in the root directory and add the following:

Code snippet
GROQ_API_KEY=your_groq_api_key_here
WEATHER_API_KEY=your_openweathermap_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
API_URL=http://127.0.0.1:8000/chat

# ChromaDB Storage Path
CHROMA_PERSIST_DIR=./chroma_db/arcface_db
COLLECTION_NAME=arcface_faces

Running the Application
You need to run both the FastAPI backend and the Streamlit frontend simultaneously.

Terminal 1: Start the Backend (FastAPI)
Bash
uvicorn main:app --reload
The backend will run on [http://127.0.0.1:8000](http://127.0.0.1:8000)

Terminal 2: Start the Frontend (Streamlit)
Bash
streamlit run app.py
The frontend will open automatically in your browser.