# import os
# from azure.core.credentials import AzureKeyCredential
# from azure.search.documents.indexes import SearchIndexClient
# from azure.search.documents.indexes.models import (
#     SearchIndex, SimpleField, SearchField, SearchFieldDataType,
#     VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
#     SemanticSettings, SemanticConfiguration, SemanticField, PrioritizedFields
# )

# endpoint = os.environ["SEARCH_ENDPOINT"]
# key = os.environ["SEARCH_ADMIN_KEY"]
# index_name = os.environ.get("SEARCH_INDEX", "disaster-knowledge")

# index_client = SearchIndexClient(endpoint, AzureKeyCredential(key))

# # Vector config
# vector_search = VectorSearch(
#     algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
#     profiles=[VectorSearchProfile(name="vec-profile", algorithm_configuration_name="hnsw")]
# )

# # Semantic config
# semantic = SemanticSettings(
#     configurations=[
#         SemanticConfiguration(
#             name="sem-config",
#             prioritized_fields=PrioritizedFields(
#                 title_field=SemanticField(field_name="title"),
#                 content_fields=[SemanticField(field_name="content")],
#                 keywords_fields=[SemanticField(field_name="category")]
#             )
#         )
#     ]
# )

# fields = [
#     SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
#     SimpleField(name="source", type=SearchFieldDataType.String, filterable=True, facetable=True),
#     SimpleField(name="title", type=SearchFieldDataType.String, searchable=True, filterable=True),
#     SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
#     SimpleField(name="category", type=SearchFieldDataType.String, searchable=True, filterable=True, facetable=True),
#     # optional geo point if you want map-aware answers later
#     # SimpleField(name="location", type=SearchFieldDataType.GeographyPoint, filterable=True, facetable=True),

#     # Vector field (1536 for text-embedding-3-large; adjust to your embedding size)
#     SearchField(
#         name="contentVector",
#         type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
#         searchable=True,
#         vector_search_dimensions=3072,   # 3072 for text-embedding-3-large, 1536 for ada-002
#         vector_search_profile_name="vec-profile",
#     ),
# ]

# index = SearchIndex(
#     name=index_name,
#     fields=fields,
#     vector_search=vector_search,
#     semantic_settings=semantic
# )

# # Create or replace
# try:
#     index_client.delete_index(index_name)
# except Exception:
#     pass

# index_client.create_index(index)
# print(f"Created index '{index_name}' with semantic + vector settings.")

# scripts/create_search_index.py
# import os
# from dotenv import load_dotenv
# load_dotenv()

# from azure.core.credentials import AzureKeyCredential
# from azure.search.documents.indexes import SearchIndexClient
# from azure.search.documents.indexes.models import (
#     SearchIndex, SimpleField, SearchField, SearchFieldDataType,
#     VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile
# )

# # Optional semantic imports (only in newer SDKs)
# SEMANTIC_SUPPORTED = True
# try:
#     from azure.search.documents.indexes.models import (
#         SemanticSettings, SemanticConfiguration, SemanticField, PrioritizedFields
#     )
# except Exception:
#     SEMANTIC_SUPPORTED = False

# endpoint = os.environ["SEARCH_ENDPOINT"]
# key = os.environ["SEARCH_ADMIN_KEY"]
# index_name = os.environ.get("SEARCH_INDEX", "disaster-knowledge")

# # Embedding dimension: 3072 for text-embedding-3-large; 1536 for ada-002
# VECTOR_DIM = int(os.getenv("VECTOR_DIM", "3072"))

# index_client = SearchIndexClient(endpoint, AzureKeyCredential(key))

# vector_search = VectorSearch(
#     algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
#     profiles=[VectorSearchProfile(name="vec-profile", algorithm_configuration_name="hnsw")]
# )

# fields = [
#     SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
#     SimpleField(name="source", type=SearchFieldDataType.String, filterable=True, facetable=True),
#     SimpleField(name="title", type=SearchFieldDataType.String, searchable=True, filterable=True),
#     SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
#     SimpleField(name="category", type=SearchFieldDataType.String, searchable=True, filterable=True, facetable=True),
#     SearchField(
#         name="contentVector",
#         type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
#         searchable=True,
#         vector_search_dimensions=VECTOR_DIM,
#         vector_search_profile_name="vec-profile",
#     ),
# ]

# kwargs = dict(name=index_name, fields=fields, vector_search=vector_search)

