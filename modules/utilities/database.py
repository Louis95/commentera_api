"""Database module, used for various database related methods"""
import os
import logging
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

load_dotenv()


def get_db_session() -> sessionmaker:
    """Retrieves a database session and yields it"""
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


def get_environment() -> str:
    """Gets the environment from the environment variable ENV and returns local if it doesn't exist"""
    environment = os.getenv("STAGE", "local")
    valid_environments = ["local", "staging", "production"]

    if environment in valid_environments:
        return environment

    return "local"


def db_connection_string(environment=None) -> str:
    """Creates db connection string to database"""
    if environment is None:
        environment = get_environment()

    # If the environment is local, and DATABASE_URL is present, use that.
    if environment == "local":
        if "DATABASE_URL" in os.environ:
            return os.environ["DATABASE_URL"]
        raise Exception(
            "Local environment is specified but DATABASE_URL cannot be found."
        )

    # postgresql
    POSTGRESQL_HOST: str = os.environ["POSTGRESQL_HOST"]
    POSTGRESQL_PORT: str = "5432"
    # common
    DB_NAME: str = os.environ["DB_NAME"]
    USERNAME: str = os.environ["USERNAME"]
    PASSWORD: str = os.environ["PASSWORD"]

    return f"postgresql://{USERNAME}:{PASSWORD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{DB_NAME}"


DB_URL = db_connection_string()
engine = create_engine(DB_URL)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)
