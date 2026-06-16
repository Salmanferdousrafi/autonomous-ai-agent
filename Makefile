.PHONY: help install dev-install run test lint format clean docker-build docker-up docker-down

help:
	@echo "Autonomous AI Agent System - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev-install   - Install dev dependencies"
	@echo "  make venv          - Create virtual environment"
	@echo ""
	@echo "Running:"
	@echo "  make run           - Run API server"
	@echo "  make run-agent     - Run interactive agent"
	@echo "  make run-all       - Run all services (docker)"
	@echo ""
	@echo "Development:"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean up temporary files"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-logs   - View Docker logs"

venv:
	python -m venv venv
	$(VENV)/pip install --upgrade pip

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	python -m uvicorn src.api:app --reload --port 8000

run-agent:
	python src/main.py

run-all: docker-up
	@echo "Services running on Docker. Access API at http://localhost:8000/docs"

test:
	pytest tests/ -v --cov=src

lint:
	flake8 src tests
	mypy src

format:
	black src tests examples.py
	isort src tests examples.py

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api
