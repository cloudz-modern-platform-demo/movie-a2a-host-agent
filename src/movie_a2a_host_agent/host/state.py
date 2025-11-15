"""Define the state structures for the Movie A2A Host Agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep, RemainingSteps
from typing_extensions import Annotated


@dataclass
class InputState:
    """Defines the input state for the agent, representing a narrower interface to the outside world.

    This class is used to define the initial state and structure of incoming data.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )
    session_active: Annotated[bool, "Whether the session is active"] = field(
        default=True
    )
    context_id: Annotated[str, "The context ID"] = field(default=None)
    task_id: Annotated[str, "The task ID"] = field(default=None)
    message_id: Annotated[str, "The message ID"] = field(default=None)
    # agent: Annotated[str, "The agent name"] = field(default=None)
    agents_info: Annotated[str, "The agents info"] = field(default="")

    is_last_step: IsLastStep = field(default=False)

    remaining_steps: RemainingSteps = field(default=0)
