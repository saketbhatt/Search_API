from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.security import HTTPBearer
from app.api.v1.controllers import movies
from app.cache_interface.initialize_cache import initialize_cache
from app import health
from apscheduler.schedulers.background import BackgroundScheduler
from scripts.movielens import sync_data_from_origin

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_cache()

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: sync_data_from_origin(), 'interval', days=2)
    scheduler.start()

    yield

security = HTTPBearer(auto_error=False)
app = FastAPI(title="Movie API Server", version="1.0.0", lifespan=lifespan)

app.include_router(health.router)
app.include_router(movies.router, prefix="/api/v1")
