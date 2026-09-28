# E-commerce Knowledge Graph Retrieval

A compact Python project that builds an e-commerce NetworkX graph from the sample entity data in `kg_retrieval/data.py` and retrieves product facts from natural-language questions. It uses OpenAI's API to produce a restricted JSON filter plan when an API key is configured. The returned answer is formatted from graph records only; the LLM does not invent or supply product facts.

## What is included

- `Product`, `Brand`, `Vendor`, `Category`, `Customer`, `Order`, and `Keyword` entities connected by typed relationships.
- The sample dataset in `kg_retrieval/data.py`, including order line quantities and calculated order totals.
- Five `banana` keyword nodes, retrievable through the question endpoint.
- An OpenAI planner that converts natural-language questions into validated graph filters.
- A FastAPI service exposing health and question endpoints.
- Query-plan validation that rejects unsupported filters and executable query text.
- MIT-licensed project code and sample data. Third-party packages retain their own licenses.

## Requirements

- Python 3.10 or newer
- An OpenAI API key is required for question queries; API usage may incur charges.

## Run locally

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python main.py
python -m pytest
```

The API is available at `http://127.0.0.1:8000`. It has exactly two routes: `GET /health` and `POST /query`. Example query body:

```json
{"question": "Which products from Apple are supplied by GlobalTech Distributors?"}
```

The response includes the validated filter plan, matching graph records, planner name, and an answer formatted only from those records. Set `OPENAI_API_KEY` before starting the app. Without it, `POST /query` returns `503`; the health endpoint remains available.

## Enable OpenAI

Create an API key at [OpenAI API Keys](https://platform.openai.com/api-keys). API usage may be billed separately from ChatGPT subscriptions. Copy `.env.example` to `.env`, then add the key:

```dotenv
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

`.env` is ignored by Git. Never commit an API key. Send a question to `POST /query`; the OpenAI model will create a JSON filter plan, the application will validate it, and NetworkX will retrieve the matching graph data. Set `OPENAI_MODEL` to a model available to your API account if the default is unavailable.

## Dataset options

The included Python lists are a fictional starter dataset designed to demonstrate brands, suppliers, categories, customers, orders, and product retrieval without relying on external files or licenses. To use real transaction data, see the [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail). It contains invoice-level retail transactions, not brand/vendor relationships, so those fields would need to be enriched or left out when adapting the graph builder. Check the dataset's current terms and attribution requirements before redistribution.

To change the sample graph, update the entity lists in `kg_retrieval/data.py` and restart the service. The graph is rebuilt from the data when `main.py` starts.

## Graph and retrieval flow

```text
Question -> OpenAI JSON filter plan
         -> plan validation -> NetworkX relationship traversal
         -> retrieved graph records -> deterministic grounded answer
```

The graph query surface is intentionally a small allowlist of exact `brand`, `vendor`, `category`, and `name` filters plus a text search. It does not execute model-generated Cypher, Python, or arbitrary NetworkX operations.

## GitHub

This folder is ready to publish as a GitHub repository. From this directory, after creating an empty repository on GitHub:

```powershell
git init
git add .
git commit -m "Build e-commerce knowledge graph retrieval demo"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/commerce-knowledge-graph.git
git push -u origin main
```

Replace the remote URL with your repository URL. Check `git status` before pushing and confirm `.env` is not staged.