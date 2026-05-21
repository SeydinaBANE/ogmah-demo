.PHONY: up down build rebuild seed logs logs-backend logs-frontend \
        shell test clean restart-backend restart-frontend help

# ── Start ──────────────────────────────────────────────────────────────────
up:
	docker-compose up

build:
	docker-compose up --build

rebuild:
	docker-compose down -v
	docker-compose up --build

# ── Stop / Clean ───────────────────────────────────────────────────────────
down:
	docker-compose down

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# ── Data ───────────────────────────────────────────────────────────────────
seed:
	docker-compose run --rm backend python -m app.data.seed

# ── Logs ───────────────────────────────────────────────────────────────────
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

# ── Dev ────────────────────────────────────────────────────────────────────
shell:
	docker-compose exec backend bash

restart-backend:
	docker-compose restart backend

restart-frontend:
	docker-compose restart frontend

# ── Tests ──────────────────────────────────────────────────────────────────
test:
	docker-compose run --rm backend pytest -v --cov=app --cov-report=term-missing

# ── Help ───────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  make build            → démarrer (avec rebuild des images)"
	@echo "  make up               → démarrer (images existantes)"
	@echo "  make rebuild          → tout repartir à zéro (down -v + build)"
	@echo "  make down             → arrêter les conteneurs"
	@echo "  make clean            → arrêter + supprimer volumes + prune"
	@echo "  make seed             → injecter les données de démo"
	@echo "  make logs             → suivre tous les logs"
	@echo "  make logs-backend     → logs backend uniquement"
	@echo "  make logs-frontend    → logs frontend uniquement"
	@echo "  make shell            → ouvrir un shell dans le backend"
	@echo "  make restart-backend  → redémarrer le backend"
	@echo "  make test             → lancer les tests pytest"
	@echo ""
