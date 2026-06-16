# AUTONOMOUS AI AGENT OPERATING SYSTEM - COMPLETE SOURCE CODE

This document contains all files for the project. Copy each section to create the corresponding file.

---

## 📁 PROJECT STRUCTURE

```
autonomous-ai-agent/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── api.py
│   ├── agents/
│   │   └── __init__.py
│   ├── memory/
│   │   └── __init__.py
│   ├── brain/
│   │   └── __init__.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── browser.py
│   ├── voice/
│   │   └── __init__.py
│   ├── knowledge_graph/
│   │   └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_system.py
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── README.md
├── QUICKSTART.md
├── ARCHITECTURE.md
└── examples.py
```

---

## 📄 FILE CONTENTS

### requirements.txt
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
langgraph==0.0.1
langchain==0.1.0
langchain-community==0.0.10
ollama==0.1.25
chromadb==0.4.18
sentence-transformers==2.2.2
pyttsx3==2.90
speechrecognition==3.10.0
selenium==4.15.2
playwright==1.40.0
beautifulsoup4==4.12.2
requests==2.31.0
numpy==1.26.3
pandas==2.1.3
networkx==3.3
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
pydantic-settings==2.1.0
httpx==0.25.1
websockets==12.0
aiohttp==3.9.1
celery==5.3.4
```

### requirements-dev.txt
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
isort>=5.12.0
```

### .env.example
```
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048

# Vector Database
CHROMA_DB_PATH=./data/chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Memory
REDIS_URL=redis://localhost:6379
MEMORY_TTL=3600

# Voice
VOICE_ENGINE=pyttsx3
VOICE_RATE=150
SPEECH_RECOGNITION_LANGUAGE=en-US

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Browser Automation
SELENIUM_HUB_URL=http://localhost:4444
PLAYWRIGHT_HEADLESS=True

# Knowledge Graph
KNOWLEDGE_GRAPH_DB=sqlite:///data/knowledge_graph.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/system.log

# Agent Configuration
MAX_CONCURRENT_AGENTS=5
AGENT_TIMEOUT=300
MEMORY_LIMIT_MB=1024
```

### .gitignore
```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual Environment
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment variables
.env
.env.local

# Data and logs
data/
logs/
*.db
*.sqlite
chroma_db/

# Build and distribution
build/
dist/
*.egg-info/
*.whl

# Testing
.pytest_cache/
.coverage
htmlcov/

# Node modules (if using frontend)
node_modules/

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.bak
*.log
```

### Dockerfile
```dockerfile
# Dockerfile for Autonomous AI Agent System

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    make \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data logs

# Expose API port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434

# Run the application
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  # Ollama LLM service
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
    volumes:
      - ollama_data:/root/.ollama
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis for caching
  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  # Main API service
  api:
    build: .
    container_name: ai-agent-api
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - REDIS_URL=redis://redis:6379
      - DEBUG=True
    depends_on:
      ollama:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    command: uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

volumes:
  ollama_data:
  redis_data:
```

### Makefile
```makefile
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
```

### src/config.py
```python
"""Configuration module for the Autonomous AI Agent System."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048

    # Vector Database
    chroma_db_path: str = "./data/chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Memory
    redis_url: str = "redis://localhost:6379"
    memory_ttl: int = 3600

    # Voice
    voice_engine: str = "pyttsx3"
    voice_rate: int = 150
    speech_recognition_language: str = "en-US"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # Browser
    selenium_hub_url: str = "http://localhost:4444"
    playwright_headless: bool = True

    # Knowledge Graph
    knowledge_graph_db: str = "sqlite:///./data/knowledge_graph.db"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/system.log"

    # Agent Configuration
    max_concurrent_agents: int = 5
    agent_timeout: int = 300
    memory_limit_mb: int = 1024

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def data_dir(self) -> Path:
        """Get data directory path."""
        path = Path("./data")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def logs_dir(self) -> Path:
        """Get logs directory path."""
        path = Path("./logs")
        path.mkdir(parents=True, exist_ok=True)
        return path


# Global settings instance
settings = Settings()
```

---

**⬇️ CONTINUE SCROLLING FOR MORE SOURCE FILES ⬇️**

This document continues with all remaining Python source files...
