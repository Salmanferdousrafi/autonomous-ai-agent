# Autonomous AI Agent Operating System

A sophisticated multi-agent AI system built with Python, FastAPI, and LangGraph. Features real-time agent coordination, persistent memory, advanced tool calling, browser automation, voice interaction, and a dynamic knowledge graph.

## Features

### 🤖 Multi-Agent System
- Hierarchical agent architecture with specialized agents
- Autonomous agent coordination and collaboration
- Dynamic agent spawning and management
- Inter-agent communication via message bus

### 💾 Memory Layer
- Short-term memory (context window)
- Long-term episodic memory (vector DB)
- Semantic memory (knowledge graph)
- Procedural memory (learned patterns)

### 🔧 Tool Calling Framework
- Dynamic tool registration and discovery
- Asynchronous tool execution
- Tool composition and chaining
- Error handling and tool fallbacks

### 🌐 Browser Automation
- Selenium/Playwright integration
- Autonomous web browsing
- Data extraction and scraping
- Screenshot analysis

### 🎤 Voice Interaction
- Text-to-speech (TTS) synthesis
- Speech-to-text (STT) recognition
- Voice command processing
- Audio streaming

### 📊 Knowledge Graph
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

