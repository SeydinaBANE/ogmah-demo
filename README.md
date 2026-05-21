# OgmahDemo — Restaurant AI Assistant

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=flat&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-FF6600?style=flat)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-F7931E?style=flat&logo=scikitlearn&logoColor=white)
![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-7C3AED?style=flat)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat)

> Demo project showcasing AI/ML engineering skills for restaurant management.
> Built to demonstrate real-world IA métier capabilities aligned with the ogmah stack.

![Dashboard screenshot](docs/screenshot-dashboard.png)

## What it does

OgmahDemo is a full-stack intelligent assistant for restaurant operators. It transforms raw business data (recipes, ingredient purchases, daily sales, stock levels) into actionable intelligence:

- **Anomaly detection** — flags supplier price spikes in real time using Isolation Forest
- **Demand forecasting** — predicts dish sales for the next 30 days with XGBoost
- **Margin analysis** — identifies recipes with poor food-cost ratios and suggests optimizations
- **Conversational AI** — a chat interface powered by Claude that answers business questions grounded in live data (no hallucinations)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│   Dashboard │ Anomaly Panel │ Forecast Chart │ Chat UI       │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API
┌─────────────────────▼───────────────────────────────────────┐
│                    Backend (FastAPI)                          │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  ML Layer   │  │  LLM Layer   │  │   Data Layer       │  │
│  │             │  │              │  │                    │  │
│  │ Anomaly     │  │ Claude API   │  │ SQLAlchemy ORM     │  │
│  │ Detector    │  │ + RAG        │  │ + PostgreSQL       │  │
│  │             │  │ Context      │  │                    │  │
│  │ Demand      │  │ Builder      │  │ Ingredients        │  │
│  │ Forecaster  │  │              │  │ Recipes            │  │
│  │             │  │              │  │ Purchases          │  │
│  │ Margin      │  │              │  │ Sales              │  │
│  │ Optimizer   │  │              │  │ Stock              │  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   PostgreSQL                                  │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy |
| ML | scikit-learn, XGBoost, pandas, numpy |
| LLM | OpenRouter (openai SDK) — défaut: `anthropic/claude-3.5-sonnet` |
| Database | PostgreSQL 15 |
| Frontend | React 18, TypeScript, Tailwind CSS, Recharts |
| Infra | Docker Compose |

## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/YOUR_USERNAME/ogmah-demo.git
cd ogmah-demo
cp .env.example .env
# Edit .env: set OPENROUTER_API_KEY (get one at openrouter.ai)
# Optionally set OPENROUTER_MODEL (default: openai/gpt-4o-mini)

# 2. Start everything
make build   # or: docker-compose up --build

# 3. Seed the database with 6 months of synthetic restaurant data
make seed    # or: docker-compose run --rm backend python -m app.data.seed

# 4. Open the app
open http://localhost:3000

# 5. Explore the API docs
open http://localhost:8000/docs
```

## Key Features

### Anomaly Detection
Monitors ingredient purchase prices against a 30-day rolling baseline.
Flags purchases where price deviates more than 20% using Isolation Forest.

### Demand Forecasting
XGBoost model with temporal features (day of week, week of year, lag features).
Predicts daily unit sales per dish for the next 30 days with confidence intervals.

### Margin Analysis
Computes food-cost ratio for each recipe based on current ingredient prices.
Identifies recipes where cost > 30% of selling price and ranks optimization opportunities.

### Conversational Assistant
Claude-powered chat grounded in live database queries — no hallucinations.
Uses prompt caching to minimize API costs on repeated system context.

Example questions:
- *"Quelle est notre marge moyenne ce mois-ci ?"*
- *"Quelles recettes ont un food cost supérieur à 35% ?"*
- *"Y a-t-il des anomalies d'achat sur nos fournisseurs cette semaine ?"*
- *"Prévision de ventes pour le Bœuf Bourguignon la semaine prochaine ?"*

## Project Structure

```
projet-2/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── requirements.txt
│   └── app/
│       ├── api/                 # Route handlers
│       ├── models/              # DB models
│       ├── ml/                  # ML modules
│       ├── llm/                 # Claude integration
│       └── data/                # Synthetic data seed
├── frontend/
│   └── src/
│       ├── components/          # React components
│       └── api/                 # API client
├── notebooks/
│   └── exploration.ipynb        # EDA + model selection
├── docker-compose.yml
└── .env.example
```

## Deployment

### Option A — Railway (recommandé, gratuit)

Railway supporte Docker Compose nativement et offre PostgreSQL géré.

```bash
# 1. Installer Railway CLI
npm install -g @railway/cli

