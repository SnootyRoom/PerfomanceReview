import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import settings
from .database import Base, SessionLocal, engine
from .routers import ai, auth, departments, directions, export, meetings, plans, scheduled_meetings, skills, users
from .scheduler import start_scheduler
from .seed import seed_if_empty

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # No Alembic here, and create_all doesn't alter existing tables, so
        # new columns are patched in manually instead of a DB reset.
        await conn.execute(text("ALTER TABLE problem_flags ADD COLUMN IF NOT EXISTS resolved_at DATE"))
    async with SessionLocal() as db:
        await seed_if_empty(db)

    scheduler = start_scheduler()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title="Performance Review API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(departments.router)
app.include_router(directions.router)
app.include_router(skills.router)
app.include_router(plans.router)
app.include_router(meetings.router)
app.include_router(scheduled_meetings.router)
app.include_router(export.router)
app.include_router(ai.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
