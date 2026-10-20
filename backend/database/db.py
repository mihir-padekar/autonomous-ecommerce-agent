from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is missing."
    )

# Standardize dialect prefix (Heroku/Neon postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )
except Exception as e:
    if "No module named 'psycopg'" in str(e) and "postgresql://" in DATABASE_URL:
        alt_url = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
        engine = create_engine(
            alt_url,
            pool_pre_ping=True,
            pool_recycle=300
        )
    else:
        raise

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
