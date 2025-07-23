from typing import Dict
from threading import Lock
from app.models.movies.movie import Movie

MOVIES: Dict[str, Movie] = {}
MOVIES_LOCK = Lock()
