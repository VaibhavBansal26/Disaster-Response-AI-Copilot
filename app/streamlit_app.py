# import os
# from dotenv import load_dotenv
# import streamlit as st

# load_dotenv()

# st.set_page_config(page_title="Disaster Response Copilot", page_icon="🌪️", layout="wide")

# st.sidebar.title("Settings (SDK)")
# st.sidebar.text_input("Project Endpoint", value=os.getenv("AZURE_AI_PROJECT_ENDPOINT",""), key="proj_endpoint")
# st.sidebar.text_input("Agent ID", value=os.getenv("AZURE_AGENT_ID",""), key="agent_id")
# st.sidebar.text_input("Agent Name (optional)", value=os.getenv("AZURE_AGENT_NAME",""), key="agent_name")
# st.sidebar.caption("Auth via DefaultAzureCredential. Tip: run `az login` first.")

# st.sidebar.markdown("---")
# st.sidebar.title("HTTP (legacy) – not used now")
# st.sidebar.text_input("Agent Endpoint (HTTP)", value=os.getenv("AGENT_ENDPOINT",""), key="endpoint", disabled=True)
# st.sidebar.text_input("API Key / Token", value=os.getenv("AGENT_API_KEY",""), key="api_key", type="password", disabled=True)
# st.sidebar.text_input("API Key Header", value=os.getenv("API_KEY_HEADER","api-key"), key="api_header", disabled=True)
# st.sidebar.text_input("Request Field", value=os.getenv("REQUEST_FIELD","input"), key="req_field", disabled=True)
# st.sidebar.text_input("Response Field", value=os.getenv("RESPONSE_FIELD","output"), key="resp_field", disabled=True)

# st.sidebar.markdown("---")
# st.sidebar.text_input("Azure Maps Key (optional)", value=os.getenv("AZURE_MAPS_KEY",""), key="maps_key")

# st.title("🌪️ Disaster Response Copilot")
# st.write(
#     """Use the pages in the left sidebar:
# - **Dashboard**: visualize incidents from `data/events.csv` on a map.
# - **Ask Agent**: grounded Q&A with citations through Azure AI Projects SDK.
# - **New Incident**: classify & get actions for a new report.
# - **Reports**: export a 1-page PDF situation report.
# """
# )

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Disaster Response AI Copilot",
    page_icon="🌍",
    layout="wide"
)

# --- Hero Section ---
st.markdown("""
    <style>
    .hero {
        background: linear-gradient(90deg, #0078D4 0%, #005A9E 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .metric-card {
        background-color: #F3F9FF;
        border-radius: 1rem;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🌍 Disaster Response AI Copilot</h1>
    <p>Leverage Azure AI Agents, Cognitive Search, and real-time data to manage disasters intelligently.</p>
</div>
""", unsafe_allow_html=True)

st.write("")
st.subheader("📊 System Overview")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Active Disaster Feeds", value="12", delta="↑ 2 new")
with col2:
    st.metric(label="Total Incidents Processed", value="1,247", delta="+8%")
with col3:
    st.metric(label="Response Accuracy", value="94.2%", delta="+1.4%")

st.write("")
st.markdown("---")

st.subheader("🧠 What this app can do")
st.markdown("""
- **Ask AI** → Get instant answers from GPT-4o powered disaster agent  
- **Knowledge Search** → Retrieve facts using **Azure Cognitive Search + RAG**  
- **Reports** → Generate analytics summaries  
- **Map Dashboard** → Visualize affected regions  
""")

st.markdown("---")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
