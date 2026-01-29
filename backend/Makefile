.PHONY: help install test lint format type-check run migrate clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make type-check   - Run type checking"
	@echo "  make run          - Run development server"
	@echo "  make migrate      - Run database migrations"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make clean        - Clean cache and temporary files"

install:
	pip install -r requirements.txt

test:
	pytest --cov=app --cov-report=term-missing

lint:
	ruff check app/
	black --check app/

format:
	black app/
	ruff check --fix app/

type-check:
	mypy app/ --ignore-missing-imports

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf coverage.xml






