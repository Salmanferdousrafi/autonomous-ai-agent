# Quick Start Guide

## Prerequisites

- Python 3.10+
- Ollama (for local LLMs)
- Redis (optional, for advanced memory)

## Installation

### 1. Install Ollama

Download and install Ollama from [https://ollama.ai](https://ollama.ai)

```bash
# Pull a model (e.g., Mistral)
ollama pull mistral
```

### 2. Clone and Setup

```bash
git clone <repo_url>
cd autonomous-ai-agent

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env

# Edit .env with your settings
# Important variables:
# - OLLAMA_BASE_URL=http://localhost:11434
# - OLLAMA_MODEL=mistral
```

## Running the System

### Option 1: Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start:
- Ollama (LLM service)
- Redis (memory cache)
- FastAPI server (on http://localhost:8000)

### Option 2: Manual Setup

**Terminal 1: Start Ollama**
```bash
ollama serve
```

**Terminal 2: Start API Server**
```bash
python -m uvicorn src.api:app --reload --port 8000
```

**Terminal 3: Run Interactive Agent**
```bash
python src/main.py
```

## API Usage

### Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example: Create an Agent

```bash
curl -X POST "http://localhost:8000/agents/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Bot",
    "role": "researcher",
    "description": "Specialized web researcher",
    "tools": ["web_search", "fetch_webpage"]
  }'
```

### Example: Chat with LLM

```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python?"}'
```

### Example: Store Memory

```bash
curl -X POST "http://localhost:8000/memory/store" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Autonomous systems are important",
    "memory_type": "semantic"
  }'
```

## Interactive Commands

When running `python src/main.py`, you can use these commands:

- `ask <question>` - Ask the LLM a question
- `remember <text>` - Store something in memory
- `recall <query>` - Search memory
- `status` - Show system status
- `agents` - List all agents
- `help` - Show all commands
- `quit` - Exit

## Troubleshooting

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Check OLLAMA_BASE_URL in .env

### Port Already in Use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

### Memory Issues
- Start with smaller batch sizes
- Use `MEMORY_LIMIT_MB` setting
- Consider reducing `CHROMA_DB_PATH` data

## Development

### Run Tests
```bash
pytest tests/
```

### Code Style
```bash
black src/
flake8 src/
```

### View Logs
```bash
tail -f logs/system.log
```

## Next Steps

1. **Create Specialized Agents** - Tailor agents for specific domains
2. **Integrate More Tools** - Add custom tool implementations
3. **Build Knowledge Base** - Populate knowledge graph with domain data
4. **Deploy** - Use Docker for production deployment

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [ChromaDB Documentation](https://docs.trychroma.com)

## Support

For issues or questions, please open a GitHub issue or contact the team.
