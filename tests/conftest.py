from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from app.api.dependencies import get_db_session
from app.db.base import Base
from app.main import app


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:16", driver=None) as postgres:
        yield postgres


@pytest.fixture(scope="session")
def test_database_url(postgres_container: PostgresContainer) -> str:
    raw_url = postgres_container.get_connection_url()
    # testcontainers może zwrócić URL bez drivera, więc dokładamy SQLAlchemy dialect
    return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)


@pytest.fixture(scope="session")
def test_engine(test_database_url: str) -> Generator[Engine, None, None]:
    engine = create_engine(
        test_database_url,
        pool_pre_ping=True,
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database(test_engine: Engine) -> Generator[None, None, None]:
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def testing_session_factory(test_engine: Engine) -> sessionmaker:
    return sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )


def _truncate_all_tables(engine: Engine) -> None:
    table_names = [table.name for table in Base.metadata.sorted_tables]
    if not table_names:
        return
    with engine.begin() as connection:
        quoted_names = ", ".join(f'"{name}"' for name in table_names)
        connection.execute(text(f"TRUNCATE TABLE {quoted_names} RESTART IDENTITY CASCADE"))


@pytest.fixture(autouse=True)
def clean_database(test_engine: Engine) -> Generator[None, None, None]:
    _truncate_all_tables(test_engine)
    yield
    _truncate_all_tables(test_engine)


@pytest.fixture
def db_session(testing_session_factory: sessionmaker) -> Generator[Session, None, None]:
    session = testing_session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(testing_session_factory: sessionmaker) -> Generator[TestClient, None, None]:
    def override_get_db_session() -> Generator[Session, None, None]:
        session = testing_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
