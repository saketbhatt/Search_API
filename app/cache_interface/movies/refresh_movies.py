import os
import json
import subprocess

from app.cache.store import MOVIES
from app.models.movies.movie import Movie
from app.utils.logger import get_logger
from app.cache.clear import clear_cache
from app.cache.put import put_into_cache
from app.utils.constants import SYNC_MOVIES_DATA_FROM_MOVIELENS_ORIGIN_SCRIPT_PATH, DEFAULT_CACHE_SIZE

logger = get_logger(__name__)

def run_sync_script(script_path: str) -> bool:
    """Run sync script to regenerate processed JSON data."""
    logger.warning(f"{script_path} not found. Attempting to run sync script...")

    result = subprocess.run(
        ["python3", script_path],
        cwd=os.path.dirname(script_path),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        logger.error(f"Sync script failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        return False

    logger.info(f"Sync script completed:\n{result.stdout}")
    return True


def load_movies_from_json(json_path: str, limit: int) -> list[dict]:
    """Load movies from JSON file with optional limit."""
    with open(json_path, 'r', encoding='utf-8') as f:
        raw_movies = json.load(f)
    return raw_movies[:limit]


def populate_cache(movies: list[dict]):
    """Clear and populate the in-memory cache."""
    clear_cache()
    for movie in movies:
        put_into_cache(movie["movie_id"], Movie(**movie))
    logger.info(f"{len(MOVIES)} movies loaded into in-memory cache.")


def refresh_movies(json_path: str, limit: int = DEFAULT_CACHE_SIZE):
    try:
        if not os.path.exists(json_path):
            if not run_sync_script(SYNC_MOVIES_DATA_FROM_MOVIELENS_ORIGIN_SCRIPT_PATH):
                return

        movies = load_movies_from_json(json_path, limit)
        populate_cache(movies)

    except Exception as e:
        logger.error(f"Error loading movies into the cache: {e}")
