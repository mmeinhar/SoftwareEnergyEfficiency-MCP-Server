import os
import logging

def get_env_default(var_name: str) -> str:
    """
    Return the default value for a given FastMCP server environment variable.

    :param var_name: Name of the environment variable.
    :return: Default value as a string, or None if the variable is not recognized.
    """
    env_defaults = {
        "MCP_SERVER_LOG_LEVEL": "INFO",
        "USE_DB": "false",
        "TRANSPORT": "sse",
        "QDRANT_URL": "https://your-qdrant-cluster-url",
        "QDRANT_API_KEY": "your-api-key",
        "FASTMCP_SERVER_AUTH": "none",
        "FASTMCP_SERVER_AUTH_JWT_JWKS_URI": "https://auth.yourcompany.com/.well-known/jwks.json",
        "FASTMCP_SERVER_AUTH_JWT_ISSUER": "https://auth.yourcompany.com",
        "FASTMCP_SERVER_AUTH_JWT_AUDIENCE": "mcp-production-api",
        "FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES": "read:data,write:data",
        "FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
        "FASTMCP_SERVER_AUTH_JWT_ISSUER_STATIC": "https://test.yourcompany.com",  # Alias for STATIC_JWT issuer
        "FASTMCP_SERVER_AUTH_JWT_AUDIENCE_STATIC": "mcp-staging-api",  # Alias for STATIC_JWT audience
        "FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES_STATIC": "read:data"  # Alias for STATIC_JWT scopes
    }
    return env_defaults.get(var_name, None)

def print_mcp_env_vars() -> None:
    """
    Print all FastMCP server environment variables for debugging and configuration verification.
    Shows the actual value set in the environment, or the default if unset.
    """
    logger = logging.getLogger(__name__)
    logger.info("\n\n=== Software-Energy-Efficiency-MCP-Server MCP Server Environment Variables ===")
    
    env_vars = [
        {
            "name": "MCP_SERVER_LOG_LEVEL",
            "description": "Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        },
        {
            "name": "USE_DB",
            "description": "Set to true to use Qdrant vector DB, false for JSON"
        },
        {
            "name": "TRANSPORT",
            "description": "Transport mode: stdio for local, sse for remote"
        },
        {
            "name": "QDRANT_URL",
            "description": "Qdrant cluster URL (required if USE_DB=true)"
        },
        {
            "name": "QDRANT_API_KEY",
            "description": "Qdrant API key (required if USE_DB=true)"
        },
        {
            "name": "FASTMCP_SERVER_AUTH",
            "description": "Authentication type: JWT (production), STATIC_JWT (staging), STATIC_TOKEN (development), or none"
        },
        {
            "name": "FASTMCP_SERVER_AUTH_JWT_JWKS_URI",
            "description": "JWKS endpoint URL for JWT verification (production)"
        },
        {
            "name": "FASTMCP_SERVER_AUTH_JWT_ISSUER",
            "description": "Token issuer for JWT verification (production)"
        },
        {
            "name": "FASTMCP_SERVER_AUTH_JWT_AUDIENCE",
            "description": "Expected audience for JWT verification (production)"
        },
        {
            "name": "FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES",
            "description": "Comma-separated required scopes for JWT verification (production)"
        },
        {
            "name": "FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY",
            "description": "Static public key for STATIC_JWT verification (staging)"
        },
        {
            "name": "FASTMCP_SERVER_AUTH_JWT_ISSUER_STATIC",
            "description": "Token issuer for STATIC_JWT verification (staging)"
        },
        {
            "name": "FASTMCP_SERVER_AUTH_JWT_AUDIENCE_STATIC",
            "description": "Expected audience for STATIC_JWT verification (staging)"
        },
        {
            "name": "FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES_STATIC",
            "description": "Comma-separated required scopes for STATIC_JWT verification (staging)"
        }
    ]

    for var in env_vars:
        value = os.getenv(var["name"], get_env_default(var["name"]))
        logger.info(f"{var['name']}={value} description=({var['description']})")
    logger.info("==============================================================================\n\n")

def configure_logging(default_level: int) -> None:
    """
    Configure logging based on the MCP_SERVER_LOG_LEVEL environment variable.

    :param default_level: Default logging level (e.g., logging.INFO) if MCP_SERVER_LOG_LEVEL is invalid or unset.
    """
    log_level = os.getenv("MCP_SERVER_LOG_LEVEL", get_env_default("MCP_SERVER_LOG_LEVEL")).upper()
    try:
        logging.basicConfig(level=getattr(logging, log_level, default_level))
    except AttributeError:
        logging.basicConfig(level=default_level)
        logging.getLogger(__name__).warning(f"Invalid MCP_SERVER_LOG_LEVEL '{log_level}', defaulting to {logging.getLevelName(default_level)}")