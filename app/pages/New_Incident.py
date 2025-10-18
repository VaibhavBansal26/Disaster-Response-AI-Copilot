import streamlit as st
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]  # repo root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.utils.agent_client import call_agent

st.title("🆕 New Incident")

with st.form("new_incident"):
    txt = st.text_area("Incident description", placeholder="e.g., Fast-moving wildfire near Sacramento with strong winds and smoke…", height=150)
    dtype = st.selectbox("Disaster type (optional)", ["", "flood", "wildfire", "storm"])
    loc = st.text_input("Location (optional)", placeholder="City, State or GPS")
    submitted = st.form_submit_button("Analyze & Recommend")

if submitted:
    if not txt.strip():
        st.warning("Please provide an incident description.")
    else:
        prompt = "Classify severity and provide top actions with citations. Incident: "
        if dtype: prompt += f"(type: {dtype}) "
        if loc: prompt += f"(location: {loc}) "
        prompt += txt
        with st.spinner("Contacting agent..."):
            res = call_agent(prompt)
        if "error" in res:
            st.error(res["error"])
        else:
            data = res.get("json", {})
            out = data.get(st.session_state.get("resp_field","output")) or "No response field found."
            st.markdown("### Response")
            st.markdown(out)
