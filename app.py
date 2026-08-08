import streamlit as st
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 150  
MAX_FILE_SIZE_MB = 10

st.set_page_config(
    page_title="Multi-Agent AI System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    """Injects custom CSS to style the UI, badges, and attachment popover button."""
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

        /* ATTACHMENT (+) BUTTON STYLING */
        div[data-testid="stPopover"] button svg,
        div[data-testid="stPopover"] button [data-testid="stIconMaterial"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
            opacity: 0 !important;
        }

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
            top: -2px !important;
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
        
        .badge-supervisor { background: linear-gradient(135deg, #9333ea, #6b21a8); } 
        .badge-weather { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }    
        .badge-translation { background: linear-gradient(135deg, #22c55e, #15803d); } 
        .badge-facts { background: linear-gradient(135deg, #f97316, #c2410c); }       
        .badge-summary { background: linear-gradient(135deg, #eab308, #a16207); }     
        .badge-movie { background: linear-gradient(135deg, #ec4899, #be185d); }  
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
        
        [data-testid="stChatMessage"]:has([data-testid="stIconAssistant"]),
        [data-testid="stChatMessage"]:nth-child(even) {
            background: rgba(30, 41, 59, 0.7);
        }

        [data-testid="stChatMessage"]:has([data-testid="stIconUser"]) {
            background: rgba(14, 165, 233, 0.1);
            flex-direction: row-reverse;
            text-align: right;
            border-color: rgba(14, 165, 233, 0.2);
        }

        [data-testid="stChatMessage"]:has([data-testid="stIconUser"]) > div:first-child {
            margin-right: 0;
            margin-left: 15px;
        }
    </style>
    """, unsafe_allow_html=True)

def inject_ui_fixes():
    """Injects JS to lock the + button inside the chat input box."""
    st.html("""
    <script>
        function lockButtonInPlace() {
            const doc = window.parent.document;
            const chatInput = doc.querySelector('[data-testid="stChatInput"]');
            const popover = doc.querySelector('[data-testid="stPopover"]');

            if (chatInput && popover) {
                const innerWrapper = chatInput.querySelector('div');
                
                if (innerWrapper && !innerWrapper.contains(popover)) {
                    innerWrapper.style.position = 'relative';
                    innerWrapper.appendChild(popover);
                    
                    popover.style.position = 'absolute';
                    popover.style.left = '10px';
                    popover.style.bottom = '10px';
                    popover.style.zIndex = '9999';
                    
                    const textArea = chatInput.querySelector('textarea');
                    if (textArea) {
                        textArea.style.setProperty('padding-left', '55px', 'important');
                    }
                }
            }
        }
        setInterval(lockButtonInPlace, 50);
    </script>
    """)

