import os
import json
import requests
import argparse
from dotenv import load_dotenv

def get_test_token():
    """
    Return a test token based on the authentication type defined in FASTMCP_SERVER_AUTH.
    For STATIC_TOKEN, use a predefined token from auth.py. For JWT/STATIC_JWT, log a warning
    as a valid token must be provided externally. For none, return None.
    """
    auth_type = os.getenv("FASTMCP_SERVER_AUTH")
    if auth_type == "STATIC_TOKEN":
        # Use a known token from auth.py's StaticTokenVerifier
        return "dev-alice-token"
    elif auth_type in ("JWT", "STATIC_JWT"):
        # For JWT/STATIC_JWT, a valid token must be provided externally
        print("JWT or STATIC_JWT authentication requires a valid token. Set TEST_TOKEN in environment or secrets file.")
        return os.getenv("TEST_TOKEN", None)
    else:
        # No authentication required
        return None

def main(url, method):
    """
    Test the FastMCP server by sending a request to the specified URL with the specified HTTP method.

    :param url: The endpoint URL to test (e.g., http://localhost:8000/sse).
    :param method: The HTTP method to use ('GET' or 'POST').
    """
    print(f"Starting test for FastMCP server with {method} request")
    
    # Load the environment variables from the .env file
    load_dotenv()

    # Test configuration
    token = get_test_token()
    headers = {}
    payload = None

    if method.upper() == "GET":
        headers["Accept"] = "text/event-stream"  # Required for SSE
    elif method.upper() == "POST":
        headers["Content-Type"] = "application/json"
        payload = {
            "language": "python",
            "code": "print('Hello, World!')"
        }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Send request
    print(f"Sending {method} request to {url} with headers: {headers}")
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    print(line.decode('utf-8'))
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: Unsupported method '{method}'. Use 'GET' or 'POST'.")
            return
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Test FastMCP server endpoint")
    default_test_url = "http://localhost:8000/sse"

    parser.add_argument(
        "--url",
        default=default_test_url,
        help= f"URL of the FastMCP server endpoint (default: {default_test_url})"
    )
    parser.add_argument(
        "--method",
        default="GET",
        choices=["GET", "POST"],
        help="HTTP method to use for the request (GET or POST, default: GET)"
    )
    args = parser.parse_args()

    main(args.url, args.method)