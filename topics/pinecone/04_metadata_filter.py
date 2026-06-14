"""
Exercise: Pinecone — Filter queries by metadata
Narrow a top-k search to only records whose metadata matches a filter, using
Pinecone's Mongo-style operators ($eq, $in, $gte, ...). Useful for scoping a
retrieval to one source, language, or date range before ranking by similarity.
"""

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone()

# TODO: index = pc.Index("<your-index-name>"); run index.query(vector=[...], top_k=3,
#       filter={"source": {"$eq": "docs"}, "year": {"$gte": 2024}},
#       include_metadata=True); confirm every returned match satisfies the filter


if __name__ == "__main__":
    pass
