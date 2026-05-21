from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://ogmah:ogmah_secret@localhost:5432/ogmah_db"
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    model_dir: str = "/app/models_cache"
    environment: str = "development"
    log_level: str = "INFO"

    model_config = {"env_file": None}  # rely on environment variables only


settings = Settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
