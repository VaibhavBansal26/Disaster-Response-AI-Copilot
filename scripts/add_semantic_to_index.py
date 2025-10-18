# # scripts/add_semantic_to_index.py
# import os
# from dotenv import load_dotenv
# load_dotenv()

# from azure.core.credentials import AzureKeyCredential
# from azure.search.documents.indexes import SearchIndexClient
# # from azure.search.documents.indexes.models import (
# #     SemanticConfiguration, SemanticField, PrioritizedFields
# # )
# SEMANTIC_SUPPORTED = True
# try:
#     from azure.search.documents.indexes.models import (
#         SSemanticConfiguration, SemanticField, PrioritizedFields
#     )
# except Exception:
#     SEMANTIC_SUPPORTED = False
# endpoint = os.environ["SEARCH_ENDPOINT"]
# key = os.environ["SEARCH_ADMIN_KEY"]
# index_name = os.environ.get("SEARCH_INDEX", "disaster-knowledge")

# client = SearchIndexClient(endpoint, AzureKeyCredential(key))

# idx = client.get_index(index_name)

# # Add/replace a semantic configuration named "sem-config"
# idx.semantic_settings = SemanticSettings(
#     configurations=[
#         SemanticConfiguration(
#             name="sem-config",
#             prioritized_fields=PrioritizedFields(
#                 title_field=SemanticField(field_name="title"),
#                 content_fields=[SemanticField(field_name="content")],
#                 keywords_fields=[SemanticField(field_name="category")],
#             )
#         )
#     ]
# )

# client.create_or_update_index(idx)
# print(f"Index '{index_name}' updated with semantic configuration 'sem-config'.")

# scripts/add_semantic_to_index.py
import os
from dotenv import load_dotenv
load_dotenv()

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)

SEARCH_ENDPOINT = os.environ["SEARCH_ENDPOINT"]
SEARCH_ADMIN_KEY = os.environ["SEARCH_ADMIN_KEY"]
INDEX_NAME = os.environ.get("SEARCH_INDEX", "disaster-knowledge")

client = SearchIndexClient(SEARCH_ENDPOINT, AzureKeyCredential(SEARCH_ADMIN_KEY))

# Our index field names (from your create script): title, content, category
SEM_CONFIG_NAME = "sem-config"

idx = client.get_index(INDEX_NAME)

new_semantic_config = SemanticConfiguration(
    name=SEM_CONFIG_NAME,
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="title"),
        keywords_fields=[SemanticField(field_name="category")],
        content_fields=[SemanticField(field_name="content")],
    ),
)

# Add or append semantic config
if getattr(idx, "semantic_search", None) is None:
    idx.semantic_search = SemanticSearch(configurations=[new_semantic_config])
else:
    if not any(c.name == SEM_CONFIG_NAME for c in idx.semantic_search.configurations or []):
        idx.semantic_search.configurations.append(new_semantic_config)

# Update index
client.create_or_update_index(idx)

# Show what’s configured
updated = client.get_index(INDEX_NAME)
print("Semantic configurations:")
if updated.semantic_search and updated.semantic_search.configurations:
    for c in updated.semantic_search.configurations:
        print(f" - {c.name}")
        pf = c.prioritized_fields
        if pf.title_field:
            print(f"   title:   {pf.title_field.field_name}")
        if pf.keywords_fields:
            print(f"   keywords:{', '.join(k.field_name for k in pf.keywords_fields)}")
        if pf.content_fields:
            print(f"   content: {', '.join(k.field_name for k in pf.content_fields)}")
    print("✅ Semantic configuration added/updated.")
else:
    print("❌ No semantic configurations found.")
