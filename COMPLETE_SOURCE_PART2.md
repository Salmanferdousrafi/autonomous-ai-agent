# PART 2 - PYTHON SOURCE FILES

### src/__init__.py
```python
"""Autonomous AI Agent System"""
__version__ = "1.0.0"
```

### src/memory/__init__.py
```python
"""Memory systems for the autonomous AI agent."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class MemoryRecord:
    """A single memory record."""

    def __init__(
        self,
        content: str,
        memory_type: str = "episodic",
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ):
        self.content = content
        self.memory_type = memory_type
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now()
        self.embedding = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "type": self.memory_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class MemoryLayer(ABC):
    """Abstract base class for memory systems."""

    @abstractmethod
    async def store(self, record: MemoryRecord) -> str:
        """Store a memory record."""
        pass

    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> List[MemoryRecord]:
        """Retrieve similar memories."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all memories."""
        pass


class ShortTermMemory(MemoryLayer):
    """Short-term memory using in-memory storage with sliding window."""

    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.memories: List[MemoryRecord] = []

    async def store(self, record: MemoryRecord) -> str:
        """Store in short-term memory."""
        self.memories.append(record)
        if len(self.memories) > self.max_size:
            self.memories.pop(0)
        return f"stm_{len(self.memories)}"

    async def retrieve(self, query: str, top_k: int = 5) -> List[MemoryRecord]:
        """Get recent memories."""
        return self.memories[-top_k:] if self.memories else []

    async def clear(self) -> None:
        """Clear all memories."""
        self.memories.clear()


class LongTermMemory(MemoryLayer):
    """Long-term memory using vector embeddings."""

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", db_path: str = "./data/chroma_db"):
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=db_path)
            self.collection = self.chroma_client.get_or_create_collection(
                name="memories", metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            logger.warning(f"ChromaDB not available: {e}. Using in-memory storage.")
            self.collection = None

        self.embedding_model = SentenceTransformer(embedding_model)
        self.memories: Dict[str, MemoryRecord] = {}
        self.counter = 0

    async def store(self, record: MemoryRecord) -> str:
        """Store in long-term memory with embedding."""
        self.counter += 1
        memory_id = f"ltm_{self.counter}"

        # Generate embedding
        embedding = self.embedding_model.encode(record.content).tolist()
        record.embedding = embedding

        # Store in ChromaDB if available
        if self.collection:
            try:
                self.collection.add(
                    ids=[memory_id],
                    documents=[record.content],
                    embeddings=[embedding],
                    metadatas=[record.metadata],
                )
            except Exception as e:
                logger.error(f"Failed to store in ChromaDB: {e}")

        # Also store in-memory
        self.memories[memory_id] = record
        return memory_id

    async def retrieve(self, query: str, top_k: int = 5) -> List[MemoryRecord]:
        """Retrieve similar memories using embeddings."""
        if not query:
            return list(self.memories.values())[-top_k:]

        query_embedding = self.embedding_model.encode(query).tolist()

        if self.collection:
            try:
                results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
                retrieved = []
                for doc_id, distance in zip(results["ids"][0], results["distances"][0]):
                    if doc_id in self.memories:
                        retrieved.append(self.memories[doc_id])
                return retrieved
            except Exception as e:
                logger.error(f"Failed to query ChromaDB: {e}")

        # Fallback to in-memory similarity search
        similarities = []
        query_vec = np.array(query_embedding)
        for mem_id, memory in self.memories.items():
            if memory.embedding:
                sim = np.dot(query_vec, np.array(memory.embedding)) / (
                    np.linalg.norm(query_vec) * np.linalg.norm(np.array(memory.embedding)) + 1e-10
                )
                similarities.append((sim, memory))

        similarities.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in similarities[:top_k]]

    async def clear(self) -> None:
        """Clear all memories."""
        self.memories.clear()
        if self.collection:
            self.collection.delete(where={})


class MemoryManager:
    """Manages multiple memory systems."""

    def __init__(self, enable_short_term: bool = True, enable_long_term: bool = True):
        self.short_term: Optional[ShortTermMemory] = (
            ShortTermMemory() if enable_short_term else None
        )
        self.long_term: Optional[LongTermMemory] = (
            LongTermMemory() if enable_long_term else None
        )

    async def remember(
        self, content: str, memory_type: str = "episodic", metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Store a memory in all enabled systems."""
        record = MemoryRecord(content, memory_type, metadata)
        ids = {}

        if self.short_term:
            ids["short_term"] = await self.short_term.store(record)

        if self.long_term:
            ids["long_term"] = await self.long_term.store(record)

        return ids

    async def recall(self, query: str, source: str = "long_term", top_k: int = 5) -> List[MemoryRecord]:
        """Retrieve memories from specified source."""
        if source == "short_term" and self.short_term:
            return await self.short_term.retrieve(query, top_k)
        elif source == "long_term" and self.long_term:
            return await self.long_term.retrieve(query, top_k)
        elif source == "all":
            memories = []
            if self.short_term:
                memories.extend(await self.short_term.retrieve(query, top_k))
            if self.long_term:
                memories.extend(await self.long_term.retrieve(query, top_k))
            return memories
        return []

    async def get_context(self, query: str, max_tokens: int = 2000) -> str:
        """Get context for an LLM query."""
        memories = await self.recall(query, source="all", top_k=10)
        context = "Recent memories:\n"
        tokens = 0

        for mem in memories:
            line = f"- [{mem.timestamp.isoformat()}] {mem.content}\n"
            tokens += len(line.split())
            if tokens > max_tokens:
                break
            context += line

        return context
```

