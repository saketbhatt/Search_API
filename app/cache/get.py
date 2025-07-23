from app.cache.store import MOVIES, MOVIES_LOCK
from app.utils.logger import get_logger

logger = get_logger(__name__)

def get_from_cache(key):
    try:
        with MOVIES_LOCK:
            value = MOVIES[key]
            return value
    except Exception as e:
        logger.error(f"Error getting value from cache: {e}")
