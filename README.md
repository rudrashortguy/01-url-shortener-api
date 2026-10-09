# 01-url-shortener-api

[![CI](https://github.com/<username>/01-url-shortener-api/actions/workflows/ci.yml/badge.svg)](https://github.com/<username>/01-url-shortener-api/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-7+-red.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A production-grade URL shortener API built with **FastAPI** and **Redis**. Supports custom slugs, TTL expiry, click tracking, and JSON/redirect responses.

## Features

- **Instant shortening** — base62-encoded slugs, atomic counter in Redis
- **Custom slugs** — reserve your own short code (alphanumeric, 4-20 chars)
- **TTL expiry** — optional `expires_in_seconds` (60s–30 days)
- **Click tracking** — atomic increment on every resolve
- **Dual response mode** — 301 redirect or `application/json` (send `Accept: application/json`)
- **Analytics endpoint** — full stats (clicks, created_at, expires_at)
- **Docker support** — one-command deploy with `docker compose`
- **OpenAPI docs** — interactive Swagger UI at `/docs`
- **Full test suite** — 70%+ coverage with pytest

## Install

### Option A: Docker (recommended)

```bash
make docker-up
make seed          # populate demo data
make demo          # run the full demo
make docker-down   # stop everything
```

### Option B: Local

```bash
# Ensure Redis is running on localhost:6379
pip install -e ".[dev]"
cp .env.example .env   # edit if needed
make dev               # starts uvicorn on :8000
```

## Usage

### Shorten a URL

```bash
curl -X POST http://localhost:8000/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://example.com","custom_slug":"ex"}'
```

Response:

```json
{
  "short_code": "ex",
  "short_url": "http://localhost:8000/r/ex",
  "original_url": "https://example.com",
  "created_at": "2026-10-09T00:00:00+00:00",
  "expires_at": null,
  "endpoint": "/r/ex"
}
```

### Resolve (redirect)

```bash
curl -I http://localhost:8000/api/v1/urls/r/ex
# → 301 Location: https://example.com
```

### Resolve (JSON)

```bash
curl http://localhost:8000/api/v1/urls/r/ex \
  -H "Accept: application/json"
```

### Stats

```bash
curl http://localhost:8000/api/v1/urls/r/ex/stats
```

### Delete

```bash
curl -X DELETE http://localhost:8000/api/v1/urls/r/ex
# → 204 No Content
```

### Health

```bash
curl http://localhost:8000/health
```

## ASCII Demo

```
  ┌─────────────────────────────────────────────┐
  │  POST /api/v1/urls                          │
  │  { "original_url": "https://example.com" }  │
  └──────────────────┬──────────────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────────────┐
  │  Redis: SET url:ex → {original_url, ...}    │
  │  INCR url_counter → 42                      │
  └──────────────────┬──────────────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────────────┐
  │  201 Created                                │
  │  { "short_code": "ex", ... }                │
  └──────────────────┬──────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
  ┌──────────────┐      ┌────────────────┐
  │ GET /r/ex    │      │ GET /r/ex/stats│
  │  → 301 redirect│     │ { clicks: 1 }  │
  └──────────────┘      └────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| Cache / store | Redis 7 |
| Config | pydantic-settings |
| Testing | pytest + pytest-cov |
| Linter | Ruff |
| Container | Docker + docker-compose |
| CI | GitHub Actions |

## Roadmap

- [ ] Rate limiting (Redis token bucket per IP)
- [ ] Admin dashboard (basic stats page)
- [ ] QR code generation for short URLs
- [ ] Batch URL creation (CSV import)
- [ ] Multi-tenancy (API keys per tenant)
- [ ] Click-event webhooks
- [ ] GraphQL endpoint
- [ ] Prometheus metrics export

## License

[MIT](LICENSE) — Copyright (c) 2026 Rudra Suryavanshi