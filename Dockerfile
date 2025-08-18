# File: Dockerfile
# Description: Defines the Docker image for the Energy Efficiency MCP Server.
# Builds a Python environment with dependencies for development and production,
# with conditional Qdrant installation based on USE_DB environment variable.

FROM python:3.10-slim

# Install necessary dependencies (curl, git, build-essential, etc.)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

WORKDIR /app

# Copy only requirements.txt first to leverage Docker layer caching
COPY requirements.txt /app/

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Conditionally install qdrant-client if USE_DB=true
ARG USE_DB=false
RUN if [ "$USE_DB" = "true" ]; then pip install qdrant-client; fi

# Copy the rest of the application files into the container
COPY . /app

# Expose the relevant port (assuming your server runs on port 8000)
EXPOSE 8000

# Default command to run the server
CMD ["python", "src/mcp_server.py"]