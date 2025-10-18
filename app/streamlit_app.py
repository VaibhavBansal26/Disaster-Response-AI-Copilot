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

# import streamlit as st
# from datetime import datetime

# st.set_page_config(
#     page_title="Disaster Response AI Copilot",
#     page_icon="🌍",
#     layout="wide"
# )

# # --- Hero Section ---
# st.markdown("""
#     <style>
#     .hero {
#         background: linear-gradient(90deg, #0078D4 0%, #005A9E 100%);
#         color: white;
#         padding: 3rem 2rem;
#         border-radius: 1rem;
#         text-align: center;
#         box-shadow: 0 4px 20px rgba(0,0,0,0.2);
#     }
#     .metric-card {
#         background-color: #F3F9FF;
#         border-radius: 1rem;
#         padding: 1.5rem;
#         text-align: center;
#         box-shadow: 0 2px 10px rgba(0,0,0,0.05);
#     }
#     </style>
# """, unsafe_allow_html=True)

# st.markdown("""
# <div class="hero">
#     <h1>🌍 Disaster Response AI Copilot</h1>
#     <p>Leverage Azure AI Agents, Cognitive Search, and real-time data to manage disasters intelligently.</p>
# </div>
# """, unsafe_allow_html=True)

# st.write("")
# st.subheader("📊 System Overview")

# col1, col2, col3 = st.columns(3)
# with col1:
#     st.metric(label="Active Disaster Feeds", value="12", delta="↑ 2 new")
# with col2:
#     st.metric(label="Total Incidents Processed", value="1,247", delta="+8%")
# with col3:
#     st.metric(label="Response Accuracy", value="94.2%", delta="+1.4%")

# st.write("")
# st.markdown("---")

# st.subheader("🧠 What this app can do")
# st.markdown("""
# - **Ask AI** → Get instant answers from GPT-4o powered disaster agent  
# - **Knowledge Search** → Retrieve facts using **Azure Cognitive Search + RAG**  
# - **Reports** → Generate analytics summaries  
# - **Map Dashboard** → Visualize affected regions  
# """)

# st.markdown("---")

# st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# app/Home.py
import os, time, json, requests, streamlit as st
from datetime import datetime, timezone
from typing import List, Dict

st.set_page_config(page_title="Disaster Response AI Copilot", page_icon="🌍", layout="wide")

