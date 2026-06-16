# PART 3 - MORE SOURCE FILES

### src/tools/browser.py
```python
"""Browser automation module."""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import base64

logger = logging.getLogger(__name__)


@dataclass
class BrowserAction:
    """A browser action."""

    action_type: str  # "click", "type", "navigate", "screenshot", etc.
    target: str  # CSS selector or XPath
    value: Optional[str] = None


class BrowserAutomation:
    """Browser automation interface."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.page = None
        self.use_playwright = True

    async def initialize(self) -> bool:
        """Initialize browser."""
        try:
            if self.use_playwright:
                from playwright.async_api import async_playwright

                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
                self.page = await self.browser.new_page()
                logger.info("Browser initialized with Playwright")
                return True
        except Exception as e:
            logger.warning(f"Playwright initialization failed: {e}")
            try:
                from selenium import webdriver

                options = webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument("--headless")
                self.browser = webdriver.Chrome(options=options)
                logger.info("Browser initialized with Selenium")
                return True
            except Exception as e2:
                logger.error(f"Both browser initializations failed: {e2}")
                return False

    async def navigate(self, url: str) -> bool:
        """Navigate to URL."""
        try:
            if self.page:
                await self.page.goto(url, wait_until="networkidle")
            else:
                self.browser.get(url)
            logger.info(f"Navigated to {url}")
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False

    async def click(self, selector: str) -> bool:
        """Click an element."""
        try:
            if self.page:
                await self.page.click(selector)
            else:
                self.browser.find_element("css selector", selector).click()
            logger.info(f"Clicked element: {selector}")
            return True
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False

    async def type_text(self, selector: str, text: str) -> bool:
        """Type text into an element."""
        try:
            if self.page:
                await self.page.fill(selector, text)
            else:
                element = self.browser.find_element("css selector", selector)
                element.clear()
                element.send_keys(text)
            logger.info(f"Typed text into: {selector}")
            return True
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return False

    async def get_text(self, selector: str) -> Optional[str]:
        """Get text from an element."""
        try:
            if self.page:
                text = await self.page.text_content(selector)
            else:
                element = self.browser.find_element("css selector", selector)
                text = element.text
            return text
        except Exception as e:
            logger.error(f"Get text failed: {e}")
            return None

    async def screenshot(self, filepath: Optional[str] = None) -> Optional[bytes]:
        """Take a screenshot."""
        try:
            if self.page:
                screenshot = await self.page.screenshot()
            else:
                screenshot = self.browser.get_screenshot_as_png()

            if filepath:
                with open(filepath, "wb") as f:
                    f.write(screenshot)
                logger.info(f"Screenshot saved to {filepath}")

            return screenshot
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None

    async def get_page_content(self) -> Optional[str]:
        """Get page HTML/content."""
        try:
            if self.page:
                content = await self.page.content()
            else:
                content = self.browser.page_source
            return content
        except Exception as e:
            logger.error(f"Get content failed: {e}")
            return None

    async def close(self) -> None:
        """Close browser."""
        try:
            if self.page:
                await self.browser.close()
                await self.playwright.stop()
            else:
                self.browser.quit()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Close failed: {e}")
```

### src/voice/__init__.py
```python
"""Voice interaction module for audio input/output."""

import logging
from typing import Optional
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AudioData:
    """Audio data container."""

    data: bytes
    sample_rate: int
    channels: int
    duration: float


class TextToSpeech:
    """Text-to-speech engine."""

    def __init__(self, engine: str = "pyttsx3", rate: int = 150):
        self.engine_type = engine
        self.rate = rate

        if engine == "pyttsx3":
            try:
                import pyttsx3

                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", rate)
            except ImportError:
                logger.warning("pyttsx3 not installed")
                self.engine = None

    async def speak(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """Convert text to speech."""
        if not self.engine:
            logger.error("TTS engine not available")
            return False

        try:
            if save_to_file:
                self.engine.save_to_file(text, save_to_file)
            self.engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False

    def set_rate(self, rate: int) -> None:
        """Set speech rate."""
        self.rate = rate
        if self.engine:
            self.engine.setProperty("rate", rate)


class SpeechToText:
    """Speech-to-text engine."""

    def __init__(self, language: str = "en-US"):
        self.language = language

        try:
            import speech_recognition as sr

            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        except ImportError:
            logger.warning("SpeechRecognition not installed")
            self.recognizer = None
            self.microphone = None

    async def listen(self, timeout: int = 10) -> Optional[str]:
        """Listen and transcribe audio from microphone."""
        if not self.recognizer:
            logger.error("STT engine not available")
            return None

        try:
            import speech_recognition as sr

            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=timeout)

                text = self.recognizer.recognize_google(audio, language=self.language)
                return text
        except Exception as e:
            logger.error(f"STT error: {e}")
            return None

    async def transcribe_file(self, audio_file: str) -> Optional[str]:
        """Transcribe audio file."""
        if not self.recognizer:
            logger.error("STT engine not available")
            return None

        try:
            import speech_recognition as sr

            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language=self.language)
                return text
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None


class VoiceInterface:
    """Unified voice I/O interface."""

    def __init__(self, language: str = "en-US", tts_rate: int = 150):
        self.tts = TextToSpeech(rate=tts_rate)
        self.stt = SpeechToText(language=language)
        self.language = language

    async def interact(self, prompt: Optional[str] = None, listen: bool = True) -> Optional[str]:
        """Full voice interaction."""
        if prompt and listen:
            await self.tts.speak(prompt)

        if listen:
            text = await self.stt.listen()
            return text

        return None

    async def handle_voice_command(self, command: str) -> str:
        """Handle a voice command with spoken response."""
        logger.info(f"Voice command: {command}")
        response = f"Processing command: {command}"
        await self.tts.speak(response)
        return response
```

