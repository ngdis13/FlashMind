from datetime import datetime

from starlette import status


def create_test_topic(client, name="Test Topic", description="Description for topic"):
    """Функция для создания темы, чтобы не дублировать код

    Args:
        client (_type_): _description_
        name (str, optional): _description_. Defaults to "Test Topic".
        description (str, optional): _description_. Defaults to "Description for topic".

    Returns:
        json: объект с темой
    """
    topic_data = {"name": name, "description": description}
    response = client.post("/topics", json=topic_data)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


def create_test_flashcard(client, topic_id, question="Test Question", answer="Test Answer", difficulty_level=1):
    """Функция для создания карточки (чтобы не дублировать код)

    Args:
        client (_type_): _description_
        topic_id (_type_): _description_
        question (str, optional): _description_. Defaults to "Test Question".
        answer (str, optional): _description_. Defaults to "Test Answer".
        difficulty_level (int, optional): _description_. Defaults to 1.

    Returns:
        _type_: _description_
    """
    flashcard_data = {
        "question": question,
        "answer": answer,
        "difficulty_level": difficulty_level,
    }
    response = client.post(f"/topics/{topic_id}/flashcards", json=flashcard_data)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


# ___________________________________________________________________________________________


# Тестирование тем
def test_read_topics(client):
    """Проверяет, что GET /topics возвращает пустой список, когда нет тем."""
    response = client.get("/topics")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_create_topic(client):
    """Проверяет, что POST /topics создает новую тему"""
    topic_data = {"name": "Новая тема", "description": "Описание новой темы"}
    response = client.post("/topics", json=topic_data)
    assert response.status_code == status.HTTP_201_CREATED

    created_topic = response.json()

    assert created_topic["name"] == topic_data["name"]
    assert created_topic["description"] == topic_data["description"]
    assert isinstance(created_topic["id"], int)
    assert "created_at" in created_topic
    assert "updated_at" in created_topic

    datetime.fromisoformat(created_topic["created_at"])
    datetime.fromisoformat(created_topic["updated_at"])


def test_read_topics_after_creation(client):
    """Проверяет, что GET /topics возвращает созданную тему"""
    topic1 = create_test_topic(client, "Первая тема", "Описание первой темы")
    topic2 = create_test_topic(client, "Вторая тема", "Описание второй темы")

    response = client.get("/topics")

    assert response.status_code == status.HTTP_200_OK
    topics = response.json()
    assert len(topics) == 2
    assert any(t["id"] == topic1["id"] for t in topics)
    assert any(t["id"] == topic2["id"] for t in topics)


def test_read_topic(client):
    """Функция для проверки чтения одной темы по ID"""
    created_topic = create_test_topic(client, "Математический анализ", "Основные понятия математического анализа")
    topic_id = created_topic["id"]

    response = client.get(f"/topics/{topic_id}")
    assert response.status_code == status.HTTP_200_OK
    read_topic = response.json()
    assert read_topic["id"] == topic_id
    assert read_topic["name"] == created_topic["name"]
    assert read_topic["description"] == created_topic["description"]