# --- Styles (simple, Azure-ish)
st.markdown("""
<style>
.hero {background: linear-gradient(90deg,#0078D4 0%,#005A9E 100%); color:white; padding:2rem; border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,0.15);}
.card {background:#F3F9FF; border-radius:14px; padding:1rem 1.25rem; box-shadow:0 4px 14px rgba(0,0,0,0.07);}
.kp {font-size:2rem; font-weight:700; margin:0;}
.kpsub {opacity:.85; margin-top:.25rem;}
.section-title {margin-top:.75rem; margin-bottom:.25rem;}
hr {border:0; border-top:1px solid #eaeaea; margin:1rem 0;}
code {background:#f6f8fa; padding:2px 6px; border-radius:6px;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------
# Helpers
# ---------------------------------------------
def get_secret(name: str, default: str | None = None):
    try:
        import streamlit as st  # st.secrets available on Cloud
        if name in st.secrets: return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name, default)

def fmt_ts(ms: int | None) -> str:
    if not ms: return "—"
    dt = datetime.fromtimestamp(ms/1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M UTC")

@st.cache_data(ttl=300, show_spinner=False)
def fetch_usgs() -> List[Dict]:
    """USGS all day feed; returns simplified list."""
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        recs = []
        for f in data.get("features", []):
            p = f.get("properties", {})
            g = f.get("geometry", {}) or {}
            coords = g.get("coordinates") or []
            if len(coords) < 2: 
                continue
            lon, lat = coords[0], coords[1]
            recs.append({
                "id": f.get("id"),
                "title": p.get("title"),
                "magnitude": p.get("mag"),
                "time_ms": p.get("time"),
                "lat": lat, "lon": lon,
                "url": p.get("url")
            })
        return recs
    except Exception:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def search_doc_count(endpoint: str, key: str, index_name: str) -> int | None:
    """Return count of documents in Azure AI Search index (fast path)."""
    try:
        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents import SearchClient
        sc = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(key))
        # cheapest way: a count-only query
        results = sc.search(search_text="*", include_total_count=True, top=0)
        return results.get_count()
    except Exception:
        return None

def push_recent(q: str):
    if not q: return
    key = "recent_questions"
    st.session_state.setdefault(key, [])
    arr = [q] + [x for x in st.session_state[key] if x != q]
    st.session_state[key] = arr[:8]

# ---------------------------------------------
# Hero
# ---------------------------------------------
st.markdown("""
<div class="hero">
  <h1>🌍 Disaster Response AI Copilot</h1>
  <p>Real-time alerts, knowledge search, and agentic analysis — on Azure.</p>
</div>
""", unsafe_allow_html=True)
st.write("")

# ---------------------------------------------
# Live Snapshot + Knowledge Stats
# ---------------------------------------------
colA, colB, colC, colD = st.columns(4)

# Live quakes
quakes = fetch_usgs()
q_count = len(quakes)
q_max = max([q["magnitude"] or 0 for q in quakes], default=0)
with colA:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="kp">🛰️ {}</div>'.format(q_count), unsafe_allow_html=True)
    st.markdown('<div class="kpsub">Incidents (USGS • 24h)</div>', unsafe_allow_html=True)
    st.markdown(f"<div>Max M: <b>{q_max:.1f}</b></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Knowledge base stats
SEARCH_ENDPOINT = get_secret("SEARCH_ENDPOINT")
SEARCH_ADMIN_KEY = get_secret("SEARCH_ADMIN_KEY")
SEARCH_INDEX = get_secret("SEARCH_INDEX", "disaster-knowledge")
kb_docs = search_doc_count(SEARCH_ENDPOINT, SEARCH_ADMIN_KEY, SEARCH_INDEX) if (SEARCH_ENDPOINT and SEARCH_ADMIN_KEY) else None
with colB:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    doc_val = "—" if kb_docs is None else f"{kb_docs:,}"
    st.markdown(f'<div class="kp">📚 {doc_val}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpsub">Docs in "{SEARCH_INDEX}"</div>', unsafe_allow_html=True)
    if kb_docs is None:
        st.caption("Set SEARCH_ENDPOINT & SEARCH_ADMIN_KEY to enable.")
    st.markdown('</div>', unsafe_allow_html=True)

# Agent health
AGENT_ENDPOINT = get_secret("AGENT_ENDPOINT")
AGENT_API_KEY = get_secret("AGENT_API_KEY")
AGENT_ID = get_secret("AZURE_AGENT_ID")
agent_ok = bool(AGENT_ENDPOINT and (AGENT_API_KEY or get_secret("AZURE_CLIENT_ID")))
with colC:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="kp">🤖 {"OK" if agent_ok else "—"}</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpsub">Agent connectivity</div>', unsafe_allow_html=True)
    if not agent_ok:
        st.caption("Set AGENT_ENDPOINT and either AGENT_API_KEY or AAD creds.")
    st.markdown('</div>', unsafe_allow_html=True)

# Uptime-ish (local clock)
with colD:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="kp">⏱️ {time.strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpsub">Server time (UTC±)</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------
# Quick Actions → opens Ask Agent with prefilled prompts
# ---------------------------------------------
st.subheader("⚡ Quick Actions")
qa1, qa2, qa3, qa4 = st.columns(4)
def goto_ask_agent(prefill: str):
    push_recent(prefill)
    st.session_state["prefill_question"] = prefill
    st.switch_page("app/pages/Ask_Agent.py")

if qa1.button("Summarize top incidents"):
    goto_ask_agent("Summarize the top 5 incidents in the last 24 hours and rank by severity. Cite sources.")
if qa2.button("Flood guidance (coastal city)"):
    goto_ask_agent("Provide flood evacuation guidance for a coastal city with heavy rainfall forecast. Cite sources.")
if qa3.button("Wildfire proximity alert"):
    goto_ask_agent("Given a wildfire near San Jose, what are recommended actions within 10km? Cite sources.")
if qa4.button("Earthquake safety steps"):
    goto_ask_agent("List immediate earthquake safety steps for a residential building. Cite sources.")

st.markdown("---")

# ---------------------------------------------
# Live Incidents (table preview)
# ---------------------------------------------
st.subheader("🛰️ Live Incidents (USGS snapshot)")
if quakes:
    # Small, readable table
    view = [{
        "When": fmt_ts(q["time_ms"]),
        "Magnitude": q["magnitude"],
        "Title": q["title"],
        "Link": q["url"]
    } for q in sorted(quakes, key=lambda x: (x["magnitude"] or 0), reverse=True)[:12]]
    st.dataframe(view, use_container_width=True, height=300)
    st.caption("Source: USGS (updated ~5 min). See the Dashboard map for geospatial view.")
else:
    st.info("No live data fetched yet (or network blocked).")

st.markdown("---")

# ---------------------------------------------
# Recent Activity (local session)
# ---------------------------------------------
st.subheader("📝 Recent Activity")
recent = st.session_state.get("recent_questions", [])
if recent:
    for i, q in enumerate(recent, 1):
        st.markdown(f"{i}. {q}")
else:
    st.caption("Ask a question on the **Ask Agent** page and it will appear here.")

# ---------------------------------------------
# System Health (friendly checks)
# ---------------------------------------------
with st.expander("🔧 System Health"):
    rows = [
        ("AGENT_ENDPOINT", bool(AGENT_ENDPOINT)),
        ("AGENT_API_KEY or AAD creds", bool(AGENT_API_KEY or get_secret("AZURE_CLIENT_ID"))),
        ("SEARCH_ENDPOINT", bool(SEARCH_ENDPOINT)),
        ("SEARCH_ADMIN_KEY", bool(SEARCH_ADMIN_KEY)),
        ("SEARCH_INDEX", bool(SEARCH_INDEX)),
        ("AOAI_ENDPOINT", bool(get_secret("AOAI_ENDPOINT"))),
        ("AOAI_API_KEY", bool(get_secret("AOAI_API_KEY"))),
    ]
    st.write("| Setting | Present? |")
    st.write("|---|---|")
    for k, ok in rows:
        st.write(f"| `{k}` | {'✅' if ok else '❌'} |")

st.caption(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
