from typing import List, Optional
from pydantic import BaseModel, Field

class Movie(BaseModel):
    movie_id: str = Field(..., description="Unique identifier for the movie")
    title: str = Field(..., description="Title of the movie")
    genre: Optional[str] = Field(None, description="Genre of the movie (optional)")
    average_rating: Optional[str] = Field(None, description="Average user rating (optional)")
    tags: Optional[List[str]] = Field(None, description="List of tags/keywords (optional)")
    