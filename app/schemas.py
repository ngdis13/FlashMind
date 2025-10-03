from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TopicBase(BaseModel):
    """Базовая схема для темы"""

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

    class Config:
        orm_mode = True


class FlashcardBase(BaseModel):
    """Базовая схема для карточки"""

    question: str
    answer: str
    difficulty_level: int = 1


class FlashcardCreate(FlashcardBase):
    """Базовая схема для создания карточки"""

    pass


class FlashcardUpdate(BaseModel):
    """Схема для обновления карточки"""

    topic_id: Optional[int] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    difficulty_level: Optional[int] = None
    last_reviewed_at: Optional[datetime] = None


class FlashcardRead(FlashcardBase):
    """Схема для чтения карточки"""

    id: int
    topic_id: int
    last_reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
