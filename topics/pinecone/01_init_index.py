"""
Exercise: Pinecone — Create a serverless index
Connect with a Pinecone client and create (idempotently) a serverless index
with a fixed dimension and similarity metric. Bring-your-own vectors: you choose
the dimension to match whatever embedding model produced your vectors elsewhere.
"""

import time

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec, Index, GrpcIndex

load_dotenv()  # expects PINECONE_API_KEY in the environment

INDEX_NAME = "my-index"
DIMENSION = 1536  # match your embedding model
METRIC = "cosine"  # "cosine" / "dotproduct" / "euclidean"


def get_or_create_index(pc: Pinecone, index_name: str) -> Index | GrpcIndex:
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=DIMENSION,
            metric=METRIC,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        # create_index returns before the index is ready; wait for it.
        while not pc.describe_index(index_name).status.ready:
            time.sleep(1)
    return pc.index(index_name)


pc = Pinecone()


if __name__ == "__main__":
    index = get_or_create_index(pc, INDEX_NAME)
    print(pc.describe_index(INDEX_NAME).host)
