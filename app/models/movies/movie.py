from pydantic import BaseModel
from typing import Optional, List

class Movie(BaseModel):
    movie_id: str
    title: str
    genre: Optional[str] = None
    average_rating: Optional[str] = None
    tags: Optional[List[str]] = None
    