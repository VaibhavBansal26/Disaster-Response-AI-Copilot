import os, uuid, glob, re
from typing import List
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI

from dotenv import load_dotenv
load_dotenv()

index_name = os.environ["SEARCH_INDEX"]
search = SearchClient(
    os.environ["SEARCH_ENDPOINT"],
    index_name,
    AzureKeyCredential(os.environ["SEARCH_ADMIN_KEY"])
)
aoai = AzureOpenAI(
    api_key=os.environ["AOAI_API_KEY"],
    api_version="2024-06-01",
    azure_endpoint=os.environ["AOAI_ENDPOINT"]
)
embed_deploy = os.environ["AOAI_EMBED_DEPLOYMENT"]

def chunk_text(text: str, max_tokens=700):
    # simple splitter by paragraphs
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) < 3000:  # rough char proxy for token budget
            cur += ("\n\n" + p) if cur else p
        else:
            chunks.append(cur)
            cur = p
    if cur:
        chunks.append(cur)
    return chunks

def embed(texts: List[str]) -> List[List[float]]:
    # batched embeddings
    resp = aoai.embeddings.create(model=embed_deploy, input=texts)
    return [d.embedding for d in resp.data]

def upsert_batch(batch):
    search.upload_documents(batch)

docs = []
for path in glob.glob("data/**/*.txt", recursive=True):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    chunks = chunk_text(raw)
    vecs = embed(chunks)
    base = os.path.basename(path)
    title = os.path.splitext(base)[0]
    for i, (content, vec) in enumerate(zip(chunks, vecs)):
        docs.append({
            "id": f"{uuid.uuid4()}",
            "source": path,
            "title": title,
            "category": "guideline",
            "content": content,
            "contentVector": vec
        })
        if len(docs) >= 1000:
            upsert_batch(docs); docs = []

if docs:
    upsert_batch(docs)

print("Ingestion complete.")
