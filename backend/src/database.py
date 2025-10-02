# database.py

import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/mydb"
)

# Configure engine with echo for SQL debugging
engine = create_engine(DATABASE_URL, echo=True)


def init_db() -> None:
    """Create all tables in the database."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Yield a database session to use with FastAPI dependencies.
    """
    with Session(engine) as session:
        yield session
