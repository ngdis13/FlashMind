from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Topic(BaseModel):
    """Базовая схема для темы
    Args:
        BaseModel (_type_): унаследованный класс BaseModel
    """

    id: int
    name: str = "Math"
    description: Optional[str]


class TopicCreate(Topic):
    """Схема для создания новой темы"""

    pass


class TopicUpdate(Topic):
    """Схема для обновления текущей темы"""

    name: Optional[str] = Field(example="Высшая математика")
    description: Optional[str] = Field(example="Уравнения прямой")


class TopicRead(Topic):
    """Схема для чтения темы (ответа API). Включает ID и временные метки."""

    id: int = Field(..., example=1)
    created_at: datetime = Field(default_factory=datetime.now, example="2023-10-27T10:00:00.000Z")
    updated_at: datetime = Field(default_factory=datetime.now, example="2023-10-27T10:00:00.000Z")

    model_config = ConfigDict(from_attributes=True)
