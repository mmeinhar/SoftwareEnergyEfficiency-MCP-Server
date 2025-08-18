# File: migrate.py
# Description: Migrates energy efficiency data from JSON to Qdrant vector database.
# Creates or updates the Qdrant collection with embeddings for semantic search.

import os
import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
model = SentenceTransformer('all-MiniLM-L6-v2')
collection_name = "efficiency_observations"

# Check if collection exists, create if not
if not client.has_collection(collection_name):
    """
    Create a new Qdrant collection for storing efficiency observations if it doesn't exist.

    Uses COSINE distance and the embedding size of the sentence transformer model.
    """
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=384,  # Dimension of all-MiniLM-L6-v2
            distance=models.Distance.COSINE
        )
    )

# Load data
data_path = os.path.join(os.path.dirname(__file__), '../..', 'data', 'efficiency_data.json')
with open(data_path, 'r') as f:
    data = json.load(f)

# Prepare points
points = [
    models.PointStruct(
        id=str(i),
        vector=model.encode(d['observation']).tolist(),
        payload=d
    ) for i, d in enumerate(data)
]

# Upsert (will insert or update)
client.upsert(
    collection_name=collection_name,
    points=points
)

print(f"Migrated {len(points)} points to Qdrant.")
