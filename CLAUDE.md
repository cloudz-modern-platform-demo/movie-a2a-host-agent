# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Movie A2A Host Agent** built with LangGraph - a delegating agent that coordinates work across multiple remote A2A (Agent-to-Agent) agents. The host agent receives user requests and routes them to appropriate specialized remote agents using the A2A SDK protocol.

## Development Commands

### Initial Setup
```bash
# Install project dependencies
uv sync

# Install the project in editable mode
uv pip install -e .

# Install LangGraph CLI in the virtual environment (REQUIRED)
uv pip install -U "langgraph-cli[inmem]"
```

**Important**: You MUST install `langgraph-cli` inside the project's virtual environment (`.venv`), not globally. The CLI needs access to the installed project modules.

### Environment Configuration
```bash
# Copy environment template and configure API keys
cp .env.example .env
# Edit .env to add required API keys:
# - OPENAI_API_KEY or ANTHROPIC_API_KEY (for LLM)
# - LANGSMITH_API_KEY (for tracing/monitoring)
# - TAVILY_API_KEY (if using search capabilities)
```

### Running the Agent
```bash
# Activate the virtual environment first
source .venv/bin/activate

# Start the LangGraph development server
langgraph dev

# The host agent will be available at http://127.0.0.1:2024
# Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
# Remote agents should be running on configured ports (default: 8300, 9300)
```

**Important**: Always activate `.venv` before running `langgraph dev`. Running the global `langgraph` command will fail because it cannot find the `movie_a2a_host_agent` module.

## Architecture

### Core Components

**HostAgent** (`src/movie_a2a_host_agent/host/host_agent.py`)
- Main orchestrator that delegates tasks to remote agents
- Initializes connections to multiple remote A2A agents on startup
- Provides two primary tools to the LLM:
  - `list_remote_agents()`: Discover available remote agents and their capabilities
  - `send_message(agent_name, message)`: Delegate tasks to specific remote agents
- Builds a LangGraph agent using `create_agent()` with system prompt for delegation strategy

**RemoteAgentConnections** (`src/movie_a2a_host_agent/host/remote_agent_connection.py`)
- Manages HTTP connections to remote A2A agents
- Handles both streaming and non-streaming message protocols
- Processes A2A protocol responses: Task, Message, TaskStatusUpdateEvent, TaskArtifactUpdateEvent
- Supports real-time streaming with progress indicators

**State Management** (`src/movie_a2a_host_agent/host/state.py`)
- `InputState`: Dataclass defining agent state with LangGraph annotations
- Tracks messages, session status, context/task IDs, and agent information
- Uses `add_messages` reducer for message history management
- Includes `is_last_step` and `remaining_steps` for execution control

**Main Entry Point** (`src/movie_a2a_host_agent/host/main.py`)
- Initializes HostAgent with remote agent addresses (currently hardcoded to localhost:8300, 9300)
- Defines `task_callback` for handling async task updates from remote agents
- Exports the compiled graph for LangGraph server via `graph = asyncio.run(main())`

### Configuration

**Application Settings** (`src/movie_a2a_host_agent/setting.py`)
- Uses `pydantic-settings` for environment-based configuration
- `ApplicationSettings`: Controls LLM model selection (default: `anthropic/claude-sonnet-4-5-20250929`)
- `LoggerSettings`: Configures logging level and config file
- All settings use `APP_` and `LOG_` prefixes for environment variables

**LangGraph Configuration** (`langgraph.json`)
- Defines the graph entry point: `./src/movie_a2a_host_agent/host/main.py:graph`
- Specifies `.env` file for environment variables
- Graph ID: `movie-host-agent`

### Key Patterns

**Async Initialization Pattern**
The HostAgent uses a factory method pattern for async initialization:
```python
host_agent = await HostAgent.initialize(
    remote_agent_addresses,
    http_client,
    task_callback
)
```
This allows async card retrieval from remote agents during setup.

**A2A Protocol Communication**
- Uses `a2a-sdk` for standardized agent-to-agent communication
- Retrieves `AgentCard` from each remote agent to discover capabilities
- Sends `MessageSendParams` with `TextPart` or `DataPart` content
- Handles response types: `Message`, `Task`, or streaming events

**LangGraph Tool Integration**
The host agent exposes Python methods as LLM tools without explicit `@tool` decorators - LangGraph's `create_agent()` handles tool wrapping automatically.

**Streaming Response Handling**
Remote agents may support streaming. The code:
1. Checks `card.capabilities.streaming` flag
2. Processes `SendStreamingMessageResponse` chunks
3. Aggregates text parts into `StreamResponse`
4. Provides real-time progress indicators (dots printed to console)

## Remote Agent Addresses

Currently hardcoded in `main.py`:
- `http://localhost:8300`
- `http://localhost:9300`

To add/modify remote agents, update the list passed to `HostAgent.initialize()`. Each remote agent must:
- Implement the A2A protocol
- Expose an agent card at `/.well-known/agent.json`
- Support message send endpoints

## LLM Model Configuration

Set via environment variable:
```bash
APP_LLM_MODEL="anthropic/claude-sonnet-4-5-20250929"
```

The model is loaded via `load_chat_model()` utility which supports multiple providers through LangChain's model loader.

## Important Implementation Notes

- The host agent does NOT execute tasks itself - it only delegates to remote agents
- Session state tracking (context_id, task_id) is partially implemented but not fully utilized
- Commented code in `send_message()` shows planned features for task state management
- The system prompt emphasizes relying on tools rather than making up responses
- Error handling for agent failures and cancellations is partially implemented