### src/brain/__init__.py
```python
"""LLM Brain - Interface to local LLMs."""

import logging
import json
from typing import Any, Dict, List, Optional
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A message in the conversation."""

    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class LLMResponse:
    """Response from LLM."""

    text: str
    tokens_used: int
    model: str
    stop_reason: str


class LLMInterface:
    """Interface to Ollama-based LLM."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model
        self.conversation_history: List[Message] = []

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> LLMResponse:
        """Generate text using the LLM."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        for msg in self.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})

        # Add current prompt
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "stream": False,
                        "options": {"num_predict": max_tokens},
                    },
                )

                if response.status_code != 200:
                    raise Exception(f"LLM error: {response.text}")

                data = response.json()
                text = data["message"]["content"]
                tokens = data.get("eval_count", 0)

                # Add to history
                self.conversation_history.append(Message(role="user", content=prompt))
                self.conversation_history.append(Message(role="assistant", content=text))

                # Keep history manageable
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]

                return LLMResponse(text=text, tokens_used=tokens, model=self.model, stop_reason="stop")
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    async def chat(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """Chat with the LLM."""
        response = await self.generate(user_message, system_prompt=system_prompt)
        return response.text

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()

    async def extract_json(self, prompt: str) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        response = await self.generate(
            f"{prompt}\n\nRespond with valid JSON only, no markdown formatting."
        )
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {response.text}")
            return {}

    async def classify(self, text: str, categories: List[str]) -> str:
        """Classify text into one of the given categories."""
        prompt = f"Classify the following text into one of these categories: {', '.join(categories)}\n\nText: {text}\n\nCategory:"
        response = await self.generate(prompt)
        return response.text.strip()

    async def summarize(self, text: str, max_length: int = 500) -> str:
        """Summarize text."""
        prompt = f"Summarize the following text in {max_length} characters or less:\n\n{text}\n\nSummary:"
        response = await self.generate(prompt, max_tokens=max_length)
        return response.text.strip()

    async def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text."""
        prompt = f"""Extract entities from the following text. Return JSON with entity types as keys and lists of entities as values.

Text: {text}

Return only valid JSON:"""
        return await self.extract_json(prompt)
```

