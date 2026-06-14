"""
Exercise: Pinecone — Upsert vectors with metadata
Push precomputed embedding vectors (bring-your-own) into an index, each with an
id and a metadata dict. Upserts are idempotent by id, so re-running overwrites.
"""

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone()

# TODO: get a handle with index = pc.Index("<your-index-name>"); build a few records
#       like {"id": "doc-1", "values": [...floats...], "metadata": {"text": ...}};
#       call index.upsert(vectors=records, namespace="demo") and print the result count


if __name__ == "__main__":
    pass
