import pytest
from fastapi.testclient import TestClient

from app.database.database import SimpleDB
from app.main import app


@pytest.fixture(name="test_db")
def test_db_fixture():
    """
    Создает новый экземпляр SimpleDB, использующий базу данных в памяти,
    для каждого теста. Это обеспечивает изоляцию тестов.
    """
    db_instance = SimpleDB(db_file=":memory:", check_same_thread=False)
    db_instance.create_tables()
    yield db_instance
    db_instance.close()


@pytest.fixture(name="client")
def client_fixture(test_db, monkeypatch):
    """
    Предоставляет TestClient для вашего FastAPI приложения.
    Заменяет глобальный объект 'db' в main.py на наш тестовый экземпляр БД.
    """
    # Заменяем глобальную переменную 'db' в модуле 'main' на наш тестовый экземпляр БД.
    # Это гарантирует, что все роуты приложения будут использовать нашу тестовую БД.
    monkeypatch.setattr("app.main.db", test_db)

    with TestClient(app) as test_client:
        yield test_client
