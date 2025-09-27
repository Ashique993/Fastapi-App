from sqlmodel import SQLModel, create_engine, Session
import os

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/mydb"
)

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
