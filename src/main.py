import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter
from prometheus_client import generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

from src.auth.router import router as auth_router
from src.messages.router import router as messages_router
from src.database import Base, engine


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://example-production-domain.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_COUNT = Counter('app_requests_total', 'Total number of requests')


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        REQUEST_COUNT.inc()
        response = await call_next(request)
        return response


app.add_middleware(MetricsMiddleware)

app.include_router(auth_router)
app.include_router(messages_router)


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/metrics")
async def get_metrics():
    return generate_latest()


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
