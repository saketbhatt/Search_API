import os
import json
import subprocess
import json
from app.cache.store import MOVIES
from app.models.movies.movie import Movie
from app.utils.logger import get_logger
from app.cache.clear import clear_cache
from app.cache.put import put_into_cache
from app.utils.constants import SYNC_MOVIES_DATA_FROM_MOVIELENS_ORIGIN_SCRIPT_PATH, DEFAULT_CACHE_SIZE

logger = get_logger(__name__)

def refresh_movies(json_path: str, limit: int = DEFAULT_CACHE_SIZE):
    try:
        if not os.path.exists(json_path):
            logger.warning(f"{json_path} not found. Attempting to run sync script...")
            result = subprocess.run(
                ["python3", SYNC_MOVIES_DATA_FROM_MOVIELENS_ORIGIN_SCRIPT_PATH],
                cwd=os.path.dirname(SYNC_MOVIES_DATA_FROM_MOVIELENS_ORIGIN_SCRIPT_PATH),
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.error(f"Sync script failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
                return
            logger.info(f"Sync script completed:\n{result.stdout}")

        with open(json_path, 'r', encoding='utf-8') as f:
            raw_movies = json.load(f)
            limited_movies = raw_movies[:limit]

            clear_cache()
            for movie in limited_movies:
                put_into_cache(movie["movie_id"], Movie(**movie))

            logger.info(f"{len(MOVIES)} movies loaded into in-memory cache.")
    except Exception as e:
        logger.error(f"Error loading movies into the cache: {e}")
