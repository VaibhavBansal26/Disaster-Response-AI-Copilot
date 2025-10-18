import sys, os, pathlib, streamlit as st
st.title("Debug")
st.write("CWD:", os.getcwd())
st.write("Repo root exists?:", pathlib.Path(__file__).resolve().parents[2].exists())
st.write("In sys.path?:", str(pathlib.Path(__file__).resolve().parents[2]) in sys.path)
st.write("sys.path:", sys.path)
try:
    import app, app.utils.agent_client as ac
    st.success("Imported app and app.utils.agent_client OK")
except Exception as e:
    st.error(f"Import failed: {e}")
