# File: mcp-server.py
# Description: This is an MCP server that provides energy efficiency suggestions for
# code snippets in multiple languages, currently Java, Python, and Javascript. Supports stdio (local) and 
# SSE (remote) transport modes for GitHub Copilot integration.
# 
# WARNING: This MCP server does not currently implement secure authentication to it.
# TODO: Implement OAUTH2 authentication for secure access to this MCP server.

import os
from fastmcp import FastMCP
from retriever import EfficiencyRetriever
import logging

# Set the logging level to WARNING for warnings, INFO for general information, or DEBUG for detailed debugging output.
logging.basicConfig(level=logging.INFO)

use_db_str = os.getenv("USE_DB", "false").lower()
use_db = use_db_str == "true" or use_db_str == "1"

logging.info("Initializing EfficiencyRetriever with use_db=%s", use_db)

retriever = EfficiencyRetriever(use_db=use_db)

mcp = FastMCP("Software-Energy-Efficiency-MCP-Server")

@mcp.tool
def get_energy_efficiency_suggestions(language: str, code: str) -> list[dict]:
    """
    Retrieve suggestions to improve the energy efficiency of a code snippet.

    :param language: The programming language of the code (e.g., 'java', 'python', 'javascript').
    :param code: The code snippet to analyze for energy efficiency improvements.
    :return: A list of dictionaries, each containing 'component' and 'observation' for suggested improvements.
    """
    print("*** WARNING: This MCP server does not currently implement secure authentication! ***")

    logging.info(f"Received request for energy efficiency suggestions in [{language}] code snippet")
    if logging.isEnabledFor(logging.DEBUG):
        logging.debug(f":\n{code}")

    query = code
    results = retriever.search(query, language.lower(), top_k=10)

    logging.info(f"Retrieved [{len(results)}] suggestions for [{language}] code snippet.")

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        print(("DEBUG:Suggestions for code snippet in language [{}]:").format(language))
        for result in results:
            print(f"Component: {result['component']}, Observation: {result['observation']}")

    return results

if __name__ == "__main__":
    """
    Start the MCP server with the specified transport mode (stdio or sse).
    """
    transport = os.getenv("TRANSPORT", "sse")
    mcp.run(transport=transport)

"""
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("multi_tool_server:app", host="0.0.0.0", port=7860, reload=True)
"""
