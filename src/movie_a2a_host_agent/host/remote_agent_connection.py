"""Remote agent connection for the Movie A2A Host Agent."""

import logging
from collections.abc import Callable
from uuid import uuid4

import httpx
from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    JSONRPCErrorResponse,
    Message,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
    SendStreamingMessageResponse,
    SendStreamingMessageSuccessResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
)
from pydantic import BaseModel

logger = logging.getLogger(__name__)

TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent
TaskUpdateCallback = Callable[[TaskCallbackArg, AgentCard], Task]


class StreamResponse(BaseModel):
    data: str


class RemoteAgentConnections:
    """A class to hold the connections to the remote agents."""

    def __init__(self, client: httpx.AsyncClient, agent_card: AgentCard):
        """Initialize the RemoteAgentConnections."""
        self.agent_client = A2AClient(client, agent_card)
        self.card = agent_card
        self.pending_tasks = set()
        logger.info(f"Initialized remote agent connections for {agent_card.name}")

    def get_agent(self) -> AgentCard:
        """Get the agent card."""
        return self.card

    async def send_message(
        self,
        request: MessageSendParams,
        task_callback: TaskUpdateCallback | None,
    ) -> (
        Task
        | Message
        | TaskStatusUpdateEvent
        | TaskArtifactUpdateEvent
        | StreamResponse
    ):
        """Send a message to the remote agent."""
        if self.card.capabilities.streaming:
            # task = None
            # async for response in self.agent_client.send_message_streaming(
            #     SendStreamingMessageRequest(id=str(uuid4()), params=request)
            # ):
            response = self.agent_client.send_message_streaming(
                SendStreamingMessageRequest(id=str(uuid4()), params=request)
            )
            logger.debug(f"response: {response}")

            data: list[str] = []
            async for chunk in response:
                # print(type(chunk))
                # print(json.dumps(chunk.model_dump(mode='json', exclude_none=True), indent=2))
                if isinstance(chunk, SendStreamingMessageResponse):
                    root = chunk.root
                    if isinstance(root, SendStreamingMessageSuccessResponse):
                        result = root.result
                        if isinstance(result, TaskStatusUpdateEvent):
                            if not result.final:
                                status = result.status
                                if status.state == TaskState.working:
                                    # print(f"::::::::1 {type(status)} = {status}")
                                    message = status.message
                                    if isinstance(message, Message) and message:
                                        if message.parts[0].root.kind == "text":
                                            # print(message.parts[0].root.text, end="", flush=True)
                                            print(".", end="", flush=True)
                                            data.append(message.parts[0].root.text)
                                        else:
                                            # print(f"{status.state.value}")
                                            data.append(status.state.value)
                                else:
                                    state = result.status.state.value
                                    print(
                                        f":::TaskStatusUpdateEvent: final={result.final}, state={state}",
                                        end="\n\n",
                                        flush=True,
                                    )
                            else:
                                state = result.status.state.value
                                print(
                                    f":::TaskStatusUpdateEvent: final={result.final}, state={state}",
                                    end="\n\n",
                                    flush=True,
                                )
                        elif isinstance(result, TaskArtifactUpdateEvent):
                            text = result.artifact.parts[0].root.text
                            print(
                                f"\n\n:::TaskArtifactUpdateEvent: {text}",
                                end="\n\n",
                                flush=True,
                            )
                        elif isinstance(result, Task):
                            text = result.history[-1].parts[-1].root.text
                            state = result.status.state.value
                            print(
                                f":::Task: state={state}, text={text}",
                                end="\n\n",
                                flush=True,
                            )
                        elif isinstance(result, Message):
                            logger.info(f"{type(result)} = {result}")
                        else:
                            logger.info(f"{type(result)} = {result}")
                    else:
                        logger.error(f"error : {chunk}")
                else:
                    logger.error(f"error : {chunk}")

            # print(f"data : {"".join(data)}")
            rv = StreamResponse(data="".join(data))

            return rv
        else:
            # Non-streaming
            response = await self.agent_client.send_message(
                SendMessageRequest(id=str(uuid4()), params=request)
            )
            root = response.root
            if isinstance(root, JSONRPCErrorResponse):
                return root.error

            if isinstance(root.result, Message):
                return root.result
            elif isinstance(root.result, Task):
                return root.result

            # if task_callback:
            #     task_callback(response.root.result, self.card)
            # return response.root.result
