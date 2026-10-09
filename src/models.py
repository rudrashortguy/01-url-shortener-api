"""Pydantic models for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class CreateUrlRequest(BaseModel):
    original_url: HttpUrl = Field(..., description="The full URL to shorten")
    custom_slug: Optional[str] = Field(
        None,
        min_length=4,
        max_length=20,
        pattern=r"^[a-zA-Z0-9]+$",
        description="Optional custom slug (alphanumeric, 4-20 chars)",
    )
    expires_in_seconds: Optional[int] = Field(
        None,
        ge=60,
        le=2592000,  # 30 days max
        description="Optional TTL in seconds (min 60, max 30 days)",
    )


class CreateUrlResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    endpoint: str = Field(
        description="Full redirect endpoint URL for this short code",
    )

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    clicks: int
    expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    version: str