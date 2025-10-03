from typing import List

from database.database import SimpleDB
from fastapi import FastAPI, HTTPException
from schemas import (
    TopicBase,
    TopicCreate,
    TopicRead,
    TopicUpdate,
)


db = SimpleDB()

app = FastAPI()


@app.get("/topics", response_model=List[TopicBase])
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
        raise HTTPException(status_code=404, detail="Тема не найдена")
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
        raise HTTPException(status_code=404, detail="Тема не найдена")
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
        raise HTTPException(status_code=404, detail="Тема не найдена")
    return {"status": "accepted"}
