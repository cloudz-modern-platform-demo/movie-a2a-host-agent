import asyncio
import logging

import httpx
from a2a.types import (
    AgentCard,
    Task,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
)
from dotenv import load_dotenv
from movie_a2a_host_agent.host.host_agent import HostAgent

load_dotenv()

logger = logging.getLogger(__name__)
TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent


async def task_callback(task: TaskCallbackArg, agent_card: AgentCard):
    """Do something with the task."""
    logger.info(f"task_callback : {type(task)}")

    if isinstance(task, TaskStatusUpdateEvent):
        logger.info(f"TaskStatusUpdateEvent : {task}")
        return task
    elif isinstance(task, TaskArtifactUpdateEvent):
        logger.info(f"TaskArtifactUpdateEvent : {task}")
        return task
    elif isinstance(task, Task):
        logger.info(f"Task : {task}")
        return task


async def main():
    host_agent = await HostAgent.initialize(
        ["http://localhost:8300", "http://localhost:9300"],
        httpx.AsyncClient(timeout=300),
        task_callback,
    )
    root_agent = host_agent.create_agent()

    return root_agent


graph = asyncio.run(main())
