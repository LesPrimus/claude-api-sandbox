"""
Exercise: Pinecone — Create a serverless index
Connect with a Pinecone client and create (idempotently) a serverless index
with a fixed dimension and similarity metric. Bring-your-own vectors: you choose
the dimension to match whatever embedding model produced your vectors elsewhere.
"""

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec  # noqa: F401

load_dotenv()  # expects PINECONE_API_KEY in the environment

pc = Pinecone()

# TODO: pick an index name, dimension, and metric ("cosine"/"dotproduct"/"euclidean");
#       skip creation if pc.has_index(name) already, otherwise pc.create_index(...)
#       with a ServerlessSpec(cloud=..., region=...); print the resulting index host


if __name__ == "__main__":
    pass
