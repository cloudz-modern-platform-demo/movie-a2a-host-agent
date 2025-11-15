"""ZMP A2A Agent Test."""

import logging
import logging.config
import warnings

from movie_a2a_host_agent.setting import logger_settings

logging.config.fileConfig(logger_settings.config_file, disable_existing_loggers=False)
logging.getLogger("appLogger").setLevel(logging.INFO)


warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
logging.getLogger("httpcore.http11").setLevel(logging.INFO)
logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)
logging.getLogger("httpcore.connection").setLevel(logging.INFO)
logging.getLogger("openai._base_client").setLevel(logging.INFO)
logging.getLogger("anthropic._base_client").setLevel(logging.INFO)
logging.getLogger("langchain").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("asgi").setLevel(logging.INFO)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("mcp.client.sse").setLevel(logging.INFO)
logging.getLogger("mcp.client.streamable_http").setLevel(logging.INFO)
logging.getLogger("pydantic").setLevel(logging.WARNING)
logging.getLogger("langsmith.client").setLevel(logging.INFO)
logging.getLogger("a2a.utils.telemetry").setLevel(logging.INFO)
logging.getLogger("a2a.server.events").setLevel(logging.INFO)
logging.getLogger("a2a.server.tasks").setLevel(logging.INFO)
logging.getLogger("sse_starlette.sse").setLevel(logging.INFO)
