from uuid import uuid4
from datetime import datetime
import chromadb
from openai import OpenAI
client = OpenAI()

def embed_text(text: str) -> list[float]:
    res = client.embeddings.create(
        model="text-embedding-3-small",
        dimensions=384,
        input=text
    )
    return res.data[0].embedding

chroma_client = chromadb.Client()
collection = chroma_client.create_collection("image_pairs")

def upsert_pair(pair_id: str, vector: list[float], meta: dict):
    collection.upsert(
        ids=[pair_id],
        embeddings=[vector],
        metadatas=[meta]
    )

def query_by_text(query: str, k: int = 3):
    return collection.query(query_texts=[query], n_results=k)

def store_image_desc(image_path: str, description: str):
    pair_id = uuid4().hex
    vec = embed_text(description)
    meta = {
        "image_path": image_path,
        "description": description,
        "added_at": datetime.utcnow().isoformat()
    }
    upsert_pair(pair_id, vec, meta)
    return pair_id