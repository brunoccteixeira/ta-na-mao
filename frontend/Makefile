.PHONY: help install test lint format build dev clean

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linter"
	@echo "  make format   - Format code (if configured)"
	@echo "  make build    - Build for production"
	@echo "  make dev      - Start development server"
	@echo "  make clean    - Clean build artifacts"

install:
	npm install

test:
	npm test

lint:
	npm run lint

format:
	npm run format || echo "Format script not configured"

build:
	npm run build

dev:
	npm run dev

clean:
	rm -rf node_modules
	rm -rf dist
	rm -rf .vite
	rm -rf coverage






