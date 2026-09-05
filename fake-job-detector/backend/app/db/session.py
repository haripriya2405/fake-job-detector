from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
from app.core.logging import logger

db_url = settings.DATABASE_URL
engine_kwargs = {"pool_pre_ping": True}

if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Production PostgreSQL connection pooling configuration
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
    })

try:
    engine = create_engine(db_url, **engine_kwargs)
    with engine.connect() as conn:
        pass
except Exception as e:
    logger.warning(f"Could not connect to primary DATABASE_URL ({e}). Falling back to local SQLite database.")
    fallback_url = "sqlite:///./app_local.db"
    engine = create_engine(
        fallback_url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
