from datetime import datetime

from pydantic import BaseModel


class Topic(BaseModel):
    id: int
    name: str = "Math"
    description: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
