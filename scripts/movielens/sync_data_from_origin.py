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


def download_and_extract():
    logger.info("Downloading MovieLens dataset...")
    response = requests.get(MOVIELENS_URL)
    response.raise_for_status()
    
    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        zip_ref.extractall(MOVIELENS_EXTRACT_DIRECTORY_PATH)
    
    logger.info(f"Dataset extracted to: {MOVIELENS_EXTRACT_DIRECTORY_PATH}")

def process_data():
    movies_file = os.path.join(MOVIELENS_EXTRACT_DIRECTORY_PATH, "ml-latest-small", "movies.csv")
    ratings_file = os.path.join(MOVIELENS_EXTRACT_DIRECTORY_PATH, "ml-latest-small", "ratings.csv")
    tags_file = os.path.join(MOVIELENS_EXTRACT_DIRECTORY_PATH, "ml-latest-small", "tags.csv")

    logger.info("Loading CSV files...")
    movies_df = pd.read_csv(movies_file)
    ratings_df = pd.read_csv(ratings_file)
    tags_df = pd.read_csv(tags_file)

    logger.info("Processing ratings (calculating average ratings)...")
    avg_ratings = ratings_df.groupby("movieId")["rating"].mean().round(2).to_dict()

    logger.info("Processing tags (aggregating tags)...")
    tag_groups = tags_df.groupby("movieId")["tag"].apply(lambda tags: list(set(tags))).to_dict()

    logger.info("Building final JSON structure...")
    result = []
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

        result.append(entry)

    logger.info("Sorting movies by average rating descending...")
    result.sort(
        key=lambda x: x.get("average_rating", -1),
        reverse=True
    )

    for movie in result:
        if "average_rating" in movie:
            movie["average_rating"] = str(movie["average_rating"])

    logger.info(f"Saving output JSON to: {MOVIELENS_PROCESSED_DATA_FILEPATH}")
    os.makedirs(os.path.dirname(MOVIELENS_PROCESSED_DATA_FILEPATH), exist_ok=True)
    with open(MOVIELENS_PROCESSED_DATA_FILEPATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)


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
