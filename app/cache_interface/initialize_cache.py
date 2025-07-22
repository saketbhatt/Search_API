import json
from app.cache.store import MOVIES
from app.models.movies.movie import Movie
from app.utils.logger import get_logger
from app.utils.constants import MOVIELENS_PROCESSED_DATA_FILEPATH, DEFAULT_CACHE_SIZE
from app.cache_interface.movies.refresh_movies import refresh_movies

logger = get_logger(__name__)

def initialize_cache(limit: int = DEFAULT_CACHE_SIZE):
    try:
        refresh_movies(MOVIELENS_PROCESSED_DATA_FILEPATH)
        logger.info(f"{len(MOVIES)} movies loaded into the cache.")

    except Exception as e:
        logger.error(f"Error initialising the cache. {e}")
