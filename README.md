# Install Langgraph cli
```
pip install -U "langgraph-cli[inmem]"
```

# Install dependencies
```
uv sync

uv pip install -e .
```

# Setup LLM API Key
```
cp .env.example .env
```

# Run a2a host agent
```
langgraph dev --port 10000
```

