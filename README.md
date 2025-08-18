# Software Energy Efficiency MCP Server

This MCP (Model Context Protocol) server provides tools for suggesting energy efficiency improvements in any computer language (dataset currently supports only Java). It has been tested with GitHub Copilot in VS Code, allowing the IDE to query for suggestions based on static analysis approximated via semantic search on a dataset of efficiency observations. The server processes code as strings and does not execute it.

The server is written in Python using FastMCP 2.x and can run locally via stdio or remotely via SSE. Data is stored in a JSON file by default or in a cloud-hosted Qdrant vector database for larger datasets. The project is developed and tested in GitHub Codespaces within a Docker container, with setup automated via `.devcontainer/devcontainer.json`.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Features
- Supports any computer language. Current available data sets: Java.
- Semantic search for relevant energy efficiency suggestions based on code snippets.
- Conditional storage: JSON for simple setups and small energy efficiency datasets, Qdrant with scalable vector search for large data sets.
- Automated script-driven migration from JSON to Qdrant.
- Containerized for portability and ease of deployment.
- Configurable levels of server authentication depending on the deployment environment (Production: JWKS-based JWT verification, Staging: Static public key JWT verification, Development: Static token verification, and None)).
- Centralized configuration via `.env` file for environment-specific settings.

## Tested with the following MCP Clients
- GitHub CoPilot in Visual Studio Code

## Project Structure
- **.devcontainer/**: GitHub Codespaces configuration (`devcontainer.json`).
- **data/**: Software energy efficiency dataset JSON file.
- **src/**: Source code for the server.
- **src/tools/**: Scripts for the JSON to database migration and test token generation.
- **tests/**: Unit tests.
- **example_code_for_testing/**: Examples of code in multiple languages for testing energy efficiency suggestions.
- **Dockerfile**: Defines the Docker image for the server.
- **.env.example**: Example environment configuration file.
- **LICENSE**: MIT License for the project.

## Setup in GitHub Codespaces
1. Open the repository in GitHub Codespaces.
2. Codespaces automatically builds the container using `.devcontainer/devcontainer.json`, which references the `Dockerfile` with `USE_DB=false` (no Qdrant dependencies) and installs:
   - Python 3.10 for the server.
3. Copy `.env.example` to `.env` and configure environment variables in it.
4. The server starts automatically in the container via `python src/mcp_server.py`. To run manually:
   ```bash
   docker run --env-file .env -p 8000:8000 software-energy-efficiency-mcp
   ```
5. If using Qdrant, rebuild the image with Qdrant support. NOTE: Default is JSON file support (`USE_DB=false`):
   ```bash
   docker build --build-arg USE_DB=true -t software-energy-efficiency-mcp .
   ```
6. If using Qdrant, populate the data/efficiency-data.json file and migrate it to the Qdrant db via the script `src/tools/migrate_data_from_json_to_db.py`:
   ```bash
   docker exec <container-id> python src/tools/migrate_data_from_json_to_db.py
   ```

## Running the Server
- In Codespaces, the server runs in the container started by `.devcontainer/devcontainer.json`.
- For local (stdio): Set `TRANSPORT=stdio` in `.env`.
- For remote (SSE)(default): Set `TRANSPORT=sse`; Codespaces auto-forwards port 8000.
- Access the server within Codespaces or externally via forwarded ports.
- The MCP server processes Java and any other code as strings sent from the MCP client (e.g. Copilot).

## Integration with GitHub Copilot
Configure GitHub Copilot in VSCode (pre-installed in Codespaces) to use this MCP server as a custom provider (refer to Copilot and FastMCP documentation for MCP integration). When prompting Copilot for energy-efficient code optimizations, it sends code as strings to the server, which returns suggestions to apply changes or generate new code, depending on the context which Copilot utilizes.

## Prompts
To force a call to the get_energy_efficiency_suggestions tool from GitHub Copilot, select some code in the IDE and then open the Copilot inline chat and enter "#get_energy_efficiency_suggestions: analyze Java code".

## Runtime Configuration file
- All configuration options are set in the `.env` file. This was copied from `.env.example` and should be customized for your environment. .env is not committed to the repository. .env should have permissions set to 600 (read/write for the owner only).

## Dataset
The dataset is in `data/efficiency_data.json`. Add more observations as needed. Any language can be added, but it currently supports only java. Format:
```json
[
  {"language": "java", "component": "Variables", "observation": "..."}
]
```
For production with Qdrant, run the migration script after updates: `docker exec <container-id> python src/migrate.py`.

## TODO Features
- Further expand the energy efficiency dataset to include more Java observations and also add additional languages.
- In the Production version of the container, remove efficiency-data.json and migrate.py from dockerfile and run outside. Investigate the ease of a continuous database migration process and fully minimize the effort to switch from development to production dockerfile. 

## Contributing
See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup and testing.
