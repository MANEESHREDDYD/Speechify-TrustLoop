from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics, demo, documents, evaluation, feedback, generation, learning
from app.config import FRONTEND_ORIGIN
from app.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="S TrustLoop API",
    description="S TrustLoop is an independent prototype for voice-first AI reliability.",
    version="1.0.1",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    demo.router, documents.router, generation.router, evaluation.router,
    feedback.router, learning.router, analytics.router,
):
    app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "s-trustloop-backend"}