### src/tools/__init__.py
```python
"""Tool calling framework for autonomous agents."""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ToolType(str, Enum):
    """Types of tools available to agents."""

    WEB_SEARCH = "web_search"
    WEB_BROWSE = "web_browse"
    CODE_EXECUTION = "code_execution"
    FILE_OPERATION = "file_operation"
    DATA_ANALYSIS = "data_analysis"
    API_CALL = "api_call"
    DATABASE = "database"
    CALCULATION = "calculation"


@dataclass
class ToolSchema:
    """Schema for a tool."""

    name: str
    description: str
    tool_type: ToolType
    parameters: Dict[str, Any]
    required_params: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ToolResult:
    """Result of tool execution."""

    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
        }


class Tool:
    """Base class for tools."""

    def __init__(self, schema: ToolSchema, handler: Callable):
        self.schema = schema
        self.handler = handler

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool."""
        try:
            # Validate required parameters
            for param in self.schema.required_params:
                if param not in kwargs:
                    return ToolResult(
                        success=False, data=None, error=f"Missing required parameter: {param}"
                    )

            # Execute handler
            result = self.handler(**kwargs)
            if asyncio.iscoroutine(result):
                result = await result

            return ToolResult(success=True, data=result)
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return ToolResult(success=False, data=None, error=str(e))


class ToolRegistry:
    """Registry for available tools."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        tool_type: ToolType,
        parameters: Dict[str, Any],
        required_params: List[str],
    ) -> Callable:
        """Decorator to register a tool."""

        def decorator(func: Callable) -> Callable:
            schema = ToolSchema(
                name=name,
                description=description,
                tool_type=tool_type,
                parameters=parameters,
                required_params=required_params,
            )
            tool = Tool(schema, func)
            self.tools[name] = tool
            return func

        return decorator

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list(self, tool_type: Optional[ToolType] = None) -> List[ToolSchema]:
        """List available tools."""
        if tool_type:
            return [tool.schema for tool in self.tools.values() if tool.schema.tool_type == tool_type]
        return [tool.schema for tool in self.tools.values()]

    async def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(success=False, data=None, error=f"Tool not found: {tool_name}")

        return await tool.execute(**kwargs)


# Global tool registry
tool_registry = ToolRegistry()


# Built-in tools
@tool_registry.register(
    name="web_search",
    description="Search the web for information",
    tool_type=ToolType.WEB_SEARCH,
    parameters={"query": {"type": "string"}},
    required_params=["query"],
)
async def web_search(query: str, top_results: int = 5) -> List[Dict[str, str]]:
    """Search the web."""
    import httpx

    try:
        # Using DuckDuckGo as alternative
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json"},
                timeout=10.0,
            )
            data = response.json()
            results = []
            for result in data.get("Results", [])[:top_results]:
                results.append(
                    {
                        "title": result.get("Text", ""),
                        "url": result.get("FirstURL", ""),
                        "snippet": result.get("Result", ""),
                    }
                )
            return results
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return []


@tool_registry.register(
    name="fetch_webpage",
    description="Fetch and parse a webpage",
    tool_type=ToolType.WEB_BROWSE,
    parameters={"url": {"type": "string"}},
    required_params=["url"],
)
async def fetch_webpage(url: str) -> Dict[str, Any]:
    """Fetch a webpage."""
    import httpx
    from bs4 import BeautifulSoup

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract text
            text = soup.get_text(separator="\n", strip=True)[:5000]

            # Extract links
            links = [a.get("href") for a in soup.find_all("a") if a.get("href")]

            return {"url": url, "title": soup.title.string if soup.title else "", "text": text, "links": links}
    except Exception as e:
        logger.error(f"Failed to fetch webpage: {e}")
        return {"url": url, "error": str(e)}


@tool_registry.register(
    name="json_parse",
    description="Parse JSON data",
    tool_type=ToolType.DATA_ANALYSIS,
    parameters={"json_str": {"type": "string"}},
    required_params=["json_str"],
)
async def json_parse(json_str: str) -> Dict[str, Any]:
    """Parse JSON string."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parsing failed: {e}"}


@tool_registry.register(
    name="calculate",
    description="Perform mathematical calculations",
    tool_type=ToolType.CALCULATION,
    parameters={"expression": {"type": "string"}},
    required_params=["expression"],
)
async def calculate(expression: str) -> Dict[str, Any]:
    """Perform calculation."""
    try:
        result = eval(expression, {"__builtins__": {}}, {"__import__": __import__})
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"expression": expression, "error": str(e)}
```

**⬇️ CONTINUE TO PART 3 FOR MORE FILES ⬇️**
