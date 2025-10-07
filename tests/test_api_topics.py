from datetime import datetime

from starlette import status


def create_test_topic(client, name="Тестовая тема", description="Тестовое описание"):
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


# ___________________________________________________________________________________________


def test_read_topics_empty(client):
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
    """Функция для проверки чтения одной темы по ID GET /topics/{topic_id}"""
    created_topic = create_test_topic(client, "Математический анализ", "Основные понятия математического анализа")
    topic_id = created_topic["id"]

    response = client.get(f"/topics/{topic_id}")
    assert response.status_code == status.HTTP_200_OK
    read_topic = response.json()
    assert read_topic["id"] == topic_id
    assert read_topic["name"] == created_topic["name"]
    assert read_topic["description"] == created_topic["description"]


def read_topic_not_found(client):
    """Проверяет, что GET /topics/{id} возвращает 404 для несуществующей темы"""
    response = client.get("/topics/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Тема не найдена"


def test_update_topic(client):
    """Проверяет обновление существующей темы"""
    created_topic = create_test_topic(client, "Английский язык B2", "1000 слов на английском языке")
    topic_id = created_topic["id"]

    updated_data = {"name": "Английский язык C1", "description": "300 слов на английском языке"}
    response = client.patch(f"/topics/{topic_id}", json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    updated_topic = response.json()
    assert updated_topic["id"] == topic_id
    assert updated_topic["name"] == updated_data["name"]
    assert updated_topic["description"] == updated_data["description"]
    # Проверяем, что updated_at изменился, а created_at остался прежним
    assert updated_topic["created_at"] == created_topic["created_at"]
    assert datetime.fromisoformat(updated_topic["updated_at"]) > datetime.fromisoformat(created_topic["updated_at"])


def test_update_topic_not_found(client):
    """Проверяет, что PATCH /topics/{id} возвращает 404 для несуществующей темы."""
    updated_data = {"name": "Несуществующая тема", "description": "Описание несуществующей темы"}
    response = client.patch("/topics/999999", json=updated_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Тема не найдена"


def test_delete_topic(client):
    """Проверяет, что DELETE /topics/{topic_id} удаляет тему"""
    created_topic = create_test_topic(client, "Тема для удаления", "Описание темы для удаления")
    topic_id = created_topic["id"]

    response = client.delete(f"/topics/{topic_id}")
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"status": "accepted"}

    # Проверка, что тема действительно удалена
    response = client.get(f"/topics/{topic_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_topic_not_found(client):
    """Проверяет, что DELETE /topics/{topic_id} возвращает 404 для несуществующей темы"""
    response = client.delete("/topics/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Тема не найдена"
