from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.main import init_db
from .endpoint import api_router
from auth.user import router


@asynccontextmanager
async def lifespan(app:FastAPI):
    print("server is running at port 8000")
    await init_db()
    print("database connected successfully")
    yield
    print("server is shutting down")

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
app.include_router(router)
