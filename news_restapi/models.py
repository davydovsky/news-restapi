from dataclasses import dataclass
from datetime import datetime


@dataclass
class Base:
    id: int
    created_date: datetime
    modified_date: datetime


@dataclass
class News(Base):
    title: str
    content: str


@dataclass
class Comment(Base):
    news_id: int
    content: str
