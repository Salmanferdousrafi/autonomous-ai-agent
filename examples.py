"""Example usage patterns for the Autonomous AI Agent System."""

import asyncio
from src.agents import AgentManager, Task
from src.brain import LLMInterface
from src.memory import MemoryManager
from src.knowledge_graph import KnowledgeGraph
from src.tools import tool_registry
from src.voice import VoiceInterface


async def example_basic_agent():
    """Example: Create and run a basic agent."""
    print("=== Example: Basic Agent ===")

    llm = LLMInterface()
    agent_manager = AgentManager(llm=llm, tool_registry=tool_registry)

    # Create an agent
    researcher = agent_manager.create_agent(
        name="Research Agent",
        role="researcher",
        description="Finds information",
        tools=["web_search"],
    )

    # Create a task
    task = Task(
        id="task_1",
        description="Research renewable energy",
        objective="Find recent trends in renewable energy",
    )

    # Execute task
    result = await agent_manager.assign_task(researcher.id, task)
    print(f"Task completed: {result.status}")
    print(f"Result: {result.result}")


async def example_memory_system():
    """Example: Using the memory system."""
    print("\n=== Example: Memory System ===")

    memory_manager = MemoryManager()

    # Store memories
    await memory_manager.remember(
        "Python is a popular programming language for AI",
        memory_type="semantic",
    )
    await memory_manager.remember(
        "FastAPI is a modern web framework",
        memory_type="semantic",
    )

    # Recall memories
    memories = await memory_manager.recall("Python programming", top_k=5)
    print(f"Found {len(memories)} memories:")
    for mem in memories:
        print(f"  - {mem.content}")

    # Get context for LLM
    context = await memory_manager.get_context("programming languages")
    print(f"LLM context:\n{context}")


async def example_knowledge_graph():
    """Example: Using knowledge graph."""
    print("\n=== Example: Knowledge Graph ===")

    kg = KnowledgeGraph()

    # Add entities
    kg.add_entity("Python", "ProgrammingLanguage", {"year": 1991})
    kg.add_entity("FastAPI", "WebFramework", {"async": True})
    kg.add_entity("Machine Learning", "Technology")

    # Add relationships
    kg.add_relationship("Python", "Machine Learning", "enables")
    kg.add_relationship("FastAPI", "Python", "built_with")

    # Query
    results = kg.query("Python")
    print(f"Query results: {results}")

    # Get stats
    stats = kg.stats()
    print(f"Graph stats: {stats}")


async def example_llm_interaction():
    """Example: Interact with LLM."""
    print("\n=== Example: LLM Interaction ===")

    llm = LLMInterface()

    # Simple chat
    response = await llm.chat("What is machine learning?")
    print(f"LLM Response:\n{response}")

    # Summarization
    text = """
    Machine learning is a subset of artificial intelligence that enables systems to learn
    and improve from experience without being explicitly programmed. It uses algorithms and
    statistical models to analyze patterns in data.
    """
    summary = await llm.summarize(text)
    print(f"\nSummary:\n{summary}")

    # Entity extraction
    entities = await llm.extract_entities("John works at Google in San Francisco")
    print(f"\nExtracted entities: {entities}")


async def example_tool_usage():
    """Example: Using tools."""
    print("\n=== Example: Tool Usage ===")

    # List available tools
    tools = tool_registry.list()
    print("Available tools:")
    for tool in tools[:5]:  # Show first 5
        print(f"  - {tool.name}: {tool.description}")

    # Execute a tool
    result = await tool_registry.execute("calculate", expression="2 ** 10")
    print(f"\nCalculation result: {result.to_dict()}")


async def example_multi_agent_coordination():
    """Example: Multi-agent coordination."""
    print("\n=== Example: Multi-Agent Coordination ===")

    llm = LLMInterface()
    agent_manager = AgentManager(llm=llm, tool_registry=tool_registry)

    # Create multiple agents
    agents = []
    for i, (name, role) in enumerate(
        [
            ("Researcher", "researcher"),
            ("Analyzer", "analyst"),
            ("Planner", "planner"),
        ]
    ):
        agent = agent_manager.create_agent(
            name=f"{name} Agent {i+1}",
            role=role,
            description=f"Specialized in {role}",
        )
        agents.append(agent)

    # Show system status
    status = agent_manager.get_status()
    print(f"System status: {status}")


async def example_voice_interaction():
    """Example: Voice interaction (if hardware available)."""
    print("\n=== Example: Voice Interaction ===")

    voice = VoiceInterface()

    # Text-to-speech
    success = await voice.tts.speak("Hello! This is the AI Agent System.")
    print(f"TTS success: {success}")

    # Speech-to-text (requires microphone)
    # text = await voice.stt.listen(timeout=5)
    # print(f"Heard: {text}")


async def main():
    """Run all examples."""
    print("Autonomous AI Agent System - Examples\n")

    try:
        await example_knowledge_graph()
        await example_memory_system()
        await example_llm_interaction()
        await example_tool_usage()
        await example_multi_agent_coordination()
        # await example_voice_interaction()  # Uncomment to test voice

        # Uncomment to test agent execution:
        # await example_basic_agent()

        print("\n=== All examples completed ===")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
