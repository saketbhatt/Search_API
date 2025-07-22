import json
from typing import List, Set
from app.models.movies.search import Movie, MovieSearchQuery, MovieSearchResponsePaginated
from app.utils.constants import MOVIELENS_PROCESSED_DATA_FILEPATH
from app.utils.logger import get_logger

logger = get_logger(__name__)


def search_processed_data(query: MovieSearchQuery, skip_ids: Set[str], limit: int = 1000) -> MovieSearchResponsePaginated:
    try:
        with open(MOVIELENS_PROCESSED_DATA_FILEPATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        filtered = []
        for item in raw_data:
            movie_id = item.get("movie_id")
            if movie_id in skip_ids:
                continue

            title = item.get("title", "")
            genre = item.get("genre", "")
            tags = item.get("tags", [])
            avg_rating = item.get("average_rating", None)

            if query.title and query.title.lower() not in title.lower():
                continue
            if query.genre and (not genre or query.genre.lower() not in genre.lower()):
                continue
            if query.tags:
                if not tags:
                    continue
                tags_lower = [tag.lower() for tag in tags]
                if not any(tag.lower() in tags_lower for tag in query.tags):
                    continue
            if query.min_average_rating and (
                not avg_rating or float(avg_rating) < query.min_average_rating
            ):
                continue
            if query.max_average_rating and (
                not avg_rating or float(avg_rating) > query.max_average_rating
            ):
                continue

            filtered.append(Movie(**item))
            if len(filtered) >= limit:
                break

        # Sort results
        if query.sort_by == "average_rating":
            reverse = query.sort_order == "desc"
            filtered.sort(
                key=lambda m: float(m.average_rating) if m.average_rating else -1,
                reverse=reverse
            )

        # Paginate
        total = len(filtered)
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        paginated = filtered[start:end]

        return MovieSearchResponsePaginated(
            total=total,
            page=query.page,
            page_size=query.page_size,
            movies=paginated
        )

    except Exception as e:
        logger.error(f"Error in search_processed_data: {str(e)}")
        raise Exception("Failed to search processed dataset.")
