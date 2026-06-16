# Autonomous AI Agent Operating System

A sophisticated multi-agent AI system built with Python, FastAPI, and LangGraph. Features real-time agent coordination, persistent memory, advanced tool calling, browser automation, voice interaction, and a dynamic knowledge graph.

## Features

###  Multi-Agent System
- Hierarchical agent architecture with specialized agents
- Autonomous agent coordination and collaboration
- Dynamic agent spawning and management
- Inter-agent communication via message bus

###  Memory Layer
- Short-term memory (context window)
- Long-term episodic memory (vector DB)
- Semantic memory (knowledge graph)
- Procedural memory (learned patterns)

###  Tool Calling Framework
- Dynamic tool registration and discovery
- Asynchronous tool execution
- Tool composition and chaining
- Error handling and tool fallbacks

###  Browser Automation
- Selenium/Playwright integration
- Autonomous web browsing
- Data extraction and scraping
- Screenshot analysis

###  Voice Interaction
- Text-to-speech (TTS) synthesis
- Speech-to-text (STT) recognition
- Voice command processing
- Audio streaming

###  Knowledge Graph
- Dynamic entity and relationship management
- Graph-based reasoning
- Entity linking and resolution
- Knowledge base persistence

## Tech Stack

- **Framework**: FastAPI, LangGraph
- **AI/LLM**: Local LLMs via Ollama
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence Transformers
- **Voice**: pyttsx3, SpeechRecognition
- **Browser**: Selenium, Playwright
- **Graph DB**: NetworkX (with SQL persistence)
- **Task Queue**: Celery
- **Async**: AsyncIO, httpx

## Project Structure

```
autonomous-ai-agent/
├── src/
│   ├── agents/              # Agent implementations
│   ├── memory/              # Memory systems
│   ├── tools/               # Tool definitions and registry
│   ├── brain/               # LLM integration
│   ├── voice/               # Voice I/O
│   ├── knowledge_graph/     # Knowledge representation
│   ├── config.py            # Configuration
│   ├── main.py              # Application entry point
│   └── api.py               # FastAPI routes
├── tests/                   # Unit and integration tests
├── config/                  # Configuration files
├── requirements.txt         # Python dependencies
└── README.md
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up local LLM (Ollama):
   ```bash
   # Download and install Ollama from https://ollama.ai
   ollama pull mistral  # or your preferred model
   ```

5. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Running the System

### Start the API Server
```bash
python -m uvicorn src.api:app --reload --port 8000
```

### Start the Agent System
```bash
python src/main.py
```

### Access the API
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

- `POST /agents/create` - Create a new agent
- `POST /agents/{agent_id}/execute` - Execute agent task
- `GET /agents/{agent_id}/status` - Get agent status
- `POST /agents/{agent_id}/message` - Send message to agent
- `GET /memory/search` - Search memory
- `POST /voice/transcribe` - Transcribe audio
- `POST /voice/synthesize` - Synthesize speech
- `GET /knowledge-graph/search` - Query knowledge graph
- `POST /tools/execute` - Execute a tool

## Configuration

Edit `config/settings.yaml`:

```yaml
llm:
  provider: ollama
  model: mistral
  base_url: http://localhost:11434

memory:
  vector_db: chromadb
  embedding_model: all-MiniLM-L6-v2

voice:
  engine: pyttsx3
  rate: 150

agents:
  max_concurrent: 5
  timeout: 300
```

## Usage Example

```python
from src.agents import AgentManager
from src.brain import LLMInterface

# Initialize
manager = AgentManager()
llm = LLMInterface()

# Create agent
agent = manager.create_agent("research_agent", "Web research specialist")

# Execute task
result = agent.execute("Find information about renewable energy trends")

# Access results
print(result.output)
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black src/
flake8 src/
```

## Roadmap

- [ ] Multi-modal learning
- [ ] Federated learning support
- [ ] Real-time collaboration
- [ ] Advanced reasoning with chain-of-thought
- [ ] Plugin system for custom agents
- [ ] Web UI dashboard

## License

MIT

## Contact

For questions or contributions, please open an issue or PR.
