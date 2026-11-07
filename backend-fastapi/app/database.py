import os
from pathlib import Path
from app.settings import settings
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)


# Base=declarative_base()
engine=create_engine(url=settings.DB_CONNECTION)
LocalSession=sessionmaker(bind=engine)

def get_db():
    session=LocalSession()
    try:
        yield session
    finally:
        session.close()



SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    with engine.connect() as conn:
        return conn.execute(text("SELECT version()")).scalar_one()