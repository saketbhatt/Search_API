from typing import List, Set
from app.models.movies.search import Movie, MovieSearchResponsePaginated, MovieSearchQuery
from app.cache.get_all import get_all_from_cache
from app.utils.logger import get_logger
from dataset.movielens.search_processed_data import search_processed_data
from app.utils.logger import get_logger

logger = get_logger(__name__)

def search_movies(query: MovieSearchQuery) -> MovieSearchResponsePaginated:
    try:
        movies_data: List[Movie] = list(get_all_from_cache())

        filtered = []
        skip_ids: Set[str] = set()

        for movie in movies_data:
            if query.title and query.title.lower() not in movie.title.lower():
                continue
            if query.genre and (not movie.genre or query.genre.lower() not in movie.genre.lower()):
                continue
            if query.tags:
                if not movie.tags:
                    continue
                movie_tags_lower = [tag.lower() for tag in movie.tags]
                if not any(tag.lower() in movie_tags_lower for tag in query.tags):
                    continue
            if query.min_average_rating and (
                not movie.average_rating or float(movie.average_rating) < query.min_average_rating
            ):
                continue
            if query.max_average_rating and (
                not movie.average_rating or float(movie.average_rating) > query.max_average_rating
            ):
                continue
            filtered.append(movie)
            skip_ids.add(movie.movie_id)

        # Sort results
        if query.sort_by == "average_rating":
            reverse = query.sort_order == "desc"
            filtered.sort(
                key=lambda m: float(m.average_rating) if m.average_rating else -1,
                reverse=reverse
            )

        total = len(filtered)
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        paginated = filtered[start:end]

        # If cache has enough results, return
        if len(paginated) > 0:
            return MovieSearchResponsePaginated(
                total=total,
                page=query.page,
                page_size=query.page_size,
                movies=paginated
            )

        # If cache is empty for this query, fallback to file
        logger.warning("No results found in cache. Falling back to file search.")
        return search_processed_data(query=query, skip_ids=skip_ids, limit=1000)

    except Exception as e:
        logger.error(f"Error in search_movies: {str(e)}")
        raise Exception("Search failed")
