"""
Exercise: Pinecone — Upsert vectors with metadata
Push precomputed embedding vectors (bring-your-own) into an index, each with an
id and a metadata dict. Upserts are idempotent by id, so re-running overwrites.
"""

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()  # expects PINECONE_API_KEY and OPENAI_API_KEY

INDEX_NAME = "my-index"
EMBED_MODEL = "text-embedding-3-small"  # 1536 dims, matches the index from 01

pc = Pinecone()
oai = OpenAI()


def embed(texts: list[str]) -> list[list[float]]:
    resp = oai.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


if __name__ == "__main__":
    index = pc.index(INDEX_NAME)

    docs = {
        "doc-1": "Pinecone is a managed vector database.",
        "doc-2": "OpenAI provides text embedding models.",
        "doc-3": "Cosine similarity compares vector direction.",
    }

    vectors = embed(list(docs.values()))
    records = [
        {"id": doc_id, "values": values, "metadata": {"text": text}}
        for (doc_id, text), values in zip(docs.items(), vectors)
    ]

    result = index.upsert(vectors=records, namespace="demo")
    print(f"upserted {result.upserted_count} vectors")
