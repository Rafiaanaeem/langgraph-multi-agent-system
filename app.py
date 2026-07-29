import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/chat")

st.set_page_config(
    page_title="Multi-Agent AI System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    """Injects custom CSS to create a modern UI and style the + button."""
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

        /* Glassmorphism Sidebar Container */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.95) !important;
            backdrop-filter: blur(15px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Sidebar Text & Metrics Visibility Fixes */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span {
            color: #cbd5e1;
        }

        [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
        }

        [data-testid="stSidebar"] [data-testid="stMetricValue"] {
            color: #38bdf8 !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
        }
        
        /* Sleek Sidebar Helper Classes */
        .sidebar-header-title {
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            color: #f1f5f9;
            margin-bottom: 2px;
        }
        .sidebar-section-label {
            color: #64748b !important;
            font-size: 0.75rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-top: 22px;
            margin-bottom: 8px;
        }

        /* =========================================
           ATTACHMENT (+) BUTTON STYLING FIXES 
           ========================================= */
           
        /* 1. COMPLETELY HIDE THE DOWNWARD ARROW */
        div[data-testid="stPopover"] button svg,
        div[data-testid="stPopover"] button [data-testid="stIconMaterial"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
            opacity: 0 !important;
        }

        /* 2. STYLE THE SQUARE + BUTTON */
        div[data-testid="stPopover"] {
            width: 36px !important;
            height: 36px !important;
        }

        div[data-testid="stPopover"] button {
            width: 36px !important;
            height: 36px !important;
            min-width: 36px !important;
            min-height: 36px !important;
            background-color: #1e293b !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stPopover"] button:hover {
            background-color: #334155 !important;
            border-color: rgba(255, 255, 255, 0.4) !important;
            transform: scale(1.05);
        }

        div[data-testid="stPopover"] button p {
            font-size: 1.8rem !important;
            line-height: 1 !important;
            color: #38bdf8 !important;
            margin: 0 !important;
            padding: 0 !important;
            position: relative !important;
            top: -2px !important; /* Visually centers the + */
        }

        div[data-testid="stPopover"] button:hover p {
            color: #ffffff !important;
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
        .badge-supervisor { background: linear-gradient(135deg, #9333ea, #6b21a8); } 
        .badge-weather { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }    
        .badge-translation { background: linear-gradient(135deg, #22c55e, #15803d); } 
        .badge-facts { background: linear-gradient(135deg, #f97316, #c2410c); }       
        .badge-summary { background: linear-gradient(135deg, #eab308, #a16207); }     
        .badge-gatekeeper { background: linear-gradient(135deg, #ec4899, #be185d); }  
        .badge-face { background: linear-gradient(135deg, #06b6d4, #0e7490); }        
        .badge-system { background: linear-gradient(135deg, #ef4444, #b91c1c); }      
        .badge-default { background: linear-gradient(135deg, #64748b, #334155); }     

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
    </style>
    """, unsafe_allow_html=True)

def inject_ui_fixes():
    """Aggressively injects JS to lock the + button inside the chat input."""
    st.html("""
    <script>
        function lockButtonInPlace() {
            // Access the parent DOM outside the st.html iframe
            const doc = window.parent.document;
            const chatInput = doc.querySelector('[data-testid="stChatInput"]');
            const popover = doc.querySelector('[data-testid="stPopover"]');

            if (chatInput && popover) {
                // Find the immediate text container inside the chat block
                const innerWrapper = chatInput.querySelector('div');
                
                if (innerWrapper && !innerWrapper.contains(popover)) {
                    // Lock the container relative
                    innerWrapper.style.position = 'relative';
                    
                    // Physically move the + button inside
                    innerWrapper.appendChild(popover);
                    
                    // Position it perfectly on the far left
                    popover.style.position = 'absolute';
                    popover.style.left = '10px';
                    popover.style.bottom = '10px';
                    popover.style.zIndex = '9999';
                    
                    // Push the text cursor right so typing doesn't overlap the button
                    const textArea = chatInput.querySelector('textarea');
                    if (textArea) {
                        textArea.style.setProperty('padding-left', '55px', 'important');
                    }
                }
            }
        }
        
        // Run continuously every 50ms to defeat Streamlit's React re-renders
        setInterval(lockButtonInPlace, 50);
    </script>
    """)

