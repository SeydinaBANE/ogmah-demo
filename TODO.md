# OgmahDemo — TODO

## Status Legend
- [ ] = À faire
- [x] = Terminé
- [~] = En cours

---

## Phase 1 — Fondations ✅

### Infra & Setup
- [x] `docker-compose.yml` avec postgres + backend + frontend
- [x] `.env.example` avec toutes les variables requises
- [x] `backend/requirements.txt` complet
- [x] `backend/Dockerfile` (utilisateur non-root, .dockerignore)
- [x] `frontend/package.json` + `frontend/Dockerfile`
- [x] SQLAlchemy models (Ingredient, Recipe, RecipeIngredient, Purchase, Sale, Stock)
- [x] Script de seed : données synthétiques réalistes (6 mois de données restaurant)

### Backend skeleton
- [x] FastAPI app + CORS configurable via env + health check endpoint
- [x] Database session / connection pool
- [x] SQLAlchemy create_all (migrations schema auto au démarrage)
- [x] Endpoints CRUD basiques : ingredients, recipes, sales

---

## Phase 2 — Modules ML ✅

### Anomaly Detection
- [x] `AnomalyDetector` class (Isolation Forest + log-ratio sur prix d'achat)
- [x] Endpoint `GET /api/anomalies` — retourne les achats suspects
- [x] Endpoint `POST /api/anomalies/retrain` — réentraîne le modèle
- [x] Tests unitaires du détecteur (3 tests)

### Demand Forecasting
- [x] `DemandForecaster` class (XGBoost avec features temporelles)
- [x] Endpoint `GET /api/forecast/{recipe_id}?days=30`
- [x] Serialisation du modèle (joblib, volume persistant)
- [x] Tests unitaires (5 tests feature engineering)

### Margin Optimizer
- [x] `MarginOptimizer` class — calcul de marge par recette
- [x] Endpoint `GET /api/recipes/margin-analysis`
- [x] Recommandations : recettes sous objectif 30%
- [x] Calcul d'impact prix fournisseur sur marge
- [x] Tests unitaires (2 tests)

---

## Phase 3 — Assistant LLM ✅

### OpenRouter Integration
- [x] `Assistant` class avec OpenRouter (openai SDK compatible, modèle configurable via env)
- [x] System prompt métier : contexte restaurant, règles de gestion
- [x] `ContextBuilder` : transforme les données DB en contexte structuré pour le LLM
- [x] RAG simple : données business + marges injectées dans chaque requête
- [x] Endpoint `POST /api/chat` avec historique de conversation par session
- [x] Gestion des erreurs (timeout, rate limit, API error) avec messages français
- [x] Rate limiting : 20 req/min sur le chat
- [x] Tests unitaires ChatSession (5 tests)

### Exemples de questions supportées
- [x] "Quelle est notre marge moyenne ce mois-ci ?"
- [x] "Quelles recettes ont un food cost > 35% ?"
- [x] "Y a-t-il des anomalies d'achat cette semaine ?"
- [x] "Quel est notre CA total ce mois-ci ?"
- [x] "Quelles recettes devrais-je optimiser en priorité ?"

---

## Phase 4 — Frontend ✅

### Dashboard
- [x] KPI cards : food cost moyen, CA du mois, couverts, recettes sous objectif
- [x] Graphique ventes journalières (Recharts LineChart)
- [x] Graphique food cost ratio par recette (BarChart, rouge/vert selon objectif)
- [x] Loading state + error state

### Anomaly Panel
- [x] Tableau des achats suspects avec badge de sévérité (Modérée/Élevée/Critique)
- [x] Filtre par période (7/30/90 jours)
- [x] Error state affiché en UI

### Forecast View
- [x] Sélecteur de recette
- [x] Graphique projection 30 jours avec intervalle de confiance (deux Area stackées)
- [x] RMSE du modèle affiché
- [x] Empty state si données insuffisantes

### Chat Interface
- [x] Interface conversationnelle (style ChatGPT)
- [x] Suggestions de questions cliquables
- [x] Rendu Markdown des réponses LLM

---

## Phase 5 — Polish & Sécurité ✅

### Documentation
- [x] README.md complet avec architecture diagram ASCII
- [x] CLAUDE.md — guide développement
- [x] `notebooks/exploration.ipynb` — EDA + justification des choix de modèles
- [x] Makefile avec toutes les commandes utiles
- [ ] Screenshots / GIF demo dans le README

### Sécurité & Configuration
- [x] `.gitignore` (protège .env, __pycache__, *.joblib, node_modules)
- [x] CORS configurable via `ALLOWED_ORIGINS` env var
- [x] Pas de données personnelles dans le seed
- [x] Validation des inputs (Pydantic v2 everywhere)
- [x] Rate limiting sur le chat endpoint
- [x] Utilisateur non-root dans le Dockerfile backend
- [x] `.dockerignore` backend + frontend

### Persistance des modèles ML
- [x] Volume Docker `models_cache` pour anomaly + forecast models
- [x] `MODEL_DIR` configurable via env var

### Tests
- [x] test_anomaly_detector.py (3 tests)
- [x] test_demand_forecaster.py (5 tests)
- [x] test_margin_optimizer.py (2 tests)
- [x] test_assistant.py (5 tests)
- [ ] Tests API intégration (endpoints bout-à-bout)
- [ ] Coverage > 70% validé

### Déploiement optionnel
- [x] Guide de déploiement Railway + Render dans le README
- [ ] Deploy effectif + lien live dans le README

---

## Backlog (nice-to-have)
- [ ] Alertes email quand anomalie détectée (simulation)
- [ ] Export PDF du rapport mensuel
- [ ] Multi-restaurant support
- [ ] Websocket pour le chat (streaming LLM response)
- [ ] Tests API intégration avec base de données de test
