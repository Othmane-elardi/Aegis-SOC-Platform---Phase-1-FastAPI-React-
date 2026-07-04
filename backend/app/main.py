"""Point d'entrée FastAPI — Aegis SOC Platform."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .api.routes import (
    assets,
    auth,
    cases,
    compliance,
    dashboards,
    detection,
    hunting,
    incidents,
    iocs,
    mitre,
    risk,
    siem,
    soar,
    threat_intel,
    ueba,
    vulnerabilities,
)
from .core.config import settings
from .db.seed import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # crée les tables + amorce les comptes de démo
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=__version__,
    docs_url="/docs",
    openapi_url=f"{settings.API_V1}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1)
app.include_router(dashboards.router, prefix=settings.API_V1)
app.include_router(incidents.router, prefix=settings.API_V1)
app.include_router(threat_intel.router, prefix=settings.API_V1)
app.include_router(mitre.router, prefix=settings.API_V1)
app.include_router(assets.router, prefix=settings.API_V1)
app.include_router(vulnerabilities.router, prefix=settings.API_V1)
app.include_router(compliance.router, prefix=settings.API_V1)
app.include_router(iocs.router, prefix=settings.API_V1)
app.include_router(ueba.router, prefix=settings.API_V1)
app.include_router(risk.router, prefix=settings.API_V1)
app.include_router(cases.router, prefix=settings.API_V1)
app.include_router(siem.router, prefix=settings.API_V1)
app.include_router(soar.router, prefix=settings.API_V1)
app.include_router(detection.router, prefix=settings.API_V1)
app.include_router(hunting.router, prefix=settings.API_V1)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": settings.PROJECT_NAME, "version": __version__, "demo_mode": settings.DEMO_MODE}
