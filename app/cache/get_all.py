from app.cache.store import MOVIES
from app.utils.logger import get_logger

logger = get_logger(__name__)

def get_all_from_cache():
    try:
        all_values = MOVIES.values()
        return all_values
    except Exception as e:
        logger.error(f"Error getting all values from cache: {e}")
