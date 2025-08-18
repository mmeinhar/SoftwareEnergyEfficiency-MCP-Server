# File: test_retriever.py
# Description: Unit tests for the EfficiencyRetriever class to verify search functionality
# in both JSON and Qdrant modes. Ensures correct retrieval of suggestions based on code snippets.

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from retriever import EfficiencyRetriever

def test_search_json_mode():
    """
    Test the search functionality of EfficiencyRetriever in JSON mode.

    Verifies that relevant suggestions are returned for a Java code snippet.
    """
    retriever = EfficiencyRetriever(use_db=False)
    results = retriever.search('StringBuilder sb = new StringBuilder(); sb.append("hello");', 'java', top_k=5)
    assert len(results) > 0
    assert any('String' in res['observation'] for res in results)

@pytest.mark.skipif(not os.getenv("QDRANT_URL"), reason="Qdrant env vars not set")
def test_search_db_mode():
    """
    Test the search functionality of EfficiencyRetriever in Qdrant mode.

    Verifies that relevant suggestions are returned for a Java code snippet if Qdrant is configured.
    """
    retriever = EfficiencyRetriever(use_db=True)
    results = retriever.search('StringBuilder sb = new StringBuilder(); sb.append("hello");', 'java', top_k=5)
    assert len(results) > 0
    assert any('String' in res['observation'] for res in results)
