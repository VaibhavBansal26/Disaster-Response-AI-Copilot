# import json, streamlit as st
# from app.utils.agent_client import call_agent

# st.title("🧠 Ask Agent")

# if "chat" not in st.session_state:
#     st.session_state.chat = []

# for msg in st.session_state.chat:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# user_input = st.chat_input("Ask about floods, wildfires, or hurricanes (the agent will cite sources)")
# if user_input:
#     st.session_state.chat.append({"role":"user","content":user_input})
#     with st.chat_message("user"):
#         st.markdown(user_input)

#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             res = call_agent(user_input)
#         if "error" in res:
#             st.error(res["error"])
#         else:
#             data = res.get("json", {})
#             show_raw = st.toggle("Show raw response", value=False, key="rawtoggle")
#             if show_raw:
#                 st.json(data)
#             out = (
#                 data.get(st.session_state.get("resp_field","output"))
#                 or (data.get("choices",[{}])[0].get("message",{}).get("content") if isinstance(data.get("choices"), list) else None)
#                 or json.dumps(data, ensure_ascii=False, indent=2)
#             )
#             st.markdown(out)
#             st.session_state.chat.append({"role":"assistant","content":out})

# app/pages/ask_agent.py
import streamlit as st
# from dotenv import load_dotenv
# load_dotenv()  # load .env for local runs
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]  # repo root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.utils.agent_client import call_agent

st.set_page_config(page_title="Ask Agent", page_icon="🧠", layout="centered")
st.title("🧠 Ask Agent")

default_q = st.session_state.pop("prefill_question", "Summarize the latest disaster risks in my region.")
q = st.text_area("Your question", default_q, height=120)

with st.container():
    prompt = st.text_input(
        "Ask anything related to disasters (e.g., flood, wildfire, hurricane):",
        placeholder="What steps should be taken when a flood alert is issued in Houston?"
    )

    ask = st.button("Ask", type="primary", use_container_width=True)

if ask:
    if not prompt.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Contacting Azure AI Agent…"):
            res = call_agent(prompt)

        if "error" in res:
            st.error(res["error"])
        elif "response" in res:
            st.success("Response")
            st.write(res["response"])
        else:
            st.warning("No response received.")


# import streamlit as st
# from app.utils.agent_client import call_agent

# st.title("💬 Disaster Response Copilot")

# query = st.text_area("Ask the AI Agent", placeholder="e.g. What should I do in case of a flood near Buffalo?")

# if st.button("Ask Agent"):
#     with st.spinner("Contacting Azure AI Agent..."):
#         res = call_agent(query)

#     if "error" in res:
#         st.error(res["error"])
#     elif "answer" in res:
#         st.success("✅ Agent Response")
#         st.write(res["answer"])
#     else:
#         st.warning("No valid response received.")
