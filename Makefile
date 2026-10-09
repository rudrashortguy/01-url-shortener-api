.PHONY: dev test lint docker-up docker-down format

REPO_ROOT := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
REDIS_URL ?= redis://localhost:6379/9

dev:
	@echo "Starting uvicorn..."
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	REDIS_URL=$(REDIS_URL) pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	ruff check src tests

format:
	ruff format src tests

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

health:
	curl -s http://localhost:8000/health | python3 -m json.tool

seed:
	python scripts/seed.py

demo: docker-up
	@echo ""
	@echo "=== API Demo ==="
	@curl -s http://localhost:8000/health | python3 -m json.tool
	@curl -s -X POST http://localhost:8000/api/v1/urls \
	  -H "Content-Type: application/json" \
	  -d '{"original_url":"https://example.com","custom_slug":"demo"}' | python3 -m json.tool
	@echo ""
	@curl -s http://localhost:8000/api/v1/urls/r/demo/stats | python3 -m json.tool
	@echo ""
	@curl -s http://localhost:8000/api/v1/urls/r/demo -H "Accept: application/json" | python3 -m json.tool
	@echo ""
	@echo "Stop with: make docker-down"