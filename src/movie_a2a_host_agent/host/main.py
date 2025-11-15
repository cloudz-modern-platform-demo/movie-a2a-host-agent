import asyncio
import logging
import uuid

import httpx
from a2a.types import (
    AgentCard,
    Task,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
)
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from movie_a2a_host_agent.host.host_agent import HostAgent
from movie_a2a_host_agent.host.state import InputState
from movie_a2a_host_agent.utils.graph_stream_utils import print_astream

load_dotenv()

logger = logging.getLogger(__name__)
TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent


async def task_callback(task: TaskCallbackArg, agent_card: AgentCard):
    """Do something with the task."""
    logger.warning(f"task_callback : {type(task)}")
    if isinstance(task, TaskStatusUpdateEvent):
        logger.warning(f"TaskStatusUpdateEvent : {task}")
        return task
    elif isinstance(task, TaskArtifactUpdateEvent):
        logger.warning(f"TaskArtifactUpdateEvent : {task}")
        return task
    elif isinstance(task, Task):
        logger.warning(f"Task : {task}")
        return task


async def main():
    host_agent = await HostAgent.initialize(
        ["http://localhost:8300", "http://localhost:9300"],
        httpx.AsyncClient(timeout=300),
        task_callback,
    )
    root_agent = host_agent.create_agent()

    return root_agent
    # config = RunnableConfig(
    #     configurable={
    #         "thread_id": str(uuid.uuid4()),
    #         "user_id": "kilsoo75",
    #     },
    #     recursion_limit=100,
    # )
    # inputs = InputState(
    #     messages=[
    #         HumanMessage(content="get movies"),
    #     ]
    # )

    # resp = root_agent.astream(inputs, config, stream_mode="messages")
    # # async for item in resp:
    # logger.info("Starting to print stream")
    # await print_astream(resp, stream_mode="messages")


# if __name__ == "__main__":
#     asyncio.run(main())
graph = asyncio.run(main())
