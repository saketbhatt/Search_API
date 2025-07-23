from app.cache.store import MOVIES, MOVIES_LOCK
from app.utils.logger import get_logger

logger = get_logger(__name__)

def put_into_cache(key, value):
    try:
        with MOVIES_LOCK:
            MOVIES[key] = value
    except Exception as e:
        logger.error(f"Error putting into cache: {e}")
