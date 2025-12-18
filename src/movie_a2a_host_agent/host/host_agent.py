"""Host agent implementation using LangGraph."""

from __future__ import annotations

import base64
import json
import logging
import uuid

import httpx
from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    DataPart,
    Message,
    MessageSendConfiguration,
    MessageSendParams,
    Part,
    TextPart,
)
from langgraph.graph.state import CompiledStateGraph
from langchain.agents import create_agent

from movie_a2a_host_agent.host.remote_agent_connection import (
    RemoteAgentConnections,
    StreamResponse,
    TaskUpdateCallback,
)
from movie_a2a_host_agent.host.state import InputState
from movie_a2a_host_agent.setting import application_settings
from movie_a2a_host_agent.utils.load_chat_model import load_chat_model

logger = logging.getLogger(__name__)


class HostAgent:
    """The host agent.

    This is the agent responsible for choosing which remote agents to send
    tasks to and coordinate their work.
    """

    def __init__(
        self,
        remote_agent_addresses: list[str],
        http_client: httpx.AsyncClient,
        task_callback: TaskUpdateCallback | None = None,
    ):
        self.task_callback = task_callback
        self.httpx_client = http_client
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ""

    @classmethod
    async def initialize(
        cls,
        remote_agent_addresses: list[str],
        http_client: httpx.AsyncClient,
        task_callback: TaskUpdateCallback | None = None,
    ) -> HostAgent:
        instance = cls(remote_agent_addresses, http_client, task_callback)
        await instance.init_remote_agent_addresses(remote_agent_addresses)
        logger.info(f"Initialized host agent with {instance.agents} agents")

        return instance

    async def init_remote_agent_addresses(self, remote_agent_addresses: list[str]):
        # async with asyncio.TaskGroup() as task_group:
        #     for address in remote_agent_addresses:
        #         task_group.create_task(self.retrieve_card(address))
        for address in remote_agent_addresses:
            await self.retrieve_card(address)

    async def retrieve_card(self, address: str):
        card_resolver = A2ACardResolver(self.httpx_client, address)
        card = await card_resolver.get_agent_card()
        self.register_agent_card(card)

    def register_agent_card(self, card: AgentCard):
        remote_connection = RemoteAgentConnections(self.httpx_client, card)
        self.remote_agent_connections[card.name] = remote_connection
        self.cards[card.name] = card
        agent_info = []
        for ra in self.list_remote_agents():
            agent_info.append(json.dumps(ra))
        self.agents = "\n".join(agent_info)

    def create_agent(self) -> CompiledStateGraph:
        def before_model_callback(state: InputState) -> InputState:
            """Ensure session_active is set to True if not present or False."""
            if not state.session_active:
                return {"session_active": True}
            return state

        return create_agent(
            model=load_chat_model(application_settings.llm_model),
            tools=[
                self.list_remote_agents,
                self.send_message,
            ],
            name="movie_a2a_host_agent",
            # state_schema=InputState,
            system_prompt=self.root_instruction(),
        )

    def root_instruction(self) -> str:
        return """You are an expert delegator that can delegate the user request to the appropriate remote agents.

Discovery:
- You can use `list_remote_agents` to list the available remote agents you can use to delegate the task.

Execution:
- For actionable requests, you can use `send_message` to interact with remote agents to take action.

Be sure to include the remote agent name when you respond to the user.

Please rely on tools to address the request, and don't make up the response. If you are not sure, please ask the user for more details.
Focus on the most recent parts of the conversation primarily.

Please resposne in markdown table format if the response data is a list.
"""

    # @tool
    def list_remote_agents(self):
        """List the available remote agents you can use to delegate the task."""
        if not self.remote_agent_connections:
            return []

        remote_agent_info = []
        for card in self.cards.values():
            remote_agent_info.append(
                {"name": card.name, "description": card.description}
            )
        return remote_agent_info

    # @tool
    async def send_message(self, agent_name: str, message: str):
        """Send a task either streaming (if supported) or non-streaming."""
        logger.info(f"Sending message to {agent_name}: {message}")
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f"Agent {agent_name} not found")
        # tool_context["agent"] = agent_name
        client = self.remote_agent_connections[agent_name]
        if not client:
            raise ValueError(f"Client not available for {agent_name}")
        # taskId = tool_context.get("task_id", None)
        # contextId = tool_context.get("context_id", None)
        # messageId = tool_context.get("message_id", None)
        message_id = str(uuid.uuid4())
        # task: Task
        # if not messageId:
        #     messageId = str(uuid.uuid4())
        request: MessageSendParams = MessageSendParams(
            id=str(uuid.uuid4()),
            message=Message(
                role="user",
                parts=[TextPart(text=message)],
                message_id=message_id,
                # contextId=contextId,
                # taskId=taskId,
            ),
            configuration=MessageSendConfiguration(
                acceptedOutputModes=["text", "text/plain", "image/png"],
            ),
        )

        response = await client.send_message(request, self.task_callback)
        logger.warning(f"response : {type(response)}")
        logger.warning(f"response : {json.dumps(response.model_dump(), indent=4)}")
        if isinstance(response, Message):
            result_data = response.parts[-1].root.text
            logger.warning(f"result_data : {result_data}")
            return result_data
        elif isinstance(response, StreamResponse):
            result_data = response.data
            logger.warning(f"result_data : {result_data}")
            return result_data
        else:
            result_data = response.artifacts[-1].parts[-1].root.text
            logger.warning(f"result_data : {result_data}")
            return result_data
