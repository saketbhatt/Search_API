from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from app.models.movies.movie import Movie


class MovieSearchQuery(BaseModel):
    title: Optional[str] = Field(
        default=None,
        description="Search by movie title (case-insensitive)"
    )
    genre: Optional[str] = Field(
        default=None,
        description="Filter by genre"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more tags",
        example=["sci-fi", "classic"]
    )

    min_average_rating: Optional[float] = Field(
        default=None,
        ge=0,
        le=5,
        description="Minimum average rating (0 to 5)"
    )
    max_average_rating: Optional[float] = Field(
        default=None,
        ge=0,
        le=5,
        description="Maximum average rating (0 to 5)"
    )

    sort_by: Optional[Literal["average_rating"]] = Field(
        default=None,
        description="Sort by field (currently supports: average_rating)"
    )
    sort_order: Optional[Literal["asc", "desc"]] = Field(
        default="desc",
        description="Sort order: asc or desc (default: desc)"
    )

    page: Optional[int] = Field(
        default=1,
        ge=1,
        description="Page number (default: 1)"
    )
    page_size: Optional[int] = Field(
        default=10,
        ge=1,
        le=100,
        description="Movies per page (default: 10)"
    )


class MovieSearchResponsePaginated(BaseModel):
    total: int = Field(..., description="Total number of matching movies")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    movies: List[Movie] = Field(..., description="List of movies in the current page")
