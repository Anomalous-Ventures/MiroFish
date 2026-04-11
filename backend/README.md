# backend

Flask application powering the MiroFish swarm intelligence engine.

## Layout

- `run.py` - Flask entrypoint (host/port from env, `FLASK_PORT=5001` default).
- `app/__init__.py` - application factory; registers `graph`, `simulation`, `report` blueprints and `/health`.
- `app/config.py`, `app/config_infrastructure.py` - env-driven configuration.
- `app/api/` - HTTP blueprints (`graph.py`, `simulation.py`, `report.py`).
- `app/services/` - graph build, OASIS simulation runner/manager, Zep memory, ReportAgent, text/profile/ontology generators.
- `app/models/` - project and task domain models.
- `app/utils/` - LLM client, file parser, logger, retry, paging.
- `scripts/` - standalone simulation runners (`run_parallel_simulation.py`, `run_reddit_simulation.py`, `run_twitter_simulation.py`) and action logger.

## Run

```bash
uv sync
uv run python run.py
```

Requires `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_NAME`, `ZEP_API_KEY` in `.env` at repo root. Python 3.11-3.12.

## Key dependencies

`flask`, `flask-cors`, `openai`, `zep-cloud==3.13.0`, `camel-oasis==0.2.5`, `camel-ai==0.2.78`, `PyMuPDF`, `pydantic`.
