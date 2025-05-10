# Gen‑AI Cloud Advisor (AWS) – v0.2
**Status**: :warning: *Early development preview*.  Gen‑AI powered rightsizing landed in `v0.2`.

## What it Does
* Ingests AWS Cost & Usage + CloudWatch metrics daily.  
* Stores features in a Vector DB (Qdrant) with embeddings.  
* Lets you **chat** in plain English about cost drivers.  
* Uses **OpenAI GPT‑4o** *and* **Google Gemini Pro** together to propose rightsizing actions (EC2/RDS).

## Quick Start (Local)
```bash
git clone https://github.com/your-org/gen-ai-cloud-advisor-aws.git
cd gen-ai-cloud-advisor-aws
cp .env.example .env        # fill in keys
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d qdrant   # vector DB
python ingest/aws_cost_export.py   # -> data/cost_daily.csv
uvicorn backend.app.main:app --reload
streamlit run frontend/app.py
```

## Architecture
```
                 ┌──────────────────────┐
                 │ AWS Cost & Usage CSV │
                 └──────┬───────────────┘
                        │
                 ┌──────▼───────────────┐
                 │      Ingest ETL      │
                 └──────┬───────────────┘
                        │
                 ┌──────▼───────────────┐
                 │     Feature Store    │
                 └──────┬───────────────┘
                        │  Embeddings
                 ┌──────▼───────────────┐
                 │      Vector DB       │
                 └──────┬───────────────┘
                        │
                 ┌──────▼───────────────┐
                 │    LLM Reasoner      │ (RAG)
                 └──────┬───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │  Rightsizing Engine (AI Duo)  │
        │  ┌──────────────┐┌──────────┐ │
        │  │  GPT‑4o      ││ Gemini    │ │
        │  └──────────────┘└──────────┘ │
        └───────────────┬───────────────┘
                        │  REST
                 ┌──────▼───────────────┐
                 │     FastAPI API      │
                 └──────┬───────────────┘
                        │
                ┌───────▼───────────────┐
                │    Streamlit UI       │
                └───────────────────────┘
```

## Roadmap
See [`docs/roadmap.md`](docs/roadmap.md).

## Contributing
PRs & issues welcome. For large changes, open a Discussion first.
