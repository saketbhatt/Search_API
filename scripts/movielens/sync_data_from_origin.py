import os
import sys
import zipfile
import requests
import pandas as pd
import json
from io import BytesIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.utils.constants import MOVIELENS_URL, MOVIELENS_EXTRACT_DIRECTORY_PATH, MOVIELENS_PROCESSED_DATA_FILEPATH
from app.utils.logger import get_logger

logger = get_logger(__name__)


def download_movielens_zip() -> bytes:
    logger.info("Downloading MovieLens dataset...")
    response = requests.get(MOVIELENS_URL)
    response.raise_for_status()
    logger.info("Download completed.")
    return response.content


def extract_zip_content(zip_content: bytes, extract_to: str):
    with zipfile.ZipFile(BytesIO(zip_content)) as zip_ref:
        zip_ref.extractall(extract_to)
    logger.info(f"Dataset extracted to: {extract_to}")


def load_csv_files(base_path: str):
    logger.info("Loading CSV files...")
    movies = pd.read_csv(os.path.join(base_path, "ml-latest-small", "movies.csv"))
    ratings = pd.read_csv(os.path.join(base_path, "ml-latest-small", "ratings.csv"))
    tags = pd.read_csv(os.path.join(base_path, "ml-latest-small", "tags.csv"))
    return movies, ratings, tags


def calculate_average_ratings(ratings_df: pd.DataFrame) -> dict:
    logger.info("Calculating average ratings...")
    return ratings_df.groupby("movieId")["rating"].mean().round(2).to_dict()


def aggregate_tags(tags_df: pd.DataFrame) -> dict:
    logger.info("Aggregating tags...")
    return tags_df.groupby("movieId")["tag"].apply(lambda tags: list(set(tags))).to_dict()


def build_movie_entries(movies_df, avg_ratings, tag_groups):
    logger.info("Building movie entries...")
    entries = []
    for _, row in movies_df.iterrows():
        movie_id = int(row["movieId"])
        entry = {
            "movie_id": str(movie_id),
            "title": row["title"],
        }

        if pd.notna(row.get("genres")) and row["genres"] != "(no genres listed)":
            entry["genre"] = row["genres"]

        if movie_id in avg_ratings:
            entry["average_rating"] = round(avg_ratings[movie_id], 2)

        if movie_id in tag_groups:
            entry["tags"] = tag_groups[movie_id]

        entries.append(entry)

    logger.info("Sorting movies by average rating...")
    entries.sort(key=lambda x: x.get("average_rating", -1), reverse=True)

    for movie in entries:
        if "average_rating" in movie:
            movie["average_rating"] = str(movie["average_rating"])

    return entries


def save_to_json(data: list, output_path: str):
    logger.info(f"Saving output JSON to: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def download_and_extract():
    zip_data = download_movielens_zip()
    extract_zip_content(zip_data, MOVIELENS_EXTRACT_DIRECTORY_PATH)


def process_data():
    movies_df, ratings_df, tags_df = load_csv_files(MOVIELENS_EXTRACT_DIRECTORY_PATH)
    avg_ratings = calculate_average_ratings(ratings_df)
    tag_groups = aggregate_tags(tags_df)
    result = build_movie_entries(movies_df, avg_ratings, tag_groups)
    save_to_json(result, MOVIELENS_PROCESSED_DATA_FILEPATH)


def sync_data_from_origin():
    try:
        logger.info("Syncing data from origin for MovieLens")
        download_and_extract()
        process_data()
    except Exception as e:
        logger.error(f"Error while refreshing data: {str(e)}")


if __name__ == "__main__":
    print("Running sync_data_from_origin.py...")
    sync_data_from_origin()
