from fastapi import APIRouter, HTTPException, Depends
from app.models.movies.search import MovieSearchQuery, MovieSearchResponsePaginated
from app.security.auth import verify_token
from app.services.movies.search import search_movies
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/movies", tags=["Movies"])

@router.post("/search", response_model=MovieSearchResponsePaginated)
def get_searched_movies(query: MovieSearchQuery, _: None = Depends(verify_token)):
    try:
        return search_movies(query)
    except Exception as e:
        logger.error(f"Search API failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
