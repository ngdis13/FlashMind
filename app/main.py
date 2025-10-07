from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette import status

from app.database.database import SimpleDB
from app.schemas import (
    FlashcardCreate,
    FlashcardRead,
    FlashcardUpdate,
    TopicCreate,
    TopicRead,
    TopicUpdate,
)


db = SimpleDB()
app = FastAPI()


# -- Обработка исключений --
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Обработчик для всех остальных необработанных исключений (например, ZeroDivisionError, ValueError).
    Возвращает 500 с кастомным JSON-форматом.
    """
    reason_detail = str(exc)

    if not reason_detail:
        reason_detail = "Произошла непредвиденная ошибка сервера."

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"status": 500, "reason": reason_detail}
    )


@app.get("/topics", response_model=List[TopicRead])
async def read_topics():
    """Функция для чтения всех существующих тем
    Returns:
        List[TopicBase]: Pydantic-модель, представляющая все существующие темы
    """
    topics = db.get_all_topics()
    return [
        TopicRead(id=topic[0], name=topic[1], description=topic[2], created_at=topic[3], updated_at=topic[4])
        for topic in topics
    ]


@app.get("/topics/{topic_id}", response_model=TopicRead)
async def read_topic(topic_id: int):
    """Функция возвращающая тему по его id номеру

    Args:
        topic_id (int): id необходимой темы

    Raises:
        HTTPException: ошибка в случае если тема не найдена(не существует)

    Returns:
        TopicRead: Pydantic-модель, представляющая тему с указанным id
    """
    topic = db.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")
    return TopicRead(id=topic[0], name=topic[1], description=topic[2], created_at=topic[3], updated_at=topic[4])


@app.post("/topics", response_model=TopicRead, status_code=201)
async def create_topics(topic: TopicCreate):
    """Функция для создания новой темы

    Args:
        topic (TopicCreate): Pydantic-модель, содержащая данные для новой темы.

    Returns:
        TopicRead: Pydantic-модель, представляющая созданную тему.
    """
    new_topic = db.create_topic(topic.name, topic.description)
    return TopicRead(
        id=new_topic[0], name=new_topic[1], description=new_topic[2], created_at=new_topic[3], updated_at=new_topic[4]
    )


@app.patch("/topics/{topic_id}", response_model=TopicRead)
async def update_topic(topic_id: int, topic_update: TopicUpdate):
    """Функция, обновляющая существующую тему

    Args:
        topic_id (int): id темы
        topic_update (TopicUpdate): Pydantic-модель, содержащая новые данные для темы

    Raises:
        HTTPException: генерирует ошибку, если такой темы не существует

    Returns:
        TopicRead: Pydantic-модель, представляющая обновленную тему
    """
    topic = db.update_topic(topic_id, topic_update.name, topic_update.description)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")
    return TopicRead(id=topic[0], name=topic[1], description=topic[2], created_at=topic[3], updated_at=topic[4])


@app.delete("/topics/{topic_id}", status_code=202)
async def delete_topic(topic_id: int):
    """Функция, удаляющая тему по id

    Args:
        topic_id (int): id темы

    Raises:
        HTTPException: генерирует ошибку, если такой темы не существует

    Returns:
        object: информирование о успешном удалении
    """
    if not db.delete_topic(topic_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")
    return {"status": "accepted"}


@app.get("/flashcards", response_model=List[FlashcardRead])
async def read_flashcards():
    """Функция для чтения всех существующих карточек

    Returns:
        List[FlashcardRead]: Pydantic модель со списком всех существующих карточек
    """
    flashcards = db.get_all_flashcards()
    return [
        FlashcardRead(
            id=flashcard[0],
            topic_id=flashcard[1],
            question=flashcard[2],
            answer=flashcard[3],
            difficulty_level=flashcard[4],
            last_reviewed_at=flashcard[5],
            created_at=flashcard[6],
            updated_at=flashcard[7],
        )
        for flashcard in flashcards
    ]


@app.get("/flashcards/{flashcard_id}", response_model=FlashcardRead)
async def read_flashcard(flashcard_id: int):
    """Функция для чтения карточки по id

    Args:
        flashcard_id (int): id карточки

    Raises:
        HTTPException: генерируется в случае, если карточка не найдена

    Returns:
        FlashcardRead: Pydantic модель с карточкой
    """
    flashcard = db.get_flashcard_by_id(flashcard_id)
    if not flashcard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Карточка не найдена")
    return FlashcardRead(
        id=flashcard_id,
        topic_id=flashcard[1],
        question=flashcard[2],
        answer=flashcard[3],
        difficulty_level=flashcard[4],
        last_reviewed_at=flashcard[5],
        created_at=flashcard[6],
        updated_at=flashcard[7],
    )


@app.post("/topics/{topic_id}/flashcards", response_model=FlashcardRead, status_code=201)
async def create_flashcard(topic_id: int, flashcard: FlashcardCreate):
    """Функция для создания новой карточки по определенной теме

    Args:
        topic_id (int): id темы карточки
        flashcard (FlashcardCreate): данные для новой карточки

    Raises:
        HTTPException: генерируется в случае, если тема не найдена

    Returns:
        FlashcardRead: Pydantic модель с карточкой
    """
    topic = db.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")
    new_flashcard = db.create_flashcard(topic_id, flashcard.question, flashcard.answer, flashcard.difficulty_level)
    return FlashcardRead(
        id=new_flashcard[0],
        topic_id=new_flashcard[1],
        question=new_flashcard[2],
        answer=new_flashcard[3],
        difficulty_level=new_flashcard[4],
        last_reviewed_at=new_flashcard[5],
        created_at=new_flashcard[6],
        updated_at=new_flashcard[7],
    )


@app.get("/topics/{topic_id}/flashcards", response_model=List[FlashcardRead])
async def read_flashcards_by_topic_id(topic_id: int):
    """Функция для получения всех карточек по определенной теме

    Args:
        topic_id (int): id темы

    Raises:
        HTTPException: генерируется в случае, если тема не найдена

    Returns:
        List[FlashcardRead]: Pydantic модель со всеми карточками по запрошенной теме
    """
    topic = db.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")
    flashcards = db.get_flashcards_by_topic(topic_id)
    return [
        FlashcardRead(
            id=flashcard[0],
            topic_id=flashcard[1],
            question=flashcard[2],
            answer=flashcard[3],
            difficulty_level=flashcard[4],
            last_reviewed_at=flashcard[5],
            created_at=flashcard[6],
            updated_at=flashcard[7],
        )
        for flashcard in flashcards
    ]


@app.patch("/flashcards/{flashcard_id}", response_model=FlashcardRead)
async def update_flashcard(flashcard_id: int, flashcard_update: FlashcardUpdate):
    flashcard = db.update_flashcard(
        flashcard_id,
        topic_id=flashcard_update.topic_id,
        question=flashcard_update.question,
        answer=flashcard_update.answer,
        difficulty_level=flashcard_update.difficulty_level,
        last_reviewed_at=flashcard_update.last_reviewed_at,
    )
    if not flashcard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Карточка с указанным id не найдена")

    last_reviewed_at_val = None
    if flashcard[5]:
        try:
            last_reviewed_at_val = datetime.fromisoformat(flashcard[5])
        except ValueError:
            print(f"Warning: Could not parse last_reviewed_at: {flashcard[5]} for flashcard ID {flashcard[0]}")
            last_reviewed_at_val = None

    return FlashcardRead(
        id=flashcard[0],
        topic_id=flashcard[1],
        question=flashcard[2],
        answer=flashcard[3],
        difficulty_level=flashcard[4],
        last_reviewed_at=last_reviewed_at_val,
        created_at=flashcard[6],
        updated_at=flashcard[7],
    )


@app.delete("/flashcards/{flashcard_id}", status_code=202)
async def delete_flashcard(flashcard_id: int):
    """Функция для удаления карточки по id

    Args:
        flashcard_id (int): id карточки

    Raises:
        HTTPException: генерируется, если карточка не была найдена

    Returns:
        object: сообщение об успехе удаления карточки
    """
    if not db.delete_flashcard(flashcard_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Карточка не найдена")
    return {"status": "accepted"}