# if SEMANTIC_SUPPORTED:
#     semantic_settings = SemanticSettings(
#         configurations=[
#             SemanticConfiguration(
#                 name="sem-config",
#                 prioritized_fields=PrioritizedFields(
#                     title_field=SemanticField(field_name="title"),
#                     content_fields=[SemanticField(field_name="content")],
#                     keywords_fields=[SemanticField(field_name="category")],
#                 ),
#             )
#         ]
#     )
#     kwargs["semantic_settings"] = semantic_settings

# # Create or replace index
# try:
#     index_client.delete_index(index_name)
# except Exception:
#     pass

# index = SearchIndex(**kwargs)
# index_client.create_index(index)

# print(f"Created index '{index_name}' "
#       f"with vector dim={VECTOR_DIM} "
#       f"and semantic={'ON' if SEMANTIC_SUPPORTED else 'OFF (SDK too old)'}.")

# if not SEMANTIC_SUPPORTED:
#     print("Note: To enable Semantic Ranker, upgrade azure-search-documents>=11.6.0 "
#           "and/or enable it in the Azure Portal (Search service → Settings → Semantic ranker).")
# scripts/create_search_index.py
import os
from dotenv import load_dotenv
load_dotenv()

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile
)

# --- Detect semantic API surface (new vs old) ---
SEMANTIC_MODE = None  # "new" | "old" | None
try:
    # Newer SDK surface (>= 11.6.0)
    from azure.search.documents.indexes.models import (
        SemanticSettings, SemanticConfiguration, SemanticField, PrioritizedFields
    )
    SEMANTIC_MODE = "new"
except Exception:
    try:
        # Older SDK surface
        from azure.search.documents.indexes.models import (
            SemanticSearch, SemanticConfiguration, SemanticField, SemanticPrioritizedFields
        )
        SEMANTIC_MODE = "old"
    except Exception:
        SEMANTIC_MODE = None

endpoint = os.environ["SEARCH_ENDPOINT"]
key = os.environ["SEARCH_ADMIN_KEY"]
index_name = os.environ.get("SEARCH_INDEX", "disaster-knowledge")

# Embedding dimension:
# - 3072 for text-embedding-3-large
# - 1536 for text-embedding-ada-002
VECTOR_DIM = int(os.getenv("VECTOR_DIM", "3072"))

index_client = SearchIndexClient(endpoint, AzureKeyCredential(key))

# ---- Vector search config ----
vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
    profiles=[VectorSearchProfile(name="vec-profile", algorithm_configuration_name="hnsw")]
)

# ---- Fields ----
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
    SimpleField(name="source", type=SearchFieldDataType.String, filterable=True, facetable=True),
    SimpleField(name="title", type=SearchFieldDataType.String, searchable=True, filterable=True),
    SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
    SimpleField(name="category", type=SearchFieldDataType.String, searchable=True, filterable=True, facetable=True),
    SearchField(
        name="contentVector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=VECTOR_DIM,
        vector_search_profile_name="vec-profile",
    ),
]

# ---- Build index args ----
kwargs = dict(name=index_name, fields=fields, vector_search=vector_search)

# ---- Add semantic configuration depending on SDK flavor ----
SEM_CONFIG_NAME = "sem-config"
if SEMANTIC_MODE == "new":
    # Newer SDK types
    semantic_settings = SemanticSettings(
        configurations=[
            SemanticConfiguration(
                name=SEM_CONFIG_NAME,
                prioritized_fields=PrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    content_fields=[SemanticField(field_name="content")],
                    keywords_fields=[SemanticField(field_name="category")],
                ),
            )
        ]
    )
    kwargs["semantic_settings"] = semantic_settings

elif SEMANTIC_MODE == "old":
    # Older SDK types
    semantic_search = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name=SEM_CONFIG_NAME,
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    content_fields=[SemanticField(field_name="content")],
                    keywords_fields=[SemanticField(field_name="category")],
                ),
            )
        ]
    )
    kwargs["semantic_search"] = semantic_search

# ---- Create or replace index ----
try:
    index_client.delete_index(index_name)
except Exception:
    pass

index = SearchIndex(**kwargs)
index_client.create_index(index)

print(
    f"Created index '{index_name}' with vector dim={VECTOR_DIM} "
    f"and semantic mode={'NEW' if SEMANTIC_MODE=='new' else ('OLD' if SEMANTIC_MODE=='old' else 'OFF')}. "
    "Note: service-level Semantic Ranker must be enabled in the portal."
)
