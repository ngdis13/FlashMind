from datetime import datetime

from starlette import status

from tests.test_api_topics import create_test_topic


def create_test_flashcard(client, topic_id, question="Тестовый вопрос", answer="Тестовый ответ", difficulty_level=1):
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


def test_read_flashcard_empty(client):
    """Проверяет, что GET /flashcards возвращает пустой список, когда нет карточек"""
    response = client.get("/flashcards")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_create_flashcard(client):
    """Проверяет создание новой карточки по существующей теме с помощью POST /topics/{topic_id}/flashcards"""
    topic = create_test_topic(client)
    flashcard_data = {
        "question": "Что такое FastAPI?",
        "answer": "FastAPI — это высокопроизводительный веб-фреймворк на Python для создания API, который обеспечивает высокую скорость работы, автоматическую валидацию данных с помощью стандартных аннотаций типов Python и автоматическую генерацию документации, что делает разработку веб-сервисов быстрее и проще",
        "difficulty_level": 1,
    }

    response = client.post(f"/topics/{topic['id']}/flashcards", json=flashcard_data)
    assert response.status_code == status.HTTP_201_CREATED
    created_flashcard = response.json()
    assert created_flashcard["topic_id"] == topic["id"]
    assert created_flashcard["question"] == flashcard_data["question"]
    assert created_flashcard["answer"] == flashcard_data["answer"]
    assert created_flashcard["difficulty_level"] == flashcard_data["difficulty_level"]
    assert isinstance(created_flashcard["id"], int)
    assert "last_reviewed_at" in created_flashcard
    assert "created_at" in created_flashcard
    assert "updated_at" in created_flashcard


def test_create_flashcard_with_non_existent_topic(client):
    """Проверяет, что POST "/topics/topic_id/flashcards для несуществующей темы возвращает 404"""
    flashcard_data = {"question": "Вопрос", "answer": "Ответ", "difficulty_level": 1}

    response = client.post("/topics/9999/flashcards", json=flashcard_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Тема не найдена"


def test_read_flashcards_by_topic_id(client):
    """Проверяет что GET /topics/{topic_id}/flashcards читает карточки по ID темы"""
    topic1 = create_test_topic(client, "Математический анализ")
    topic2 = create_test_topic(client, "Линейная алгебра")

    flashcard1_topic1 = create_test_flashcard(
        client,
        topic1["id"],
        "Что такое предел последовательности?",
        "Это число, к которому все более отдаленные члены последовательности приближаются сколь угодно близко",
    )
    flashcard2_topic1 = create_test_flashcard(
        client,
        topic1["id"],
        "ЧТо такое непрерывная функция?",
        "функция, значения которой меняются без резких скачков (разрывов), а малые изменения аргумента приводят к малым изменениям значения функции.",
    )
    flashcard1_topic2 = create_test_flashcard(
        client,
        topic2["id"],
        "Что такое определитель?",
        "Это числовая характеристика квадратной матрицы, получаемая по определённому правилу из её элементов",
    )

    response = client.get(f"/topics/{topic1['id']}/flashcards")
    assert response.status_code == status.HTTP_200_OK
    flashcards = response.json()
    assert len(flashcards) == 2
    assert any(f["id"] == flashcard1_topic1["id"] for f in flashcards)
    assert any(f["id"] == flashcard2_topic1["id"] for f in flashcards)
    # Проверка, что карточка из второй темы не попала в первую
    assert not any(f["id"] == flashcard1_topic2["id"] for f in flashcards)


def test_read_flashcards_by_non_existent_topic_id(client):
    """Проверяет, что GET /topics/{topic_id}/flashcards возвращает 404 для несуществующей темы."""
    response = client.get("/topics/99999/flashcards")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Тема не найдена"


def test_read_all_flashcards(client):
    """Проверяет чтение всех карточек"""
    topic = create_test_topic(client)
    flashcard1 = create_test_flashcard(client, topic["id"], "Первый вопрос", "Первый ответ")
    flashcard2 = create_test_flashcard(client, topic["id"], "Второй вопрос", "Второй ответ")

    response = client.get("/flashcards")
    assert response.status_code == status.HTTP_200_OK
    flashcards = response.json()
    assert len(flashcards) == 2
    assert any(f["id"] == flashcard1["id"] for f in flashcards)
    assert any(f["id"] == flashcard2["id"] for f in flashcards)


def test_read_flashcard(client):
    """Проверяет что GET /flashcards/{flashcard_id} возвращает карточку по ID"""
    topic = create_test_topic(client)
    created_flashcards = create_test_flashcard(client, topic["id"], "Что такое линукс?", "Это ядро")
    flashcard_id = created_flashcards["id"]

    response = client.get(f"/flashcards/{flashcard_id}")
    assert response.status_code == status.HTTP_200_OK
    read_flashcard = response.json()
    assert read_flashcard["id"] == flashcard_id
    assert read_flashcard["question"] == created_flashcards["question"]
    assert read_flashcard["answer"] == created_flashcards["answer"]


def test_read_flashcard_not_found(client):
    """Проверяет, что GET /flashcards/{flashcard_id} возвращает 404 с несуществующей темой"""
    response = client.get("/flashcards/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Карточка не найдена"


def test_update_flashcard(client):
    """Проверяет, что PATCH /flashcards/{flashcard_id} обновляет существующую карточку"""
    topic = create_test_topic(client)
    created_flashcard = create_test_flashcard(client, topic["id"], "Что такое линукс?", "Это ядро")
    flashcard_id = created_flashcard["id"]

    update_data = {
        "question": "Что такое командная строка?",
        "answer": "Это текстовый интерфейс, который позволяет управлять компьютером и программами с помощью текстовых команд, а не графического меню",
        "difficulty_level": 3,
        "last_reviewed_at": datetime.now().isoformat(),
        "topic_id": topic["id"],  # topic_id тоже может быть обновлен
    }

    response = client.patch(f"/flashcards/{flashcard_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    updated_flashcard = response.json()
    assert updated_flashcard["id"] == flashcard_id
    assert updated_flashcard["question"] == update_data["question"]
    assert updated_flashcard["answer"] == update_data["answer"]
    assert updated_flashcard["difficulty_level"] == update_data["difficulty_level"]
    assert updated_flashcard["last_reviewed_at"] == update_data["last_reviewed_at"]
    assert updated_flashcard["created_at"] == created_flashcard["created_at"]
    assert datetime.fromisoformat(updated_flashcard["updated_at"]) > datetime.fromisoformat(
        created_flashcard["updated_at"]
    )


def test_update_flashcard_not_found(client):
    """Проверяет, что PATCH /flashcards/{id} возвращает 404 для несуществующей карточки"""
    update_data = {"question": "Обновление", "answer": "Описание"}
    response = client.patch("/flashcards/9999", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Карточка с указанным id не найдена"


def test_delete_flashcard(client):
    """Проверяет, что DELETE /flashcards/{flashcard_id} удаляет карточку по id"""
    topic = create_test_topic(client)
    created_flashcard = create_test_flashcard(client, topic["id"], "Карточка для удаления", "Описание карточки")
    flashcard_id = created_flashcard["id"]

    response = client.delete(f"/flashcards/{flashcard_id}")
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"status": "accepted"}

    # Проверка, что карточки действительно нет
    response = client.get(f"/flashcards/{flashcard_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_flashcard_not_found(client):
    """Проверяет, что DELETE /flashcards/{flashcard_id} возвращает 404 для несуществующей карточки"""
    response = client.get("/flashcards/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Карточка не найдена"
