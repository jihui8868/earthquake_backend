from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import engine, Base
from app.models import *  # noqa: F401, F403 — ensure all models are registered
from app.router import chat, department, user, role, permission, knowledge_base, knowledge_graph, file_system


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

# Register routers under /api prefix
for r in [chat, department, user, role, permission, knowledge_base, knowledge_graph, file_system]:
    app.include_router(r.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
