import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.infrastructure.database.models import Base
from app.infrastructure.database.session import engine
from app.presentation.routes import router

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Report service starting", extra={"event": "service_start"})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Report service shutting down", extra={"event": "service_stop"})
    await engine.dispose()


app = FastAPI(
    title="Report Service",
    description="Gera e persiste relatórios técnicos estruturados de análise de arquitetura.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
)

app.include_router(router)