# 2. Login et init
railway login
railway init   # dans le dossier du projet

# 3. Ajouter PostgreSQL
railway add --plugin postgresql

# 4. Configurer les variables d'environnement
railway variables set OPENROUTER_API_KEY=sk-or-v1-...
railway variables set OPENROUTER_MODEL=openai/gpt-4o-mini
railway variables set ALLOWED_ORIGINS=https://VOTRE_APP.up.railway.app
railway variables set DATABASE_URL='${{Postgres.DATABASE_URL}}'

# 5. Déployer
railway up
```

Après le déploiement, seed la base :
```bash
railway run python -m app.data.seed
```

### Option B — Render

Render permet de déployer backend et frontend séparément en free tier.

**Backend (Web Service)**
1. New → Web Service → connecter le repo GitHub
2. Root Directory : `backend`
3. Runtime : Docker
4. Variables d'environnement :
   - `OPENROUTER_API_KEY` = votre clé
   - `OPENROUTER_MODEL` = `openai/gpt-4o-mini`
   - `DATABASE_URL` = URL de la base PostgreSQL Render

**Base de données**
1. New → PostgreSQL (free tier)
2. Copier l'`Internal Database URL` dans `DATABASE_URL` du backend

**Frontend (Static Site)**
1. New → Static Site → connecter le repo GitHub
2. Root Directory : `frontend`
3. Build Command : `npm install && npm run build`
4. Publish Directory : `dist`
5. Variables : `VITE_API_BASE_URL=https://votre-backend.onrender.com`

**Seeder (une fois déployé)**
```bash
# Via Render Shell dans le dashboard backend
python -m app.data.seed
```

### Variables d'environnement en production

| Variable | Description | Exemple |
|---|---|---|
| `OPENROUTER_API_KEY` | Clé API OpenRouter | `sk-or-v1-...` |
| `OPENROUTER_MODEL` | Modèle LLM | `openai/gpt-4o-mini` |
| `DATABASE_URL` | URL PostgreSQL complète | `postgresql://user:pass@host/db` |
| `ALLOWED_ORIGINS` | URL(s) frontend autorisées | `https://mon-app.up.railway.app` |
| `ENVIRONMENT` | Environnement | `production` |

## Running Tests

```bash
make test   # or: docker-compose run --rm backend pytest -v --cov=app --cov-report=term-missing
```

## Troubleshooting

| Problème | Solution |
|---|---|
| `database "ogmah" does not exist` | Lancer `make rebuild` pour repartir avec un volume propre |
| `Error code: 401 — User not found` | Vérifier `OPENROUTER_API_KEY` dans `.env`, puis `make restart-backend` |
| `404 — No endpoints found for model` | Changer `OPENROUTER_MODEL` dans `.env` (ex: `openai/gpt-4o-mini`) |
| Frontend vide / erreur réseau | Attendre que le backend soit prêt : `make logs-backend` |
| Modèles ML perdus après redémarrage | Normal si le volume `models_cache` a été supprimé — ils se ré-entraînent automatiquement |

## RGPD / Security
- No real personal data — all data is synthetically generated
- All secrets via environment variables
- Input validation via Pydantic on all endpoints
- Rate limiting on the chat endpoint
