import os, streamlit as st
from dotenv import load_dotenv; load_dotenv()
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient

st.set_page_config(page_title="Knowledge Search", page_icon="🧭")
st.title("🧭 Knowledge Search (Semantic)")

ep = os.environ["SEARCH_ENDPOINT"]; key = os.environ["SEARCH_ADMIN_KEY"]
index = os.getenv("SEARCH_INDEX","disaster-knowledge")

idxc = SearchIndexClient(ep, AzureKeyCredential(key))
idx = idxc.get_index(index)
configs = (idx.semantic_search.configurations if idx.semantic_search else []) or []
sem_name = configs[0].name if configs else None

client = SearchClient(ep, index, AzureKeyCredential(key))
q = st.text_input("Query", "urban flood evacuation steps")

if st.button("Search", type="primary"):
    if sem_name:
        res = client.search(search_text=q, query_type="semantic",
                            semantic_configuration_name=sem_name,
                            query_language="en-us",
                            select=["title","source","content"], top=5)
    else:
        st.warning("No semantic config found. Showing standard results.")
        res = client.search(search_text=q, select=["title","source","content"], top=5)

    for r in res:
        st.markdown(f"**{r['title']}**  \n`{r['source']}`")
        st.write((r.get("content") or "")[:600] + "…")
        st.divider()
