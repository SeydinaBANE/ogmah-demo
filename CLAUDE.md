# OgmahDemo — Restaurant AI Assistant

## Project Overview
Demo project built to showcase AI/ML skills for the ogmah job application.
Simulates an intelligent restaurant management assistant: cost analysis, anomaly detection,
demand forecasting, and a conversational LLM interface over business data.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI
- **ML**: scikit-learn, XGBoost, Prophet (or statsmodels fallback), pandas, numpy
- **LLM**: OpenRouter API (openai SDK compatible), default model `anthropic/claude-3.5-sonnet`, with RAG via simple vector search
- **Database**: PostgreSQL (Docker), SQLAlchemy ORM
- **Frontend**: React + TypeScript + Tailwind CSS + Recharts
- **Infra**: Docker Compose (postgres + backend + frontend)
- **Testing**: pytest for backend, vitest for frontend

## Project Structure
```
projet-2/
├── CLAUDE.md
├── TODO.md
├── docker-compose.yml
├── README.md
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── app/
│   │   ├── api/                 # Route handlers
│   │   │   ├── ingredients.py
│   │   │   ├── recipes.py
│   │   │   ├── sales.py
│   │   │   ├── anomalies.py
│   │   │   ├── forecast.py
│   │   │   └── chat.py
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   └── db_models.py
│   │   ├── ml/                  # ML logic
│   │   │   ├── anomaly_detector.py
│   │   │   ├── demand_forecaster.py
│   │   │   └── margin_optimizer.py
│   │   ├── llm/                 # Claude integration
│   │   │   ├── assistant.py     # Conversational logic + RAG
│   │   │   └── context_builder.py
│   │   ├── data/                # Synthetic data generation
│   │   │   └── seed.py
│   │   └── database.py          # DB connection / session
├── frontend/
│   ├── package.json
│   ├── Dockerfile
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Dashboard.tsx    # KPIs + charts
│   │   │   ├── RecipeTable.tsx
│   │   │   ├── AnomalyPanel.tsx
│   │   │   ├── ForecastChart.tsx
│   │   │   └── ChatInterface.tsx
│   │   └── api/
│   │       └── client.ts
└── notebooks/
    └── exploration.ipynb        # EDA + model prototyping
```

## Key Business Rules (restaurant domain)
- **Food cost ratio** = ingredient cost / selling price. Target < 30%.
- **Margin** = (selling price - ingredient cost) / selling price.
- An anomaly is flagged when a purchase price deviates >20% from the rolling 30-day average.
- Demand forecasting uses 90 days of daily sales history per dish.

## Development Guidelines
- Always use typed Python (type hints everywhere).
- All ML models must be serializable (joblib or pickle) for API serving.
- The LLM assistant must never hallucinate numbers — always ground responses in DB queries.
- Use environment variables for all secrets (OPENROUTER_API_KEY, DATABASE_URL).
- No hardcoded credentials anywhere.
- Keep frontend components small and focused. No massive components.
- Run `docker-compose up` to start everything.

## Running the Project
```bash
cp .env.example .env          # fill in OPENROUTER_API_KEY
docker-compose up --build     # starts postgres + backend + frontend
# backend: http://localhost:8000
# frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
```

## Seeding Data
```bash
docker-compose exec backend python -m app.data.seed
```
