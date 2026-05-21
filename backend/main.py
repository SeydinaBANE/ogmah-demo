from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.chat import limiter
from app.api import anomalies, chat, forecast, recipes, sales
from app.database import engine, settings
from app.models.db_models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="OgmahDemo — Restaurant AI API",
    description="Anomaly detection, demand forecasting, margin analysis, and LLM assistant for restaurants.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(recipes.router)
app.include_router(anomalies.router)
app.include_router(forecast.router)
app.include_router(sales.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ogmah-demo"}
