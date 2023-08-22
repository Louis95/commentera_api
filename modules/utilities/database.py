"""Database module, used for various database related methods"""
import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
        raise OSError(
            "Local environment is specified but DATABASE_URL cannot be found.",
        )

    # postgresql
    postgresql_host: str = os.environ["POSTGRESQL_HOST"]
    postgresql_port: str = "5432"
    # common
    db_name: str = os.environ["DB_NAME"]
    username: str = os.environ["USERNAME"]
    password: str = os.environ["PASSWORD"]

    return f"postgresql://{username}:{password}@{postgresql_host}:{postgresql_port}/{db_name}"


DB_URL = db_connection_string()
engine = create_engine(DB_URL)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)
