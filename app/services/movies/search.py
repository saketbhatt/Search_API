from typing import List, Set
from app.models.movies.search import Movie, MovieSearchResponsePaginated, MovieSearchQuery
from app.cache.get_all import get_all_from_cache
from app.utils.logger import get_logger
from dataset.movielens.search_processed_data import search_processed_data

logger = get_logger(__name__)


def movie_matches_query(movie: Movie, query: MovieSearchQuery) -> bool:
    if query.title and query.title.lower() not in movie.title.lower():
        return False
    if query.genre and (not movie.genre or query.genre.lower() not in movie.genre.lower()):
        return False
    if query.tags:
        if not movie.tags:
            return False
        movie_tags_lower = [tag.lower() for tag in movie.tags]
        if not any(tag.lower() in movie_tags_lower for tag in query.tags):
            return False
    if query.min_average_rating and (
        not movie.average_rating or float(movie.average_rating) < query.min_average_rating
    ):
        return False
    if query.max_average_rating and (
        not movie.average_rating or float(movie.average_rating) > query.max_average_rating
    ):
        return False
    return True


def filter_movies_from_cache(movies_data: List[Movie], query: MovieSearchQuery) -> tuple[List[Movie], Set[str]]:
    filtered = []
    skip_ids = set()
    for movie in movies_data:
        if movie_matches_query(movie, query):
            filtered.append(movie)
            skip_ids.add(movie.movie_id)
    return filtered, skip_ids


def sort_movies(movies: List[Movie], query: MovieSearchQuery) -> List[Movie]:
    if query.sort_by == "average_rating":
        reverse = query.sort_order == "desc"
        movies.sort(
            key=lambda m: float(m.average_rating) if m.average_rating else -1,
            reverse=reverse
        )
    return movies


def paginate_movies(movies: List[Movie], page: int, page_size: int) -> List[Movie]:
    start = (page - 1) * page_size
    end = start + page_size
    return movies[start:end]


def search_movies(query: MovieSearchQuery) -> MovieSearchResponsePaginated:
    try:
        movies_data: List[Movie] = list(get_all_from_cache())

        filtered, skip_ids = filter_movies_from_cache(movies_data, query)
        sorted_movies = sort_movies(filtered, query)
        paginated = paginate_movies(sorted_movies, query.page, query.page_size)

        if paginated:
            return MovieSearchResponsePaginated(
                total=len(filtered),
                page=query.page,
                page_size=query.page_size,
                movies=paginated
            )

        logger.warning("No results found in cache. Falling back to file search.")
        return search_processed_data(query=query, skip_ids=skip_ids, limit=1000)

    except Exception as e:
        logger.error(f"Error in search_movies: {str(e)}")
        raise Exception("Search failed")
