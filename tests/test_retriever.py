# File: test_retriever.py
# Description: Unit tests for the EfficiencyRetriever class to verify search functionality
# in both JSON and Qdrant modes. Ensures correct retrieval of suggestions based on code snippets.

import sys
import os
import pytest
import json
import textwrap
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from retriever import EfficiencyRetriever

def run_search_test(retriever, search_params, expected_keywords, test_name):
    """
    Common test logic for executing search and verifying results.

    :param retriever: Initialized EfficiencyRetriever instance.
    :param search_params: Dictionary with 'query' (str), 'language' (str), and 'top_k' (int).
    :param expected_keywords: List of keywords (str) expected in results (all must be present).
    :param test_name: Name of the test for printing (e.g., 'JSON Mode', 'Qdrant Mode').
    :return: List of search results (list[str]).
    """
    # Clean the query for readable printing
    cleaned_params = search_params.copy()
    cleaned_params['query'] = textwrap.dedent(cleaned_params['query']).strip()
    print(f"\n=== Testing EfficiencyRetriever in {test_name} ===")
    print(f"Search Parameters:\n{json.dumps(cleaned_params, indent=2, ensure_ascii=False)}")
    print("-" * 50)
    results = retriever.search(search_params['query'], search_params['language'], top_k=search_params['top_k'])
    print(f"{len(results)} Search Results:\n{json.dumps(results, indent=2, ensure_ascii=False)}")
    print("-" * 50)
    assert len(results) > 0, "Expected non-empty results"
    missing_keywords = [keyword for keyword in expected_keywords if not any(keyword in res for res in results)]
    assert not missing_keywords, f"Expected observations containing all of {expected_keywords}, but missing: {', '.join(missing_keywords)}"
    print(f"Test Passed: Results contain all expected observations and are non-empty.\n")
    return results

def test_search_json_mode():
    """
    Test the search functionality of EfficiencyRetriever in JSON mode.

    Verifies that relevant observation strings are returned for a Java code snippet.
    """
    retriever = EfficiencyRetriever(use_db=False)
    search_params = {
        'query': """
            public class Examples1 {
                static String string1;
                static String string2 = "test";

                long example1_1() {
                    Long a = 4;
                    int ternary_operator = (a > b) ? a : b;
                    Vector<Integer> vector = new Vector<>();
                    for (long j = 1; j < iter; j++) {
                        for (long k = 1; k < iter; k++) {
                            a = j % k;
                        }
                    }
                    string1 = "hello" + "world";
                    string1.compareTo(string2);
                    return i;
                }
            }
        """,
        'language': 'java',
        'top_k': 50
    }
    expected_keywords = ["static", "Long", "Vector", "compareTo", "Modulus"]
    run_search_test(retriever, search_params, expected_keywords, "JSON Mode")

@pytest.mark.skipif(not os.getenv("QDRANT_URL"), reason="Qdrant env vars not set")
@patch('qdrant_client.QdrantClient')
def test_search_db_mode(mock_client):
    """
    Test the search functionality of EfficiencyRetriever in Qdrant mode.

    Verifies that relevant observation strings are returned for a Java code snippet if Qdrant is configured.
    """
    # Mock Qdrant client
    mock_client_instance = MagicMock()
    mock_client_instance.collection_exists.return_value = True
    mock_client.return_value = mock_client_instance
    test_json_data = [
        {
            "lang": "java",
            "component": "Variables",
            "lang-keywords": "static",
            "observation": "Avoid excessive use of static variables to reduce memory usage."
        },
        {
            "lang": "java",
            "component": "Types",
            "lang-keywords": "Long",
            "observation": "Use primitive long instead of Long to avoid boxing overhead."
        },
        {
            "lang": "java",
            "component": "Collections",
            "lang-keywords": "Vector",
            "observation": "Vector is synchronized; consider ArrayList for better performance."
        },
        {
            "lang": "java",
            "component": "String Operations",
            "lang-keywords": "compareTo",
            "observation": "Optimize compareTo usage in string comparisons."
        },
        {
            "lang": "java",
            "component": "Operators",
            "lang-keywords": "%",
            "observation": "Modulus operations can be computationally expensive."
        }
    ]
    mock_hits = [
        MagicMock(payload=test_json_data[0], score=0.2),
        MagicMock(payload=test_json_data[1], score=0.18),
        MagicMock(payload=test_json_data[2], score=0.16),
        MagicMock(payload=test_json_data[3], score=0.14),
        MagicMock(payload=test_json_data[4], score=0.12)
    ]
    mock_client_instance.search.return_value = mock_hits

    retriever = EfficiencyRetriever(use_db=True)
    search_params = {
        'query': """
            public class Examples1 {
                static String string1;
                static String string2 = "test";

                long example1_1() {
                    Long a = 4;
                    int ternary_operator = (a > b) ? a : b;
                    Vector<Integer> vector = new Vector<>();
                    for (long j = 1; j < iter; j++) {
                        for (long k = 1; k < iter; k++) {
                            a = j % k;
                        }
                    }
                    string1 = "hello" + "world";
                    string1.compareTo(string2);
                    return i;
                }
            }
        """,
        'language': 'java',
        'top_k': 50
    }
    expected_keywords = ["static", "Long", "Vector", "compareTo", "Modulus"]
    run_search_test(retriever, search_params, expected_keywords, "Qdrant Mode")