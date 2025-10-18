# scripts/show_index_status.py
import os
from dotenv import load_dotenv
load_dotenv()

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient

ep   = os.environ["SEARCH_ENDPOINT"]
key  = os.environ["SEARCH_ADMIN_KEY"]
name = os.getenv("SEARCH_INDEX","disaster-knowledge")

idxc = SearchIndexClient(ep, AzureKeyCredential(key))
idx  = idxc.get_index(name)

# SDK flavor detection
mode = "none"
if getattr(idx, "semantic_settings", None):
    mode = "new"
elif getattr(idx, "semantic_search", None):
    mode = "old"

print(f"Index: {name}")
print(f"Fields: {[f.name for f in idx.fields]}")
if mode == "new":
    cfgs = idx.semantic_settings.configurations or []
    print("Semantic mode: NEW; configs:", [c.name for c in cfgs])
elif mode == "old":
    cfgs = (idx.semantic_search.configurations or [])
    print("Semantic mode: OLD; configs:", [c.name for c in cfgs])
else:
    print("Semantic mode: NONE")

sc = SearchClient(ep, name, AzureKeyCredential(key))
try:
    print("Document count:", sc.get_document_count())
except Exception as e:
    print("Document count error:", e)
