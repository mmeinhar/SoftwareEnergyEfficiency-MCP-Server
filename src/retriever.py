# File: retriever.py
# Description: Defines the EfficiencyRetriever class for retrieving energy efficiency suggestions
# based on code snippets using semantic search. Supports both JSON-based storage and Qdrant
# vector database, with conditional imports to avoid Qdrant dependencies in development.
#
# TODO: Test the use_db=true use case
# TODO: SSL support for Qdrant connections in production.
# TODO: Evaluate the need for including the data file observation list to be further search filtered 
# by another data file called "language_components.json" with "language", "component", and "keyword". 
# For example, "{"language": "java", "component": "Loops", "keyword": "for"}". Test to see if this would
# further narrow down the observation list returned by the search without reducing associated observations. 
# This MCP server should not return an excess # of unecessary observations which would make the corresponding 
# GitHub Copilot LLM prompt too big or out of context, since these observations are added to that LLM query.
# 

import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class EfficiencyRetriever:
    def __init__(self, use_db: bool = False):
        """
        Initialize the EfficiencyRetriever with either JSON or Qdrant storage.

        :param use_db: If True, use Qdrant vector database; if False, use JSON file.
        :raises FileNotFoundError: If JSON file is not found when use_db is False.
        :raises ValueError: If JSON file is malformed or missing required fields.
        """
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.use_db = use_db
        if use_db:
            try:
                from qdrant_client import QdrantClient
                from qdrant_client import models
                self.client = QdrantClient(
                    url=os.getenv("QDRANT_URL"),
                    api_key=os.getenv("QDRANT_API_KEY")
                )
                self.models = models
                self.collection_name = "efficiency_observations"
                # Verify collection exists
                if not self.client.collection_exists(self.collection_name):
                    raise ValueError(f"Qdrant collection '{self.collection_name}' does not exist.")
            except ImportError:
                raise ImportError("Qdrant client is not installed. Install qdrant-client to use database mode.")
        else:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'efficiency-data.json')
            try:
                if not os.path.exists(data_path):
                    raise FileNotFoundError(f"JSON file not found at {data_path}")
                with open(data_path, 'r') as f:
                    self.data = json.load(f)
                # Validate JSON structure
                required_fields = {'language', 'component', 'observation'}
                for entry in self.data:
                    if not all(field in entry for field in required_fields):
                        raise ValueError(f"JSON entry missing required fields: {entry}")
                self.vectors = np.array([self.model.encode(d['observation']) for d in self.data])
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON file: {e}")

    def search(self, query: str, language: str, top_k: int = 5) -> list[dict]:
        """
        Search for energy efficiency suggestions relevant to the provided code snippet.

        :param query: The code snippet to analyze.
        :param language: The programming language of the code (e.g., 'java', 'python', 'javascript').
        :param top_k: Maximum number of suggestions to return.
        :return: List of dictionaries containing efficiency observations with fields 'language', 'component', 'observation'.
        :raises ValueError: If query is empty or invalid.
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string.")

        query_vec = self.model.encode(query)

        if self.use_db:
            try:
                # Filters results to only include those matching the specified language using Qdrant's FieldCondition.
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
                    limit=top_k,
                    with_payload=True,  # Ensure full payload is returned
                    with_vectors=False,  # No need to return vectors
                    search_params=self.models.SearchParams(exact=True)  # Force exact search to match JSON path's brute-force cosine similarity
                )
                # Sorts hits by similarity score in descending order to match top-k ranking.
                # Applies similarity threshold (>0.2) and validates required payload fields before inclusion.
                results = [
                    hit.payload for hit in sorted(hits, key=lambda x: x.score, reverse=True)
                    if hit.score > 0.2 and all(field in hit.payload for field in ['language', 'component', 'observation'])
                ]
                return results
            except Exception as e:
                raise RuntimeError(f"Qdrant search failed: {e}")
        else: # Read the data from the JSON file
            # Performs in-memory semantic search using precomputed vectors from JSON file for language-filtered observations.
            # Collects indices of entries matching the specified language via list comprehension.
            indices = [i for i, d in enumerate(self.data) if d['language'] == language]
            if not indices:
                return []

            # Get the pre-computed vector embeddings of all "observation" texts from the local JSON file.
            lang_vectors = self.vectors[indices]

            # Computes cosine similarity scores between the query vector and all language-filtered observation vectors.
            sims = np.dot(lang_vectors, query_vec) / (np.linalg.norm(lang_vectors, axis=1) * np.linalg.norm(query_vec))

            # Sorts similarity scores to get indices of the top-k most similar entries in descending order.
            top_indices = np.argsort(sims)[-top_k:][::-1]

            # Selects top entries only if their similarity score exceeds the 0.2 threshold.
            results = [self.data[indices[i]] for i in top_indices if sims[i] > 0.2]

            return results
