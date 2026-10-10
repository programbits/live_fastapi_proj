"""Database configuration.

SQLite is created automatically for local development. On Render, render.yaml
points DATABASE_URL at a persistent disk so blog data survives restarts/deploys.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
_url = make_url(DATABASE_URL)

# Create the parent directory when a file-based SQLite database uses a custom path.
if _url.drivername.startswith("sqlite") and _url.database not in (None, ":memory:"):
    db_path = Path(_url.database)
    if db_path.is_absolute():
        db_path.parent.mkdir(parents=True, exist_ok=True)

_engine_kwargs = {"pool_pre_ping": True}
if _url.drivername.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
