# # scripts/search_test.py
# import os
# from dotenv import load_dotenv
# load_dotenv()

# from azure.core.credentials import AzureKeyCredential
# from azure.search.documents import SearchClient
# from azure.search.documents.indexes import SearchIndexClient

# endpoint = os.environ["SEARCH_ENDPOINT"]
# key = os.environ["SEARCH_ADMIN_KEY"]
# index = os.environ.get("SEARCH_INDEX", "disaster-knowledge")

# idx_client = SearchIndexClient(endpoint, AzureKeyCredential(key))
# idx = idx_client.get_index(index)

# has_semantic = bool(getattr(idx, "semantic_settings", None) and idx.semantic_settings.configurations)
# client = SearchClient(endpoint, index, AzureKeyCredential(key))

# query = "steps during an urban flood evacuation"

# if has_semantic:
#     print("Semantic top results:")
#     results = client.search(
#         search_text=query,
#         query_type="semantic",
#         semantic_configuration_name=idx.semantic_settings.configurations[0].name,
#         query_language="en-us",
#         select=["title", "source", "content"],
#         top=5,
#     )
# else:
#     print("Semantic settings not found. Using standard search.")
#     results = client.search(
#         search_text=query,
#         select=["title", "source", "content"],
#         top=5,
#     )

# for r in results:
#     print("-", r["title"], "->", r["source"])

# scripts/search_test.py
# import os
# from dotenv import load_dotenv
# load_dotenv()

# from azure.core.credentials import AzureKeyCredential
# from azure.search.documents import SearchClient
# from azure.search.documents.indexes import SearchIndexClient

# endpoint = os.environ["SEARCH_ENDPOINT"]
# key = os.environ["SEARCH_ADMIN_KEY"]
# index = os.environ.get("SEARCH_INDEX", "disaster-knowledge")

# idx_client = SearchIndexClient(endpoint, AzureKeyCredential(key))
# idx = idx_client.get_index(index)

# client = SearchClient(endpoint, index, AzureKeyCredential(key))

# configs = (idx.semantic_search.configurations if idx.semantic_search else []) or []
# sem_name = configs[0].name if configs else None

# query = "steps during an urban flood evacuation"

# if sem_name:
#     print("Semantic top results (using", sem_name, "):")
#     results = client.search(
#         search_text=query,
#         query_type="semantic",
#         semantic_configuration_name=sem_name,
#         query_language="en-us",
#         select=["title", "source", "content"],
#         top=5,
#     )
# else:
#     print("Semantic config not found. Falling back to standard search.")
#     results = client.search(
#         search_text=query,
#         select=["title", "source", "content"],
#         top=5,
#     )

# for r in results:
#     print("-", r["title"], "->", r["source"])
# scripts/search_test.py
import os
from dotenv import load_dotenv
load_dotenv()

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient

endpoint = os.environ["SEARCH_ENDPOINT"]
key = os.environ["SEARCH_ADMIN_KEY"]
index = os.environ.get("SEARCH_INDEX", "disaster-knowledge")

idx_client = SearchIndexClient(endpoint, AzureKeyCredential(key))
idx = idx_client.get_index(index)

client = SearchClient(endpoint, index, AzureKeyCredential(key))

configs = (idx.semantic_search.configurations if idx.semantic_search else []) or []
sem_name = configs[0].name if configs else None

query = "steps during an urban flood evacuation"

if sem_name:
    print("Semantic top results (using", sem_name, "):")
    results = client.search(
        search_text=query,
        query_type="semantic",
        semantic_configuration_name=sem_name,
        query_language="en-us",
        select=["title", "source", "content"],
        top=5,
    )
else:
    print("Semantic config not found. Falling back to standard search.")
    results = client.search(
        search_text=query,
        select=["title", "source", "content"],
        top=5,
    )

for r in results:
    print("-", r["title"], "->", r["source"])
