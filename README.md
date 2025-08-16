# Energy Efficiency MCP Server

This MCP (Model Context Protocol) server provides tools for suggesting energy efficiency improvements in Java, Python, and JavaScript code. It is designed to integrate with GitHub Copilot in VSCode, allowing the IDE to query for suggestions based on static analysis approximated via semantic search on a dataset of efficiency observations. Written in Python.

The server uses FastMCP 2.x and can run locally via stdio or remotely via SSE. Data is stored in a JSON file by default or in a cloud-hosted Qdrant vector database for larger datasets. The project is developed and tested in GitHub Codespaces within a Docker container, with setup automated via `.devcontainer/devcontainer.json`.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Features
- Supports Java, Python, and JavaScript.
- Semantic search for relevant efficiency suggestions based on code snippets.
- Low RAM usage and fast response times, even for datasets >1000 entries.
- Conditional storage: JSON for simple setups, Qdrant for scalable vector search.
- Easy migration from JSON to Qdrant.
- Containerized for consistent development in GitHub Codespaces.

## Tested with the following MCP Clients
1. GitHub Copilot

## Project Structure
- **.devcontainer/**: GitHub Codespaces configuration (`devcontainer.json`).
- **config/**: Configuration files (currently empty; use `.env` for env vars).
- **data/**: Dataset JSON file.
- **docs/**: Additional documentation (e.g., API details).
- **src/**: Source code for the server and utilities.
- **tests/**: Unit tests.
- **Dockerfile**: Defines the Docker image for the server.
- **LICENSE**: MIT License for the project.

## Setup in GitHub Codespaces
1. Open the repository in GitHub Codespaces.
2. Codespaces automatically builds the container using `.devcontainer/devcontainer.json`, which references the `Dockerfile` with `USE_DB=false` (no Qdrant dependencies) and installs Python 3.10, Java 17, and VSCode extensions.
3. Copy `.env.example` to `.env` and configure:
   ```
   USE_DB=false
   TRANSPORT=stdio
   ```
   - For production with Qdrant, set `USE_DB=true` and add `QDRANT_URL` and `QDRANT_API_KEY` (e.g., for Qdrant Cloud).
4. The server starts automatically in the container via `python src/server.py`. To run manually:
   ```bash
   docker run --env-file .env -p 8000:8000 energy-efficiency-mcp
   ```
5. If using Qdrant, rebuild the image with Qdrant support:
   ```bash
   docker build --build-arg USE_DB=true -t energy-efficiency-mcp .
   ```
6. Migrate data to Qdrant:
   ```bash
   docker exec <container-id> python src/migrate.py
   ```

## Running the Server
- In Codespaces, the server runs in the container started by `.devcontainer/devcontainer.json`.
- For local (stdio): Set `TRANSPORT=stdio` in `.env`.
- For remote (SSE): Set `TRANSPORT=sse`; Codespaces auto-forwards port 8000.
- Access the server within Codespaces or externally via forwarded ports.

## Integration with GitHub Copilot
Configure GitHub Copilot in VSCode (pre-installed in Codespaces) to use this MCP server as a custom provider (refer to Copilot and FastMCP documentation for MCP integration). When prompting Copilot for energy-efficient code optimizations, it invokes the server's tool to retrieve suggestions, apply changes, or generate new code.

## Build Configurations
- **USE_DB**: Set to `true` to use Qdrant (requires `QDRANT_URL` and `QDRANT_API_KEY`). Default: `false` (uses JSON).
- **TRANSPORT**: `stdio` for local single-instance use, `sse` for remote multi-instance access. Default: `stdio`.
- In Docker, set `USE_DB` as a build argument: `--build-arg USE_DB=true` for production.

## Dataset
The dataset is in `data/efficiency_data.json`. Add more observations as needed. Format:
```json
[
  {"language": "java", "component": "Variables", "observation": "..."}
]
```
For production with Qdrant, run the migration script after updates: `docker exec <container-id> python src/migrate.py`.

## Contributing
See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup and testing.
