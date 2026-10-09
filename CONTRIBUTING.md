# Contributing to URL Shortener API

Thanks for your interest! This is a portfolio project—contributors are welcome, but the bar is "clean, tested code that fits the style."

## Quick Start

```bash
# 1. Clone & enter the repo
git clone https://github.com/<username>/01-url-shortener-api.git
cd 01-url-shortener-api

# 2. Start Redis + API via Docker
make docker-up

# 3. Seed demo data
make seed

# 4. Open the interactive docs
open http://localhost:8000/docs
```

## Running Tests

```bash
# Requires a running Redis on localhost:6379
make test

# Or with a specific Redis URL
REDIS_URL=redis://localhost:6379/9 make test
```

## Code Style

- We use **Ruff** for linting and formatting.
- `make lint` — check style
- `make format` — auto-format

```bash
make lint && make format
```

## Pull Request Guidelines

1. **One feature per PR.** Keep diffs small.
2. **Tests required.** Every new behaviour needs a test.
3. **No hardcoded secrets.** Use `.env.example` as a template.
4. **Describe your changes** in the PR body. Link issues when relevant.

## Architecture Notes

- **`src/`** — Application source (FastAPI app, routes, service layer)
- **`src/services/url_service.py`** — Core Redis-backed logic
- **`src/utils/slugs.py`** — Base62 slug generation
- **`tests/`** — pytest suite (run with `make test`)
- **`docker-compose.yml`** — Redis + API services