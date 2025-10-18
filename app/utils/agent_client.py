# import os, time
# import streamlit as st
# from azure.identity import DefaultAzureCredential
# from azure.ai.projects import AIProjectClient
# from azure.ai.agents.models import ListSortOrder

# # We build a single, cached client per session.
# @st.cache_resource(show_spinner=False)
# def _get_project_client(endpoint: str):
#     cred = DefaultAzureCredential()
#     return AIProjectClient(credential=cred, endpoint=endpoint)

# def _resolve_agent(project, agent_id: str = "", agent_name: str = ""):
#     # Try ID first (your snippet uses an ID like "asst_...")
#     if agent_id:
#         try:
#             return project.agents.get_agent(agent_id)
#         except Exception as e:
#             st.warning(f"Could not get agent by ID: {e}")
#     # Fallback: try by name
#     if agent_name:
#         try:
#             # List & match by name (exact)
#             for a in project.agents.list():
#                 if (getattr(a, "name", "") or "").strip() == agent_name.strip():
#                     return a
#             raise ValueError(f"No agent found with name '{agent_name}'")
#         except Exception as e:
#             st.error(f"Could not resolve agent by name: {e}")
#             raise
#     raise ValueError("No valid agent ID or name provided.")

# def call_agent(prompt: str) -> dict:
#     """
#     Uses your Azure AI Projects SDK flow:
#       - create a thread
#       - add user message
#       - create_and_process a run
#       - read ordered messages and return the assistant reply
#     Returns: {"text": "..."} on success or {"error": "..."} on error.
#     """
#     endpoint = st.session_state.get("proj_endpoint") or os.getenv("AGENT_ENDPOINT","").strip()
#     agent_id = st.session_state.get("agent_id") or os.getenv("AZURE_AGENT_ID","").strip()
#     agent_name = st.session_state.get("agent_name") or os.getenv("AGENT_NAME","").strip()

#     if not endpoint or not (agent_id or agent_name):
#         return {"error": "Missing project endpoint or agent id/name. Fill them in the sidebar or .env."}

#     try:
#         project = _get_project_client(endpoint)
#         agent = _resolve_agent(project, agent_id=agent_id, agent_name=agent_name)

#         # Create a thread
#         thread = project.agents.threads.create()

#         # Add user message
#         project.agents.messages.create(
#             thread_id=thread.id,
#             role="user",
#             content=prompt
#         )

#         # Run (create_and_process per your snippet)
#         run = project.agents.runs.create_and_process(
#             thread_id=thread.id,
#             agent_id=agent.id
#         )

#         if run.status == "failed":
#             return {"error": f"Run failed: {run.last_error}"}

#         # List messages in ascending order and return the last assistant message
#         messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

#         last_assistant_text = None
#         for m in messages:
#             if m.role == "assistant" and m.text_messages:
#                 last_assistant_text = m.text_messages[-1].text.value

#         if not last_assistant_text:
#             # Fallback: show last message if any
#             for m in reversed(list(messages)):
#                 if m.text_messages:
#                     last_assistant_text = m.text_messages[-1].text.value
#                     break

#         if not last_assistant_text:
#             return {"error": "No assistant response returned."}

#         # For compatibility with the rest of the app, return under 'json'->'output'
#         return {"json": {"output": last_assistant_text}}

#     except Exception as e:
#         return {"error": str(e)}

# app/utils/agent_client.py (SDK mode only)
# import os
# import streamlit as st
# from azure.identity import DefaultAzureCredential
# from azure.ai.projects import AIProjectClient
# from azure.ai.agents.models import ListSortOrder

# @st.cache_resource(show_spinner=False)
# def _project_client():
#     endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT") or os.getenv("AGENT_ENDPOINT")  # keep one source of truth
#     if not endpoint:
#         raise RuntimeError("AZURE_AI_PROJECT_ENDPOINT/AGENT_ENDPOINT is not set")
#     cred = DefaultAzureCredential()  # will use your SP or az login
#     return AIProjectClient(credential=cred, endpoint=endpoint)

# def call_agent(prompt: str) -> dict:
#     """Create a thread, add user message, run the agent, return assistant text."""
#     endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT") or os.getenv("AGENT_ENDPOINT")
#     agent_id = os.getenv("AZURE_AGENT_ID")
#     if not endpoint or not agent_id:
#         return {"error": "Missing AZURE_AI_PROJECT_ENDPOINT/AGENT_ENDPOINT or AZURE_AGENT_ID."}

#     try:
#         project = _project_client()
#         # IMPORTANT: resolve by ID only; no list-by-name branch
#         agent = project.agents.get_agent(agent_id)

#         thread = project.agents.threads.create()
#         project.agents.messages.create(thread_id=thread.id, role="user", content=prompt)

#         run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
#         if run.status == "failed":
#             return {"error": f"Run failed: {run.last_error}"}

#         messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
#         for m in reversed(list(messages)):
#             if m.role == "assistant" and getattr(m, "text_messages", None):
#                 return {"answer": m.text_messages[-1].text.value}

#         return {"error": "No assistant response returned."}

#     except Exception as e:
#         return {"error": str(e)}

# app/utils/agent_client.py
import os
from functools import lru_cache
from typing import Dict, Optional

# from dotenv import load_dotenv
# load_dotenv()  # ensure .env is loaded for local runs

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder


REQUIRED_VARS = ["AGENT_ENDPOINT", "AZURE_AGENT_ID"]
for v in REQUIRED_VARS:
    if not os.getenv(v):
        raise RuntimeError(f"Missing required env var: {v}")

# If you are using a Service Principal locally, make sure these are in .env too:
# AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET


@lru_cache(maxsize=1)
def _project_client() -> AIProjectClient:
    """
    Cached Projects client using DefaultAzureCredential.
    Works with az login, service principal, or managed identity.
    """
    endpoint = os.environ["AGENT_ENDPOINT"]
    cred = DefaultAzureCredential()
    return AIProjectClient(credential=cred, endpoint=endpoint)


def _last_assistant_text(thread_id: str) -> Optional[str]:
    """
    Returns the most recent assistant text for a thread, if any.
    """
    messages = _project_client().agents.messages.list(
        thread_id=thread_id, order=ListSortOrder.ASCENDING
    )
    # iterate from the end to get the last assistant message quickly
    for m in reversed(list(messages)):
        if m.role == "assistant" and getattr(m, "text_messages", None):
            return m.text_messages[-1].text.value
    return None


def call_agent(prompt: str) -> Dict[str, str]:
    """
    High-level helper your Streamlit page can call.
    Returns a dict with either {"response": "..."} or {"error": "..."}.
    """
    try:
        agent_id = os.environ["AZURE_AGENT_ID"]
        client = _project_client()

        # Create thread & add user message
        thread = client.agents.threads.create()
        client.agents.messages.create(
            thread_id=thread.id, role="user", content=prompt
        )

        # Run and wait
        run = client.agents.runs.create_and_process(
            thread_id=thread.id, agent_id=agent_id
        )

        if run.status == "failed":
            return {"error": f"Agent run failed: {run.last_error}"}

        # Extract the assistant's final text
        answer = _last_assistant_text(thread.id)
        if not answer:
            return {"error": "No assistant response returned."}

        return {"response": answer}

    # Surface permission/SDK issues cleanly in the UI
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
