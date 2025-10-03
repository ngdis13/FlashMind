from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TopicBase(BaseModel):
    """Базовая схема для темы
    Args:
        BaseModel (_type_): унаследованный класс BaseModel
    """

    name: str
    description: Optional[str]


class TopicCreate(TopicBase):
    """Схема для создания новой темы"""

    pass


class TopicUpdate(BaseModel):
    """Схема для обновления текущей темы"""

    name: Optional[str] = None
    description: Optional[str] = None


class TopicRead(TopicBase):
    """Схема для чтения темы (ответа API). Включает ID и временные метки."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
