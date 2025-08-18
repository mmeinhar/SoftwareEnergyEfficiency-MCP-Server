# Development Guide

This project is developed and tested in GitHub Codespaces using a Docker container defined by the `Dockerfile` and `.devcontainer/devcontainer.json` for consistent environments. The server is written in Python and processes all computer languages as strings for energy efficiency optimizations, requiring no runtime execution of these languages. Current energy-efficiency datasets: Java.

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

## Logging
- Change the environment variable `MCP_SERVER_LOG_LEVEL` in `.env` to `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` to set the log level.

## Build Configurations
- Development: `USE_DB=false`, `TRANSPORT=stdio` (no Qdrant imports/installs).
- Production: `USE_DB=true`, `TRANSPORT=sse` (build with `--build-arg USE_DB=true`, configure Qdrant env vars).
- Migration: After updating `data/efficiency_data.json`, run:
  ```bash
  docker exec <container-id> python src/migrate.py
  ```

## Adding New Languages/
- Update `data/efficiency_data.json` with new entries for multiple languages. If the dataset becomes too large for a JSON file, enable Qdrant by setting `USE_DB=true` in `.env` and run the migration script called "migrate_data_from_json_to_db.py 

## Notes
- In development, using JSON mode (`USE_DB=false`) has code implemented to avoid importing external database dependencies.
- For production, deploy the container with SSE for multi-instance Copilot access.
