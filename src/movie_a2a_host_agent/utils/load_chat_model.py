"""Utility & helper functions."""

import logging

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

logger = logging.getLogger("appLogger")


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(
    fully_specified_name: str, temperature: float = 0.0, max_tokens: int = 5000
) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
        temperature (float): Temperature for the model.
        max_tokens (int): Maximum tokens for the model.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)

    logger.info(f"Provider: {provider} Model: {model} Temperature: {temperature}")

    return init_chat_model(
        model,
        model_provider=provider,
        configurable_fields=["temperature", "max_tokens"],
        temperature=temperature,
        max_tokens=max_tokens,
    )
