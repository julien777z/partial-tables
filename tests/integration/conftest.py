import asyncio
import time
from typing import Final
import pytest
import pytest_asyncio
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Engine
from tests.integration.database.sqlalchemy_tables import SQLAlchemyBusinessBase
from tests.integration.database.sqlmodel_tables import SQLModelBusinessBase

DATABASE_CONNECTION_MAX_TRIES: Final[int] = 10


@pytest_asyncio.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
def start_docker_services(docker_services):
    """Start the Docker services."""


@pytest.fixture(scope="session", autouse=True)
def docker_setup():
    """Stop the stack before starting a new one."""

    return ["down -v", "up --build -d"]


@pytest.fixture(scope="session", autouse=True)
def sqlalchemy_connect_url() -> str:
    """Return the SQLAlchemy connection URL."""

    return "postgresql://admin:admin123@localhost:5432/partial_table"


@pytest.fixture(scope="session", autouse=True)
def wait_for_database(sqlalchemy_connect_url: str) -> None:
    """Wait for the database to be ready."""

    tries_remaining = DATABASE_CONNECTION_MAX_TRIES

    while not database_exists(sqlalchemy_connect_url):
        tries_remaining -= 1

        if not tries_remaining:
            raise RuntimeError("Failed to connect to the database")

        time.sleep(1)


@pytest.fixture(scope="function")
def create_session(
    engine: Engine,
    sqlalchemy_connect_url: str,
    wait_for_database,
) -> Session:
    """Create the database and tables."""

    sessionmaker_ = sessionmaker(bind=engine)
    session = sessionmaker_()

    if not database_exists(sqlalchemy_connect_url):
        create_database(sqlalchemy_connect_url)

    return session


@pytest.fixture(scope="function")
def sqlalchemy_session(
    create_session: Session,
    engine: Engine,
) -> Session:
    """Create a SQLAlchemy engine."""

    SQLAlchemyBusinessBase.metadata.drop_all(engine)  # start from scratch
    SQLAlchemyBusinessBase.metadata.create_all(engine)  # create tables

    yield create_session

    create_session.close()


@pytest.fixture(scope="function")
def sqlmodel_session(
    create_session: Session,
    engine: Engine,
) -> Session:
    """Create a SQLModel engine."""

    SQLModelBusinessBase.metadata.drop_all(engine)  # start from scratch
    SQLModelBusinessBase.metadata.create_all(engine)  # create tables

    yield create_session

    create_session.close()