def init_session_state():
    """Initializes session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "last_plan" not in st.session_state:
        st.session_state.last_plan = None

def get_agent_styling(agent_name: str):
    """Returns matching emoji and CSS badge class based on agent identity."""
    name = agent_name.lower() if agent_name else ""
    if "supervisor" in name: return "🟣", "badge-supervisor"
    elif "weather" in name: return "🔵", "badge-weather"
    elif "translation" in name: return "🟢", "badge-translation"
    elif "fact" in name: return "🟠", "badge-facts"
    elif "summary" in name: return "🟡", "badge-summary"
    elif "movie" in name: return "🎬", "badge-movie"
    elif "face" in name or "arcface" in name: return "👤", "badge-face"
    elif "system" in name or "error" in name or "validation" in name: return "⚠️", "badge-system"
    else: return "🤖", "badge-default"



def send_text_request(user_text: str):
    target_url = f"{API_BASE_URL}/api/chat"
    return requests.post(target_url, json={"message": user_text}, timeout=REQUEST_TIMEOUT)

def send_file_request(user_text: str, uploaded_files: list):
    target_url = f"{API_BASE_URL}/api/chat/upload"
    files_payload = [
        ("files", (f.name, f.getvalue(), f.type)) 
        for f in uploaded_files
    ]
    return requests.post(target_url, data={"message": user_text}, files=files_payload, timeout=REQUEST_TIMEOUT)

def send_request_to_backend(user_text: str, uploaded_files=None):
    """
    Main dispatcher for backend execution requests with detailed exception handling.
    Returns: (outputs: list, last_agent: str, plan: list|None)
    """
    try:
        # File Size Validation Check
        if uploaded_files:
            for file in uploaded_files:
                file_size_mb = len(file.getvalue()) / (1024 * 1024)
                if file_size_mb > MAX_FILE_SIZE_MB:
                    err_msg = f"File '{file.name}' ({file_size_mb:.1f} MB) exceeds maximum allowed size of {MAX_FILE_SIZE_MB} MB."
                    return [{"agent": "Validation Error", "content": err_msg}], "Validation Error", None

            response = send_file_request(user_text, uploaded_files)
        else:
            response = send_text_request(user_text)

        response.raise_for_status()
        res_data = response.json()
        
        outputs = res_data.get("outputs", [])
        last_agent = res_data.get("last_agent", "System")
        plan = res_data.get("plan")
        
        if not outputs:
            return [{"agent": last_agent, "content": "No outputs produced by execution pipeline."}], last_agent, plan

        return outputs, last_agent, plan
        
    except requests.exceptions.ConnectionError:
        msg = f"Cannot connect to FastAPI server at {API_BASE_URL}. Ensure main.py is running."
        return [{"agent": "System Error", "content": msg}], "System Error", None
    except requests.exceptions.Timeout:
        msg = f"Backend timed out after {REQUEST_TIMEOUT} seconds. Try reducing workflow query complexity."
        return [{"agent": "System Error", "content": msg}], "System Error", None
    except requests.exceptions.HTTPError as http_err:
        msg = f"Backend returned HTTP error: {http_err.response.status_code} - {http_err.response.text}"
        return [{"agent": "System Error", "content": msg}], "System Error", None
    except Exception as e:
        msg = f"Unexpected client error: {str(e)}"
        return [{"agent": "System Error", "content": msg}], "System Error", None



def display_sidebar():
    with st.sidebar:
        st.markdown("<div class='sidebar-header-title'>🤖 Multi-Agent AI</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: #64748b; font-size: 0.78rem;'>Autonomous Routing Network</div>", unsafe_allow_html=True)
        
        st.write("")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✨ New", use_container_width=True, type="primary"):
                st.session_state.messages = []
                st.session_state.uploaded_files = []
                st.session_state.last_plan = None
                st.rerun()
        with col_b:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.messages = []
                st.session_state.uploaded_files = []
                st.session_state.last_plan = None
                st.rerun()

        st.markdown("<div class='sidebar-section-label'>Overview</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Messages", len(st.session_state.messages))
        active_agent = st.session_state.messages[-1]["agent"] if st.session_state.messages else "None"
        col2.metric("Last Agent", active_agent.replace(" Agent", "") if active_agent else "None")

        # Visualizer for Execution Plan (Debug Mode)
        if st.session_state.last_plan:
            st.markdown("<div class='sidebar-section-label'>Execution Plan</div>", unsafe_allow_html=True)
            with st.expander("🔍 View Stages Plan", expanded=True):
                for stage_idx, stage_tasks in enumerate(st.session_state.last_plan, 1):
                    agents_list = [t.get("agent", "UNKNOWN") for t in stage_tasks]
                    st.markdown(f"**Stage {stage_idx}:** `{', '.join(agents_list)}`")
                    for t in stage_tasks:
                        st.caption(f"↳ *{t.get('agent')}*: {t.get('query')}")

def display_chat_interface():
    if not st.session_state.messages:
        st.markdown("""
        <div style='text-align: center; color: #ffffff; margin-top: -10px; margin-bottom: 40px;'>
            <h3>👋 Welcome! I am your Multi-Agent Assistant.</h3>
            <p style='color: #94a3b8;'>Describe your task, ask a question, or upload one or more images.<br>
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
    # 1. Attachment Popover supporting multiple image uploads
    with st.popover("+", help="Attach Image File(s)"):
        st.markdown("<div style='font-weight: 600; margin-bottom: 8px;'>Attach Image Files</div>", unsafe_allow_html=True)
        
        if st.session_state.uploaded_files:
            st.success(f"{len(st.session_state.uploaded_files)} file(s) attached.")
            if st.button("Clear Attachments"):
                st.session_state.uploaded_files = []
                st.rerun()
                
        new_files = st.file_uploader(
            "Select images", 
            type=["jpg", "jpeg", "png"], 
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        if new_files and (st.session_state.uploaded_files != new_files):
            st.session_state.uploaded_files = new_files
            st.rerun()

    # 2. Native Chat Input
    prompt = st.chat_input("Type your message here...")
    
    if prompt:
        files_to_send = st.session_state.uploaded_files
        user_display = prompt
        
        if files_to_send:
            filenames = ", ".join([f"`{f.name}`" for f in files_to_send])
            user_display += f"\n\n*(Attached {len(files_to_send)} file(s): {filenames})*"

        # Store User Message
        st.session_state.messages.append({"role": "user", "content": user_display, "agent": None})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_display)
            
        # Execute & Display Assistant Response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤖 Agents are working..."):
                agent_outputs, last_agent, plan = send_request_to_backend(prompt, files_to_send)
                
                # Update plan in session state if returned
                if plan:
                    st.session_state.last_plan = plan
                
                # Render worker node outputs
                for output in agent_outputs:
                    agent_name = output.get("agent", "Assistant")
                    content = output.get("content", "")
                    
                    emoji, css_class = get_agent_styling(agent_name)
                    st.markdown(f"<div class='agent-badge {css_class}'>{emoji} {agent_name}</div>", unsafe_allow_html=True)
                    st.markdown(content)
                    
                    st.session_state.messages.append({
                        "role": "ai",
                        "content": content,
                        "agent": agent_name
                    })
        
        # Reset file attachments after message dispatch
        st.session_state.uploaded_files = []
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

if __name__ == "__main__":
    main()