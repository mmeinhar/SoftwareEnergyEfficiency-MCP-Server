# File: mcp-server.py
# Description: This is an MCP server that provides energy efficiency suggestions for
# code snippets in multiple languages. Supports stdio (local) and SSE (remote) transport 
# modes. Server authentication is handled via a Bearer token loaded from a secure file.
# 
# See additional information on increasing software energy efficiency at: https://agile7.com/publications.

import os
from fastmcp import FastMCP
from retriever import EfficiencyRetriever
import logging
from typing import List, Dict
from mcp_auth import configure_mcp_authentication
from utils import configure_logging, get_env_default, print_mcp_env_vars
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Configure logging
configure_logging(default_level=get_env_default("MCP_SERVER_LOG_LEVEL"))
logger = logging.getLogger(__name__)

# Function to print MCP environment variables for debugging purposes
if logger.isEnabledFor(logging.DEBUG):
    print_mcp_env_vars(log_level="debug")

# Initialize EfficiencyRetriever
use_db_str = os.getenv("USE_DB", get_env_default("USE_DB")).lower()
use_db = use_db_str == "true" or use_db_str == "1"
logger.info("Initializing EfficiencyRetriever with USE_DB=%s", use_db)
retriever = EfficiencyRetriever(use_db=use_db)

# Initialize FastMCP server with authentication
mcp = FastMCP(
    name="Agile7-Software-Energy-Efficiency-MCP-Server",
    auth=configure_mcp_authentication()
)

@mcp.tool
async def optimize_energy_efficiency(language: str, code: str, token_data: dict = None) -> List[Dict]:
    """
    Retrieve suggestions to improve the energy efficiency of a code snippet.
    Requires valid authentication based on environment configuration.

    :param language: The programming language of the code (e.g., 'java', 'python', 'javascript').
    :param code: The code snippet to analyze for energy efficiency improvements.
    :param token_data: Injected token data from authentication (automatically provided by FastMCP if auth enabled).
    :return: A list of dictionaries, each containing 'component' and 'observation' for suggested improvements.
    """
    if token_data:
        logger.info(f"Authenticated request from {token_data.get('client_id', 'unknown')} with scopes: {token_data.get('scopes', [])}")
    else:
        logger.info("Unauthenticated request (no auth configured)")

    logger.info(f"Processing energy efficiency suggestions for [{language}] code snippet")
    
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Code snippet:\n{code}")

    results = retriever.search(code, language.lower(), top_k=10)
    logger.info(f"Retrieved [{len(results)}] suggestions for [{language}] code snippet")

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Suggestions for code snippet in language [{language}]:")
        for result in results:
            logger.debug(f"Component: {result['component']}, Observation: {result['observation']}")

    return results

if __name__ == "__main__":
    """
    Start the MCP server with the specified transport mode (stdio or sse).
    Authentication is configured via environment variables in auth.py.
    """
    transport = os.getenv("TRANSPORT", get_env_default("TRANSPORT"))
    mcp.run(transport=transport)