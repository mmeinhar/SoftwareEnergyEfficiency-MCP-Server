import os
from fastmcp.server.auth.providers.jwt import RSAKeyPair
from datetime import datetime, timedelta
import json

def generate_test_token(
    subject: str = "test-user-123",
    issuer: str = "https://test.yourcompany.com",
    audience: str = "mcp-test-api",
    scopes: list = ["read:data", "write:data"],
    expiry_minutes: int = 60
) -> tuple[str, str]:
    """
    Generate a test JWT and its corresponding public key for testing FastMCP authentication.

    :param subject: JWT subject (e.g., user ID).
    :param issuer: JWT issuer (must match FASTMCP_SERVER_AUTH_JWT_ISSUER).
    :param audience: JWT audience (must match FASTMCP_SERVER_AUTH_JWT_AUDIENCE).
    :param scopes: List of scopes for the token (must include FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES).
    :param expiry_minutes: Token expiry time in minutes.
    :return: Tuple of (test_token, public_key_pem).
    """
    print("Generating test key pair and JWT...")

    # Generate a new RSA key pair
    key_pair = RSAKeyPair.generate()

    # Generate the test token
    test_token = key_pair.create_token(
        subject=subject,
        issuer=issuer,
        audience=audience,
        scopes=scopes,
        expires_in_seconds=expiry_minutes * 60
    )

    print(f"Generated test token: {test_token}")
    print(f"Public key:\n{key_pair.public_key}")

    return test_token, key_pair.public_key

if __name__ == "__main__":
    """
    Generate a test JWT for use with FastMCP server authentication.
    Outputs the token and public key for use in STATIC_JWT or JWT testing.
    
    WARNING: Do not use these tokens or keys in production environments!
    """
    # Example configuration matching mcp_server.py and auth.py
    test_token, public_key = generate_test_token(
        subject="test-user-123",
        issuer="https://test.yourcompany.com",
        audience="mcp-staging-api",  # Matches STATIC_JWT audience in auth.py
        scopes=["read:data"],  # Matches required scopes for STATIC_JWT
        expiry_minutes=60
    )

    # Print results in a format suitable for .env or manual use
    print("\n=== Test Token Output ===")
    print(f"Test Token: {test_token}")
    print("\nPublic Key for STATIC_JWT:")
    print(public_key)
    print("\nSuggested .env configuration for STATIC_JWT (staging):")
    print(f"FASTMCP_SERVER_AUTH=STATIC_JWT")
    print(f"FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY={public_key}")
    print(f"FASTMCP_SERVER_AUTH_JWT_ISSUER=https://test.yourcompany.com")
    print(f"FASTMCP_SERVER_AUTH_JWT_AUDIENCE=mcp-staging-api")
    print(f"FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES=read:data")
    print("\nTo test, use the token in the Authorization header:")
    print(f"Authorization: Bearer {test_token}")