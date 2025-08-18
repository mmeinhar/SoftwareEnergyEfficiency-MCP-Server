import os
from fastmcp.server.auth.providers.jwt import JWTVerifier, StaticTokenVerifier
import logging
from utils import get_env_default

# Get logger
logger = logging.getLogger(__name__)

def configure_mcp_authentication():
    """
    Configure authentication based on environment variables.
    FastAPI doc: https://gofastmcp.com/servers/auth/token-verification
    
    Environment variables:
    - FASTMCP_SERVER_AUTH: Authentication type ('JWT', 'STATIC_JWT', 'STATIC_TOKEN', or 'none')
    - For JWT (Production):
        - FASTMCP_SERVER_AUTH_JWT_JWKS_URI: JWKS endpoint URL
        - FASTMCP_SERVER_AUTH_JWT_ISSUER: Token issuer
        - FASTMCP_SERVER_AUTH_JWT_AUDIENCE: Expected audience
        - FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES: Comma-separated list of required scopes
    - For STATIC_JWT (Staging):
        - FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY: Static public key in PEM format
        - FASTMCP_SERVER_AUTH_JWT_ISSUER: Token issuer
        - FASTMCP_SERVER_AUTH_JWT_AUDIENCE: Expected audience
        - FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES: Comma-separated list of required scopes
    - For STATIC_TOKEN (Development):
        - No additional variables needed; uses predefined tokens
    
    Returns:
        Configured verifier instance or None if no authentication is required.
    """
    auth_type = os.getenv("FASTMCP_SERVER_AUTH", get_env_default("FASTMCP_SERVER_AUTH")).upper()

    if "JWT" == auth_type: # <------ TODO. test
        # Production: JWKS-based JWT verification
        verifier = JWTVerifier(
            jwks_uri=os.getenv("FASTMCP_SERVER_AUTH_JWT_JWKS_URI", get_env_default("FASTMCP_SERVER_AUTH_JWT_JWKS_URI")),
            issuer=os.getenv("FASTMCP_SERVER_AUTH_JWT_ISSUER", get_env_default("FASTMCP_SERVER_AUTH_JWT_ISSUER")),
            audience=os.getenv("FASTMCP_SERVER_AUTH_JWT_AUDIENCE", get_env_default("FASTMCP_SERVER_AUTH_JWT_AUDIENCE")),
            required_scopes=os.getenv("FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES", get_env_default("FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES")).split(",")
        )
    elif "STATIC_JWT" == auth_type: #<------ TODO. test
        # Staging: Static public key JWT verification
        public_key_pem = os.getenv("FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY", get_env_default("FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY"))
        verifier = JWTVerifier(
            public_key=public_key_pem,
            issuer=os.getenv("FASTMCP_SERVER_AUTH_JWT_ISSUER_STATIC", get_env_default("FASTMCP_SERVER_AUTH_JWT_ISSUER_STATIC")),
            audience=os.getenv("FASTMCP_SERVER_AUTH_JWT_AUDIENCE_STATIC", get_env_default("FASTMCP_SERVER_AUTH_JWT_AUDIENCE_STATIC")),
            required_scopes=os.getenv("FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES_STATIC", get_env_default("FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES_STATIC")).split(",")
        )
    elif "STATIC_TOKEN" == auth_type:
        # Development: Static token verification
        verifier = StaticTokenVerifier(
            tokens={
                "dev-alice-token": {
                    "client_id": "alice@company.com",
                    "scopes": ["read:data", "write:data", "admin:users"]
                },
                "dev-guest-token": {
                    "client_id": "guest-user",
                    "scopes": ["read:data"]
                }
            },
            required_scopes=["read:data"]
        )
    else:
        # No authentication
        verifier = None
        logger.warning("No authentication configured. Server running in insecure mode.")

    return verifier