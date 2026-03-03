# Welcome to AI Agents Learning Hub — Codespaces!

Your environment is ready. All Python packages for labs are pre-installed.

## Quick start

```bash
# Set your GitHub token (already forwarded from local env if set)
export GITHUB_TOKEN=ghp_your_token_here

# Run a lab's Python script
cd /workspaces/AI-LearningHub
python -c "import openai, semantic_kernel, mcp; print('All packages ready!')"

# Preview the docs site locally
cd docs && python -m mkdocs serve
# Then open the forwarded port 8080
```

## Services available

| Service | Port | How to start |
|---------|------|--------------|
| MCP Server | 8000 | `python your_mcp_server.py` |
| PostgreSQL + pgvector | 5432 | `docker run -d --name pgvector -e POSTGRES_PASSWORD=ragpass -p 5432:5432 pgvector/pgvector:pg16` |
| Ollama | 11434 | Install: `curl -fsSL https://ollama.com/install.sh \| sh && ollama serve` |
| MCP Inspector | — | `npx @modelcontextprotocol/inspector` |
| Docs preview | 8080 | `cd docs && python -m mkdocs serve --dev-addr 0.0.0.0:8080` |

## Environment variables

Set these as **Codespaces secrets** at github.com/settings/codespaces:
- `GITHUB_TOKEN` — for GitHub Models API (free LLM inference)
- `AZURE_OPENAI_API_KEY` — for L300+ labs (optional)
- `AZURE_OPENAI_ENDPOINT` — for L300+ labs (optional)

## Useful commands

```bash
# Download lab sample data
curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv
curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json
curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/orders.csv

# Test GitHub Models connection
python -c "
import os
from openai import OpenAI
client = OpenAI(base_url='https://models.inference.ai.azure.com', api_key=os.environ['GITHUB_TOKEN'])
r = client.chat.completions.create(model='gpt-4o-mini', messages=[{'role':'user','content':'Say hello in one word'}])
print(r.choices[0].message.content)
"
```
