# from langchain_core.messages import HumanMessage
# from config import Config
# from gate_keeper import check_casual_conversation
# from graph import app

# def main():
#     """Main execution loop for the Multi-Agent System."""
    
#     # 1. Validate configuration before starting
#     try:
#         Config.validate_config()
#     except ValueError as e:
#         print(e)
#         return

#     print("="*60)
#     print("Welcome to the Professional Multi-Agent AI System")
#     print("Type 'exit' or 'quit' to close the application.")
#     print("="*60)

#     # 2. Start the interactive loop
#     while True:
#         user_input = input("\nYou: ").strip()
        
#         # Exit condition
#         if user_input.lower() in ['exit', 'quit']:
#             print("System shutting down. Goodbye!")
#             break
            
#         if not user_input:
#             continue

#         # 3. Layer 1: The LLM Gatekeeper (Rule-Based / Triage)
#         print("[System] Checking intent...")
#         gatekeeper_response = check_casual_conversation(user_input)

#         # If it's casual chat, the gatekeeper handled it. Print and loop.
#         if gatekeeper_response is not None:
#             print(f"AI: {gatekeeper_response}")
#             continue
            
#         # 4. Layer 2: The Multi-Agent LangGraph
#         print("[System] Routing to Specialized Agents via Supervisor...")
        
#         # Format the user input into LangChain's message format
#         initial_state = {
#             "messages": [HumanMessage(content=user_input)]
#         }
        
#         try:
#             # Invoke the LangGraph workflow
#             final_state = app.invoke(initial_state)
            
#             # Extract the final message appended by the specialized agent
#             ai_response = final_state["messages"][-1].content
#             agent_name = final_state.get("last_agent", "Supervisor")
#             print(f"\n[{agent_name}] AI: {ai_response}")
            
            
#         except Exception as e:
#             print(f"\n[ERROR] The system encountered an issue during execution: {e}")

# if __name__ == "__main__":
#     main()

from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from graph import app as langgraph_app
from gate_keeper import check_casual_conversation

app = FastAPI()

class ChatRequest(BaseModel):
    user_input: str

@app.get("/")
def welcome_screen():
    return {
        "message": "Welcome to the Multi-Agent System!", 
    }
@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    user_text = request.user_input

    gatekeeper_response = check_casual_conversation(user_text)
    if gatekeeper_response:
        return {
            "response": gatekeeper_response, 
            "last_agent": "Gatekeeper"
        }

    initial_state = {"messages": [HumanMessage(content=user_text)]}
    final_state = langgraph_app.invoke(initial_state)
    ai_response = final_state["messages"][-1].content
    agent_name = final_state.get("last_agent", "Supervisor")

    return {
        "response": ai_response, 
        "last_agent": agent_name
    }