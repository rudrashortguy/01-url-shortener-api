"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .config import settings
from .dependencies import lifespan  # noqa: F401 – lifespan is used below
from .routes import router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A high-performance URL shortener API backed by Redis.",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        content={"status": "healthy", "version": settings.app_version}
    )


@app.get("/", tags=["root"])
async def root() -> JSONResponse:
    """API root – link to docs."""
    return JSONResponse(
        content={
            "name": settings.app_name,
            "docs": "/docs",
            "openapi": "/openapi.json",
        }
    )