### src/knowledge_graph/__init__.py
```python
"""Knowledge Graph - Dynamic entity and relationship management."""

import logging
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
import json
import networkx as nx
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """A knowledge entity."""

    name: str
    entity_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.entity_type,
            "properties": self.properties,
            "created_at": self.created_at,
            "confidence": self.confidence,
        }


@dataclass
class Relationship:
    """A relationship between entities."""

    source: str
    target: str
    relation_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.relation_type,
            "properties": self.properties,
            "weight": self.weight,
            "created_at": self.created_at,
        }


class KnowledgeGraph:
    """Dynamic knowledge graph for semantic reasoning."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self.entity_index: Dict[str, Set[str]] = {}

    def add_entity(
        self, name: str, entity_type: str, properties: Optional[Dict[str, Any]] = None, confidence: float = 1.0
    ) -> Entity:
        """Add an entity to the graph."""
        entity = Entity(name=name, entity_type=entity_type, properties=properties or {}, confidence=confidence)
        self.entities[name] = entity
        self.graph.add_node(name, **entity.to_dict())

        if entity_type not in self.entity_index:
            self.entity_index[entity_type] = set()
        self.entity_index[entity_type].add(name)

        logger.info(f"Added entity: {name} ({entity_type})")
        return entity

    def add_relationship(
        self,
        source: str,
        target: str,
        relation_type: str,
        properties: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
    ) -> Optional[Relationship]:
        """Add a relationship between entities."""
        if source not in self.entities or target not in self.entities:
            logger.warning(f"Cannot add relationship: entities not found")
            return None

        rel = Relationship(
            source=source, target=target, relation_type=relation_type, properties=properties or {}, weight=weight
        )
        self.relationships.append(rel)
        self.graph.add_edge(source, target, relation_type=relation_type, weight=weight, **rel.to_dict())

        logger.info(f"Added relationship: {source} --[{relation_type}]--> {target}")
        return rel

    def find_entity(self, name: str) -> Optional[Entity]:
        """Find an entity by name."""
        return self.entities.get(name)

    def find_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Find all entities of a given type."""
        names = self.entity_index.get(entity_type, set())
        return [self.entities[name] for name in names if name in self.entities]

    def find_relationships(self, source: Optional[str] = None, target: Optional[str] = None) -> List[Relationship]:
        """Find relationships."""
        results = []
        for rel in self.relationships:
            if source and rel.source != source:
                continue
            if target and rel.target != target:
                continue
            results.append(rel)
        return results

    def query(self, query_text: str) -> Dict[str, Any]:
        """Query the knowledge graph."""
        results = {
            "entities": [],
            "relationships": [],
        }

        query_lower = query_text.lower()
        for name, entity in self.entities.items():
            if query_lower in name.lower() or query_lower in entity.entity_type.lower():
                results["entities"].append(entity.to_dict())

                related_rels = self.find_relationships(source=name)
                for rel in related_rels:
                    results["relationships"].append(rel.to_dict())

        return results

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary."""
        return {
            "entities": [e.to_dict() for e in self.entities.values()],
            "relationships": [r.to_dict() for r in self.relationships],
        }

    def stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "num_entities": len(self.entities),
            "num_relationships": len(self.relationships),
        }
```

**⬇️ CONTINUE TO PART 4 ⬇️**
