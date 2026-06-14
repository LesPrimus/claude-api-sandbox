"""
Exercise: Pinecone — Query top-k nearest neighbors
Given a precomputed query vector (same dimension as what you upserted), retrieve
the k most similar records and read their ids, scores, and metadata.
"""

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone()

# TODO: index = pc.Index("<your-index-name>"); call index.query(vector=[...],
#       top_k=3, namespace="demo", include_metadata=True); iterate result.matches
#       and print each match.id, match.score, and match.metadata


if __name__ == "__main__":
    pass
