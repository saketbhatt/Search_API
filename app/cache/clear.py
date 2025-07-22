from app.cache.store import MOVIES
from app.utils.logger import get_logger

logger = get_logger(__name__)

def clear_cache():
    try:
        MOVIES.clear()
    except Exception as e:
        logger.error(f"Error clearing the cache: {e}")
