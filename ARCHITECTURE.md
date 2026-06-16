# Architecture Overview

## System Components

### 1. **Multi-Agent System** (`src/agents/`)
- Hierarchical agent architecture
- Specialized agents (Researcher, Executor, Coordinator)
- Agent lifecycle management
- Inter-agent communication
- Task distribution and execution

### 2. **Memory Layer** (`src/memory/`)
- **Short-term Memory**: In-memory context window (recent 50 items)
- **Long-term Memory**: Vector embeddings with semantic search
- ChromaDB integration for persistence
- Sentence Transformers for embeddings
- Memory recall and context generation

### 3. **Tool Calling Framework** (`src/tools/`)
- Tool registry with dynamic registration
- Asynchronous tool execution
- Built-in tools:
  - `web_search`: Search the web
  - `fetch_webpage`: Scrape and parse web pages
  - `json_parse`: Parse JSON data
  - `calculate`: Perform math calculations
- Tool composition and chaining
- Error handling and fallbacks

### 4. **LLM Brain** (`src/brain/`)
- Ollama integration for local LLMs
- Conversation history management
- Multiple LLM capabilities:
  - General chat
  - Summarization
  - Entity extraction
  - Text classification

### 5. **Knowledge Graph** (`src/knowledge_graph/`)
- Dynamic entity management
- Relationship tracking
- NetworkX-based graph structure
- Semantic reasoning
- Entity linking
- Graph persistence (JSON export/import)

### 6. **Voice Interaction** (`src/voice/`)
- Text-to-speech (pyttsx3)
- Speech-to-text (Google Speech Recognition)
- Voice command processing
- Audio I/O interface

### 7. **Browser Automation** (`src/tools/browser.py`)
- Playwright integration (with Selenium fallback)
- Page navigation
- Element interaction
- Content extraction
- Screenshot capture
- JavaScript execution

### 8. **FastAPI Server** (`src/api.py`)
- RESTful API endpoints
- Agent management
- Memory operations
- Knowledge graph queries
- Tool execution
- Voice I/O
- LLM interaction

## Data Flow

```
User Input
    ↓
[API/Voice Interface]
    ↓
[Agent Manager] ← → [Memory Manager]
    ↓
[LLM Brain] ← → [Knowledge Graph]
    ↓
[Tool Registry] → [Browser/Web Tools]
    ↓
Result → [Output/Storage]
```

## Key Design Patterns

### 1. **Asynchronous Architecture**
- All major operations are async
- Built on asyncio for concurrent execution
- Non-blocking I/O operations

### 2. **Plugin System**
- Tool registry for extensible tooling
- Easy addition of new agents
- Memory systems are pluggable

### 3. **Separation of Concerns**
- Each module has single responsibility
- Clean interfaces between components
- Independent testing capability

### 4. **Event-Driven**
- Message passing between agents
- Status tracking and state machines
- Background task execution

## Deployment Options

### Development
```bash
python src/main.py          # Interactive agent
python -m uvicorn src.api:app --reload  # API server
```

### Production (Docker)
```bash
docker-compose up -d
```

### Distributed
- API can run on multiple instances
- Shared memory via Redis
- Shared knowledge graph via PostgreSQL

## Technology Stack Justification

- **FastAPI**: Modern, async-first, auto-documentation
- **LangGraph**: Agent orchestration and workflows
- **Ollama**: Local LLM execution, privacy-first
- **ChromaDB**: Efficient vector search for memory
- **Sentence Transformers**: High-quality embeddings
- **NetworkX**: Flexible graph representation
- **Playwright**: Modern browser automation
- **pyttsx3**: Cross-platform TTS

## Performance Considerations

- Vector embeddings cached in ChromaDB
- Conversation history limited to prevent context bloat
- Async I/O for non-blocking operations
- Tool execution parallelization
- Memory pagination for large datasets

## Security Features

- Local LLM execution (no cloud API)
- Input validation on all API endpoints
- Sandboxed tool execution
- Environment variable configuration
- Access control ready (can be added)

## Extensibility Points

1. **Add Custom Tools**: Register new tools in `tool_registry`
2. **Custom Agents**: Extend `Agent` class with specialized behavior
3. **Memory Systems**: Implement new `MemoryLayer` subclasses
4. **Knowledge Domains**: Populate knowledge graph with domain data
5. **Voice Engines**: Swap TTS/STT implementations

## Future Enhancements

- Multi-modal learning (text + images + audio)
- Federated learning across agents
- Real-time web search integration
- Advanced reasoning with chain-of-thought
- Web UI dashboard
- Persistent agent state
- Distributed agent deployment
- Fine-tuning capabilities
