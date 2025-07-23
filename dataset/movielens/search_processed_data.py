import json
from typing import List, Set

from app.models.movies.search import Movie, MovieSearchQuery, MovieSearchResponsePaginated
from app.utils.constants import MOVIELENS_PROCESSED_DATA_FILEPATH
from app.utils.logger import get_logger

logger = get_logger(__name__)


def load_processed_data(filepath: str) -> List[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def match_filters(movie: dict, query: MovieSearchQuery, skip_ids: Set[str]) -> bool:
    movie_id = movie.get("movie_id")
    if movie_id in skip_ids:
        return False

    title = movie.get("title", "")
    genre = movie.get("genre", "")
    tags = movie.get("tags", [])
    avg_rating = movie.get("average_rating")

    if query.title and query.title.lower() not in title.lower():
        return False
    if query.genre and (not genre or query.genre.lower() not in genre.lower()):
        return False
    if query.tags:
        if not tags:
            return False
        tags_lower = [tag.lower() for tag in tags]
        if not any(tag.lower() in tags_lower for tag in query.tags):
            return False
    if query.min_average_rating and (
        not avg_rating or float(avg_rating) < query.min_average_rating
    ):
        return False
    if query.max_average_rating and (
        not avg_rating or float(avg_rating) > query.max_average_rating
    ):
        return False

    return True


def filter_and_convert_movies(
    raw_data: List[dict],
    query: MovieSearchQuery,
    skip_ids: Set[str],
    limit: int
) -> List[Movie]:
    filtered = []
    for item in raw_data:
        if match_filters(item, query, skip_ids):
            filtered.append(Movie(**item))
            if len(filtered) >= limit:
                break
    return filtered


def sort_movies(movies: List[Movie], sort_by: str, order: str) -> List[Movie]:
    if sort_by == "average_rating":
        reverse = order == "desc"
        movies.sort(
            key=lambda m: float(m.average_rating) if m.average_rating else -1,
            reverse=reverse
        )
    return movies


def paginate_movies(
    movies: List[Movie], page: int, page_size: int
) -> List[Movie]:
    start = (page - 1) * page_size
    end = start + page_size
    return movies[start:end]


def search_processed_data(
    query: MovieSearchQuery, skip_ids: Set[str], limit: int = 1000
) -> MovieSearchResponsePaginated:
    try:
        raw_data = load_processed_data(MOVIELENS_PROCESSED_DATA_FILEPATH)
        filtered = filter_and_convert_movies(raw_data, query, skip_ids, limit)
        sorted_movies = sort_movies(filtered, query.sort_by, query.sort_order)

        paginated = paginate_movies(sorted_movies, query.page, query.page_size)

        return MovieSearchResponsePaginated(
            total=len(filtered),
            page=query.page,
            page_size=query.page_size,
            movies=paginated
        )

    except Exception as e:
        logger.error(f"Error in search_processed_data: {str(e)}")
        raise Exception("Failed to search processed dataset.")
