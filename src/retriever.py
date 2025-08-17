# File: retriever.py
# Description: Defines the EfficiencyRetriever class for retrieving energy efficiency suggestions
# based on code snippets using semantic search. Supports both JSON-based storage and Qdrant
# vector database, with conditional imports to avoid Qdrant dependencies in development.
#
# TODO: SSL support for Qdrant connections in production.

import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class EfficiencyRetriever:
    def __init__(self, use_db: bool = False):
        """
        Initialize the EfficiencyRetriever with either JSON or Qdrant storage.

        :param use_db: If True, use Qdrant vector database; if False, use JSON file.
        """
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.use_db = use_db
        if use_db:
            from qdrant_client import QdrantClient
            from qdrant_client import models
            self.client = QdrantClient(
                url=os.getenv("QDRANT_URL"),
                api_key=os.getenv("QDRANT_API_KEY")
            )
            self.models = models
            self.collection_name = "efficiency_observations"
            # Assume collection is created/migrated; no auto-create here to avoid errors
        else:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'efficiency-data.json')
            with open(data_path, 'r') as f:
                self.data = json.load(f)
            self.vectors = np.array([self.model.encode(d['observation']) for d in self.data])

    def search(self, query: str, language: str, top_k: int = 5) -> list[dict]:
        """
        Search for energy efficiency suggestions relevant to the provided code snippet.

        :param query: The code snippet to analyze.
        :param language: The programming language of the code (e.g., 'java', 'python', 'javascript').
        :param top_k: Maximum number of suggestions to return.
        :return: List of dictionaries containing efficiency observations.
        """
        query_vec = self.model.encode(query)
        if self.use_db:
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vec.tolist(),
                query_filter=self.models.Filter(
                    must=[
                        self.models.FieldCondition(
                            key="language",
                            match=self.models.MatchValue(value=language)
                        )
                    ]
                ),
                limit=top_k
            )
            return [hit.payload for hit in hits if hit.score > 0.2]
        else: # Perform in-memory semantic search using preloaded vectors from JSON data
            indices = [i for i, d in enumerate(self.data) if d['language'] == language]

            if not indices:
                return []
            
            # Get the pre-computed vector embeddings of all "observation" texts from the local JSON file.
            lang_vectors = self.vectors[indices]

            # Compute cosine similarity between the query vector and each language-specific vector
            sims = np.dot(lang_vectors, query_vec) / (np.linalg.norm(lang_vectors, axis=1) * np.linalg.norm(query_vec))
            # Get indices of the top_k most similar entries, sorted in descending order of similarity
            top_indices = np.argsort(sims)[-top_k:][::-1]

            # Retrieve the top matching observations from the data if similarity exceeds threshold
            results = [self.data[indices[i]] for i in top_indices if sims[i] > 0.2]

            return results
