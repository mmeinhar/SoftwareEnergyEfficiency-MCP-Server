# Development Guide

This project is developed and tested in GitHub Codespaces using a Docker container defined by the `Dockerfile` and `.devcontainer/devcontainer.json` for consistent environments. The server is written in Python and processes all (only Java currently supported) computer code as strings for energy efficiency optimizations, requiring no runtime execution of these languages.

## Setup in GitHub Codespaces
1. Open the repository in Codespaces.
2. The `.devcontainer/devcontainer.json` configures the environment to use the `Dockerfile` with:
   - Python 3.10 for the server.
   - VSCode extensions for Python and GitHub Copilot.
3. For development, `USE_DB=false` is set in `devcontainer.json` to avoid Qdrant dependencies.
4. For Qdrant testing (production mode):
   - Update `.env` with `USE_DB=true`, `QDRANT_URL`, and `QDRANT_API_KEY` (use a free Qdrant Cloud instance).
   - Rebuild the Docker image:
     ```bash
     docker build --build-arg USE_DB=true -t software-energy-efficiency-mcp .
     ```
5. Codespaces automatically starts the container. To run manually:
   ```bash
   docker run --env-file .env -p 8000:8000 software-energy-efficiency-mcp
   ```
6. Port 8000 is auto-forwarded by Codespaces for SSE mode if `TRANSPORT=sse`.

## Testing
- Run tests inside the container:
  ```bash
  docker exec <container-id> pytest tests/
  ```
- Tests cover the retriever with JSON mode. Qdrant tests are skipped unless `QDRANT_URL` is set.
- To test the server’s suggestions, create code snippets (e.g., Java, Python, JavaScript files) in VSCode; the server processes them as strings without execution.

## Build Configurations
- Development: `USE_DB=false`, `TRANSPORT=stdio` (no Qdrant imports/installs).
- Production: `USE_DB=true`, `TRANSPORT=sse` (build with `--build-arg USE_DB=true`, configure Qdrant env vars).
- Migration: After updating `data/efficiency_data.json`, run:
  ```bash
  docker exec <container-id> python src/migrate.py
  ```

## Adding New Languages/Observations
- Update `data/efficiency_data.json` with new entries for Java, Python, or JavaScript.
- If using Qdrant, re-run `migrate.py` inside the container.
- The retriever abstraction minimizes code changes for JSON-to-Qdrant migration.

## Notes
- In development, use JSON mode (`USE_DB=false`) to avoid external dependencies.
- For production, deploy the container with SSE for multi-instance Copilot access.
- The `.devcontainer/devcontainer.json` automates setup, installing VSCode extensions for Python, JavaScript, Java (for editing, not execution), and Copilot, and forwards port 8000 for SSE.
- Java and JavaScript support is included for editing code snippets in VSCode, as the server processes these as strings sent by the MCP client (e.g., Copilot).
- The Docker image ensures low RAM usage by computing embeddings once during initialization or migration.
