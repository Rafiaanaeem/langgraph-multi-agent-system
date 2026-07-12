import streamlit as st
import requests
import time

# ==========================================
# Configuration & Constants
# ==========================================
API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="Multi-Agent AI System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS Styling (UI Design & Glassmorphism)
# ==========================================
def load_css():
    """Injects custom CSS to create a modern, ChatGPT-like professional UI."""
    st.markdown("""
    <style>
        /* Gradient Header */
        .main-header {
            background: -webkit-linear-gradient(45deg, #0ea5e9, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.8rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 10px;
            padding-top: 20px;
        }
        
        .sub-header {
            text-align: center;
            color: #94a3b8;
            font-size: 1.1rem;
            margin-bottom: 40px;
        }

        /* Glassmorphism Sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.6) !important;
            backdrop-filter: blur(15px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Agent Badges */
        .agent-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        
        /* Agent Specific Colors */
        .badge-supervisor { background: linear-gradient(135deg, #9333ea, #6b21a8); } /* Purple */
        .badge-weather { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }    /* Blue */
        .badge-translation { background: linear-gradient(135deg, #22c55e, #15803d); } /* Green */
        .badge-facts { background: linear-gradient(135deg, #f97316, #c2410c); }       /* Orange */
        .badge-summary { background: linear-gradient(135deg, #eab308, #a16207); }     /* Yellow */
        .badge-gatekeeper { background: linear-gradient(135deg, #ec4899, #be185d); }  /* Pink */
        .badge-system { background: linear-gradient(135deg, #ef4444, #b91c1c); }      /* Red (Errors) */
        .badge-default { background: linear-gradient(135deg, #64748b, #334155); }     /* Gray */

        /* Chat Bubbles Styling */
        [data-testid="stChatMessage"] {
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* AI Message Background */
        [data-testid="stChatMessage"]:has([data-testid="stIconAssistant"]), 
        [data-testid="stChatMessage"]:nth-child(even) {
            background: rgba(30, 41, 59, 0.7); 
        }

        /* Right align User Messages */
        /* Note: Uses modern CSS :has selector to push user messages to the right */
        [data-testid="stChatMessage"]:has([data-testid="stIconUser"]) {
            background: rgba(14, 165, 233, 0.1);
            flex-direction: row-reverse;
            text-align: right;
            border-color: rgba(14, 165, 233, 0.2);
        }

        /* Fix avatar margin when reversed */
        [data-testid="stChatMessage"]:has([data-testid="stIconUser"]) > div:first-child {
            margin-right: 0;
            margin-left: 15px;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }
        
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# Helper Functions
# ==========================================
def init_session_state():
    """Initializes the chat history in Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def get_agent_styling(agent_name: str):
    """Maps the agent name to a specific emoji and CSS class for the badge."""
    name = agent_name.lower()
    
    if "supervisor" in name: return "🟣", "badge-supervisor"
    elif "weather" in name: return "🔵", "badge-weather"
    elif "translation" in name: return "🟢", "badge-translation"
    elif "fact" in name: return "🟠", "badge-facts"
    elif "summary" in name: return "🟡", "badge-summary"
    elif "gatekeeper" in name: return "🛑", "badge-gatekeeper"
    elif "system" in name or "error" in name: return "⚠️", "badge-system"
    else: return "🤖", "badge-default"

def send_request_to_backend(user_text: str):
    """Sends the user input to the FastAPI backend and handles errors gracefully."""
    try:
        response = requests.post(
            API_URL, 
            json={"user_input": user_text},
            timeout=30 # Prevent infinite hanging
        )
        response.raise_for_status() # Check for HTTP errors (4xx, 5xx)
        
        data = response.json()
        return data.get("response", "No response content found."), data.get("last_agent", "Unknown Agent")
        
    except requests.exceptions.ConnectionError:
        return "Backend API is currently unreachable. Please make sure FastAPI is running on `http://127.0.0.1:8000`.", "System Error"
    except requests.exceptions.Timeout:
        return "The request timed out. The agents took too long to process.", "System Error"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}", "System Error"

# ==========================================
# UI Components
# ==========================================
def display_sidebar():
    """Renders the sidebar with controls and project information."""
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>⚙️ Control Panel</h2>", unsafe_allow_html=True)
        st.write("---")
        
        # Action Buttons
        if st.button("✨ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
        if st.button("🗑️ Clear History", type="primary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
        st.write("---")
        
        # Information Section
        st.markdown("### ℹ️ About")
        st.info(
            "This is a Multi-Agent AI System. "
            "It uses a Supervisor architecture to intelligently route your query to specialized agents."
        )
        
        st.markdown("### 🛠️ Technologies Used")
        st.markdown("""
        * **Frontend:** Streamlit 
        * **Backend:** FastAPI
        * **Orchestration:** LangGraph
        * **AI/LLM:** LangChain
        """)
        
        st.write("---")
        st.caption("Developed for Professional AI Architecture.")

def display_chat_interface():
    """Renders the chat history and the badges."""
    # Display welcome message if history is empty
    if not st.session_state.messages:
        st.markdown("""
        <div style='text-align: center; color: #64748b; margin-top: 50px;'>
            <h3>👋 Welcome! I am your Multi-Agent Assistant.</h3>
            <p>Ask me about the weather, translate text, get facts, or summarize data.</p>
        </div>
        """, unsafe_allow_html=True)

    # Render previous messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                # Dynamically generate agent badge
                emoji, css_class = get_agent_styling(msg["agent"])
                badge_html = f"<div class='agent-badge {css_class}'>{emoji} {msg['agent']}</div>"
                
                st.markdown(badge_html, unsafe_allow_html=True)
                st.markdown(msg["content"])

def handle_user_input():
    """Handles the chat input, displays spinners, and updates state."""
    # Chat input bar (Always fixed at bottom)
    prompt = st.chat_input("Type your message here... (e.g., What's the weather in London?)")
    
    if prompt:
        # 1. Add user message to state and UI
        st.session_state.messages.append({"role": "user", "content": prompt, "agent": None})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
            
        # 2. Show loading spinner while waiting for FastAPI
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Processing request..."):
                # API Call
                ai_response, agent_name = send_request_to_backend(prompt)
                
                # Display Badge
                emoji, css_class = get_agent_styling(agent_name)
                badge_html = f"<div class='agent-badge {css_class}'>{emoji} {agent_name}</div>"
                st.markdown(badge_html, unsafe_allow_html=True)
                
                # Display text
                st.markdown(ai_response)
                
        # 3. Save AI message to state
        st.session_state.messages.append({
            "role": "ai", 
            "content": ai_response, 
            "agent": agent_name
        })

# ==========================================
# Main Application Execution
# ==========================================
def main():
    load_css()
    init_session_state()
    display_sidebar()
    
    # Header Area
    st.markdown("<div class='main-header'>✨ Multi-Agent AI System</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Powered by LangGraph, FastAPI & Streamlit</div>", unsafe_allow_html=True)
    
    # Chat Area
    display_chat_interface()
    handle_user_input()

if __name__ == "__main__":
    main()