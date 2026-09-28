# E-commerce Knowledge Graph

A FastAPI app that answers e-commerce questions using a NetworkX graph and Groq. Groq creates a restricted query plan; the app validates it, retrieves matching graph records, and builds the answer from those records only.

## Start

Requires Python 3.12. In PowerShell, from the project folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Add your Groq API key to `.env`. Check [Groq's model list and pricing](https://console.groq.com/docs/models) and set `GROQ_MODEL` to a model your account can access. Free quotas and model access vary; check pricing before sending requests. Do not commit `.env`.

Start the server:

```powershell
python main.py
```

Open Swagger at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). The API endpoints are `GET /health` and `POST /query`. Example request:

```json
{"question": "Find banana"}
```

The graph contains five `banana` keyword nodes. You can also ask questions such as `Which products from Apple are supplied by GlobalTech Distributors?`.

## How It Works

The sample brands, products, vendors, categories, customers, orders, and keyword nodes are defined in `kg_retrieval/data.py`. At startup, `kg_retrieval/graph.py` builds their relationships in NetworkX.

For each question, Groq returns a JSON filter plan. `kg_retrieval/retrieval.py` validates the plan and finds matching graph records. The response includes both the records and a readable answer generated from them. The model does not provide product facts or run arbitrary graph code. Update `data.py` and restart the server to rebuild the graph.

Application logs are written daily to `logs/app-YYYY-MM-DD.log`; they also appear in the server terminal.