def init_session_state():
    """Initializes the chat history in Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None

def get_agent_styling(agent_name: str):
    name = agent_name.lower() if agent_name else ""
    if "supervisor" in name: return "🟣", "badge-supervisor"
    elif "weather" in name: return "🔵", "badge-weather"
    elif "translation" in name: return "🟢", "badge-translation"
    elif "fact" in name: return "🟠", "badge-facts"
    elif "summary" in name: return "🟡", "badge-summary"
    elif "gatekeeper" in name: return "🛑", "badge-gatekeeper"
    elif "face" in name or "arcface" in name: return "👤", "badge-face"
    elif "system" in name or "error" in name: return "⚠️", "badge-system"
    else: return "🤖", "badge-default"

def send_request_to_backend(user_text: str, uploaded_file=None):
    try:
        payload = {"user_input": user_text}
        files_payload = None
        if uploaded_file:
            files_payload = [("files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type))]

        response = requests.post(API_URL, data=payload, files=files_payload, timeout=150)
        response.raise_for_status()
        
        data = response.json()
        return data.get("response", "No response content found."), data.get("last_agent", "Unknown Agent")
        
    except Exception as e:
        return f"System Error: {str(e)}", "System Error"

def display_sidebar():
    with st.sidebar:
        st.markdown("<div class='sidebar-header-title'>🤖 Multi-Agent AI</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: #64748b; font-size: 0.78rem;'>Autonomous Routing Network</div>", unsafe_allow_html=True)
        
        st.write("")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✨ New", use_container_width=True, type="primary"):
                st.session_state.messages = []
                st.session_state.uploaded_file = None
                st.rerun()
        with col_b:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.messages = []
                st.session_state.uploaded_file = None
                st.rerun()

        st.markdown("<div class='sidebar-section-label'>Overview</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Messages", len(st.session_state.messages))
        active_agent = st.session_state.messages[-1]["agent"] if st.session_state.messages else "None"
        col2.metric("Last Agent", active_agent.replace(" Agent", "") if active_agent else "None")

def display_chat_interface():
    if not st.session_state.messages:
        st.markdown("""
        <div style='text-align: center; color: #fffff; margin-top: -30px; margin-bottom: 50px;'>
            <h3>👋 Welcome! I am your Multi-Agent Assistant.</h3>
            <p>Describe your task, ask a question, or upload an image.<br>
            I'll assemble the right AI specialists behind the scenes to get it done.</p>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                emoji, css_class = get_agent_styling(msg["agent"])
                st.markdown(f"<div class='agent-badge {css_class}'>{emoji} {msg['agent']}</div>", unsafe_allow_html=True)
                st.markdown(msg["content"])

def handle_user_input():
    # 1. Render Popover (JS will move this inside the Chat Input)
    with st.popover("+", help="Attach Image"):
        st.markdown("<div style='font-weight: 600; margin-bottom: 8px;'>Attach Image File</div>", unsafe_allow_html=True)
        
        if st.session_state.uploaded_file:
            st.success(f"Attached: {st.session_state.uploaded_file.name}")
            if st.button("Remove Attachment"):
                st.session_state.uploaded_file = None
                st.rerun()
                
        uploaded_file = st.file_uploader("Select image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        
        if uploaded_file and (st.session_state.uploaded_file != uploaded_file):
            st.session_state.uploaded_file = uploaded_file
            st.rerun()

    # 2. Render Native Chat Input (Sticks to the bottom natively)
    prompt = st.chat_input("Type your message here...")
    
    if prompt:
        file_to_send = st.session_state.uploaded_file
        user_display = prompt
        
        if file_to_send:
            user_display += f"\n\n*(Attached file: `{file_to_send.name}`)*"

        st.session_state.messages.append({"role": "user", "content": user_display, "agent": None})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_display)
            
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Processing request..."):
                ai_response, agent_name = send_request_to_backend(prompt, file_to_send)
                
                emoji, css_class = get_agent_styling(agent_name)
                st.markdown(f"<div class='agent-badge {css_class}'>{emoji} {agent_name}</div>", unsafe_allow_html=True)
                st.markdown(ai_response)
                
        st.session_state.messages.append({
            "role": "ai",
            "content": ai_response,
            "agent": agent_name
        })
        
        # Clear the file after sending
        st.session_state.uploaded_file = None
        st.rerun()

def main():
    load_css()
    inject_ui_fixes()
    init_session_state()
    display_sidebar()
    
    st.markdown("<div class='main-header'>✨ Multi-Agent AI System</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Powered by LangGraph, FastAPI & Streamlit</div>", unsafe_allow_html=True)
    
    display_chat_interface()
    handle_user_input()

# Ensures the app actually runs!
if __name__ == "__main__":
    main()