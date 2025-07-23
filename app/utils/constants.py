import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "dataset", "movielens")

MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
MOVIELENS_EXTRACT_DIRECTORY_PATH = os.path.join(BASE_DIR, "dataset", "movielens", "raw")

MOVIELENS_PROCESSED_DATA_FILEPATH = os.path.join(BASE_DIR, "dataset", "movielens", "processed_data.json")

SYNC_MOVIES_DATA_FROM_MOVIELENS_ORIGIN_SCRIPT_PATH = os.path.join(
    BASE_DIR, "scripts", "movielens", "sync_data_from_origin.py"
)

DEFAULT_CACHE_SIZE = 7000
API_AUTH_TOKEN = "my_secure_token_123"

BEARER = "Bearer"
