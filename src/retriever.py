# File: retriever.py
# Description: Defines the EfficiencyRetriever class for retrieving energy efficiency suggestions
# based on code snippets using semantic search. Supports both JSON-based storage and Qdrant
# vector database, with conditional imports to avoid Qdrant dependencies in development.
#
# TODO: For the use_db=true use case, recheck the code and test. Not tested yet.
# TODO: Add support for single character operators such as the turnary operator (&) and concatination (+) characters in the code snippet.
# TODO: Test the search code some more. The filtering is currently only ~50 accurate.
# 
import os
import json
import numpy as np
import re
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
                required_fields = {'lang', 'component', 'lang-keywords', 'observation'}
                for entry in self.data:
                    if not all(field in entry for field in required_fields):
                        raise ValueError(f"JSON entry missing required fields: {entry}")
                self.vectors = np.array([self.model.encode(d['observation']) for d in self.data])
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON file: {e}")

    def search(self, query: str, language: str, top_k: int = 5) -> list[str]:
        """
        Search for energy efficiency observations relevant to the provided code snippet.

        :param query: The code snippet to analyze.
        :param language: The programming language of the code (e.g., 'java', 'python', 'javascript').
        :param top_k: Maximum number of observation strings to return.
        :return: List of observation strings for matching entries.
        :raises ValueError: If query is empty or invalid.
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string.")
        
        # Tokenize query for keywords (alphanumeric, including hyphens) and operators with spaces
        tokens = set()
        for match in re.findall(r'\b[\w-]+\b|\s[+\-*/%=]\s', query.lower()):
            tokens.add(match.strip())
        
        # Initialize results and deduplication set
        results = []
        seen_observations = set()
        
        # URed from Qdrant db
        if self.use_db: 
            try:
                # Single Qdrant search to retrieve all relevant entries
                hits = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=self.model.encode(query).tolist(),
                    query_filter=self.models.Filter(
                        must=[
                            self.models.FieldCondition(
                                key="lang",
                                match=self.models.MatchValue(value=language)
                            )
                        ]
                    ),
                    limit=max(top_k, 1000),  # Ensure all potential matches are retrieved
                    with_payload=True,
                    with_vectors=False,
                    search_params=self.models.SearchParams(exact=True)
                )
                # Collect observations for token matches and high-similarity entries
                for hit in hits:
                    payload = hit.payload
                    observation = payload.get('observation', '')
                    if all(field in payload for field in ['lang', 'component', 'lang-keywords', 'observation']) and observation not in seen_observations:
                        # Parse lang-keywords
                        keywords = payload.get('lang-keywords', '').lower().split(', ')
                        # Check if any query token matches a whole word in lang-keywords
                        matches_token = any(
                            any(re.search(r'\b' + re.escape(token) + r'\b', keyword) for keyword in keywords)
                            for token in tokens
                        )
                        # Include if matches token or has high similarity (>= 0.1)
                        if matches_token or hit.score >= 0.1:
                            results.append(observation)
                            seen_observations.add(observation)
                            if len(results) >= top_k:
                                break
                return results[:top_k]
            except Exception as e:
                raise RuntimeError(f"Qdrant search failed: {e}")
        # Read from JSON file
        else:
            # Filter entries by language
            indices = [i for i, d in enumerate(self.data) if d['lang'] == language]
            if not indices:
                return []
            
            # Compute similarities for language-filtered entries
            lang_vectors = self.vectors[indices]
            query_vec = self.model.encode(query)
            sims = np.dot(lang_vectors, query_vec) / (np.linalg.norm(lang_vectors, axis=1) * np.linalg.norm(query_vec))
            
            # Collect observations for token matches and high-similarity entries
            for i in indices:
                observation = self.data[i]['observation']
                if observation not in seen_observations:
                    # Parse lang-keywords
                    keywords = self.data[i].get('lang-keywords', '').lower().split(', ')
                    # Check if any query token matches a whole word in lang-keywords
                    matches_token = any(
                        any(re.search(r'\b' + re.escape(token) + r'\b', keyword) for keyword in keywords)
                        for token in tokens
                    )
                    # Include if matches token or has high similarity (>= 0.1)
                    if matches_token or sims[indices.index(i)] >= 0.2:
                        results.append(observation)
                        seen_observations.add(observation)
                        if len(results) >= top_k:
                            break
            
            # Sort results by similarity to prioritize relevant matches
            if results:
                result_indices = [indices.index(i) for i, r in enumerate(self.data) if r['observation'] in results]
                result_sims = [sims[i] if i < len(sims) else 0.0 for i in result_indices]
                sorted_results = [r for _, r in sorted(zip(result_sims, results), key=lambda x: x[0], reverse=True)]
                return sorted_results[:top_k]
            return results[:top_k]