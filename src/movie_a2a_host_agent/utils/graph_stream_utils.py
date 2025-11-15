"""Graph Stream Utils."""

from typing import Any, AsyncIterator, Iterator

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    ToolMessage,
    ToolMessageChunk,
)
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.schema import EventData, StreamEvent


def print_invoke(response: dict[str, Any], stream_mode: str = "updates") -> None:
    """Print the invoke response."""
    if stream_mode == "updates":
        for nodes in response:
            for node, value in nodes.items():
                print("=" * 30 + f"{node}" + "=" * 30)
                print(f"{value}")
    else:
        for key, value in response.items():
            print(f"{key} : {value}")


def print_stream(
    response: Iterator[dict[str, Any]], stream_mode: str = "updates"
) -> None:
    """Print the stream response."""
    if stream_mode == "updates":
        for chunk in response:
            for node, value in chunk.items():
                print("=" * 30 + f"{node}" + "=" * 30)
                print(f"{value}")
    elif stream_mode == "values":
        for chunk in response:
            for key, value in chunk.items():
                print("=" * 30 + "=" * 30)
                print(f"{key} : {value}")
    elif stream_mode == "messages":
        first = True
        for chunk_msg, metadata in response:
            # if metadata['ls_model_type'] in ["chat"]:
            # # if metadata['langgraph_node'] in ["retrieve", "sum_up"]:
            #     print(chunk_msg.content, end="", flush=True)
            # else:
            #     print(f"Node metadata ::: {metadata}")

            if not isinstance(
                chunk_msg, AIMessageChunk | ToolMessageChunk | ToolMessage
            ):
                print(f"chunk_msg type ::: {type(chunk_msg)}")

            if isinstance(chunk_msg, AIMessageChunk):
                if first:
                    gathered = chunk_msg
                    first = False
                else:
                    gathered = gathered + chunk_msg

                # if chunk_msg.tool_call_chunks:
                # ai decided to call tool
                # print(
                #     "=========================AIMessageChunk========================="
                # )
                # print(f"Tool Name ::: {gathered.tool_calls[0]['name']}")
                # print(f"Tool Args ::: {gathered.tool_calls[0]['args']}")
                # print(f"Tool Call Chunks ::: {gathered.tool_call_chunks}")
                # else:
                # ai is generating response as stream from the tool call result
                print(chunk_msg.content, end="", flush=True)
            elif isinstance(chunk_msg, ToolMessageChunk):
                # tool message chunk
                print(chunk_msg.content, end="", flush=True)
            elif isinstance(chunk_msg, ToolMessage):
                print("=========================ToolMessage=========================")
                print(f"Tool Type ::: {chunk_msg.type}")
                print(f"Tool Name ::: {chunk_msg.name}")

                if isinstance(chunk_msg.content, str):
                    # print(chunk_msg.content, end="\n", flush=True)
                    print(">>> ToolMessage 1 generated")
                    # chunk_msg.
                elif isinstance(chunk_msg.content, list[str]):
                    for content in chunk_msg.content:
                        # print(content, end="\n", flush=True)
                        print(">>> ToolMessage 2 generated")
    else:
        ...


async def print_astream(
    response: AsyncIterator[dict[str, Any]], stream_mode: str = "updates"
) -> None:
    """Print the async stream response."""
    if stream_mode == "updates":
        async for chunk in response:
            for node, value in chunk.items():
                print("=" * 30 + f"{node}" + "=" * 30)
                print(f"{node} : {value}")
    elif stream_mode == "values":
        async for chunk in response:
            for key, value in chunk.items():
                print("=" * 30 + f"{key}:{type(value[-1])}" + "=" * 30)
                message = value[-1]
                if isinstance(message, AIMessage):
                    tool_calls = message.tool_calls
                    if tool_calls:
                        for tool_call in tool_calls:
                            print(f"{key} : {tool_call['name']}")
                            print(f"{key} : {tool_call['args']}")
                    else:
                        print(f"{key} : {message.content}")
                elif isinstance(message, ToolMessage):
                    print(f"{key} : {message.content}")
                else:
                    print(f"{key} : {value[-1]}")
    elif stream_mode == "messages":
        # first = True
        async for chunk_msg, metadata in response:
            if not isinstance(
                chunk_msg, AIMessageChunk | ToolMessageChunk | ToolMessage
            ):
                ...
                # print(
                #     f"chunk_msg type ::: {type(chunk_msg)}, content ::: {chunk_msg.content}"
                # )

            if isinstance(chunk_msg, AIMessageChunk):
                # if first:
                #     gathered = chunk_msg
                #     first = False
                # else:
                #     gathered = gathered + chunk_msg

                # if chunk_msg.tool_call_chunks:
                #     print(f"Tool Name ::: {gathered.tool_calls[0]['name']}")
                #     print(f"Tool Args ::: {gathered.tool_calls[0]['args']}")
                # else:
                if chunk_msg.content:
                    if isinstance(chunk_msg.content, str):
                        print(chunk_msg.content, end="", flush=True)
                    elif isinstance(chunk_msg.content, list):
                        for content in chunk_msg.content:
                            if isinstance(content, dict):
                                if content.get("type") == "text":
                                    print(content["text"], end="", flush=True)
                            else:
                                print(content, end="", flush=True)

            elif isinstance(chunk_msg, ToolMessageChunk):
                print(chunk_msg.content, end="", flush=True)
            elif isinstance(chunk_msg, ToolMessage):
                print("=========================ToolMessage=========================")
                print(f"Tool Type ::: {chunk_msg.type}")
                print(f"Tool Name ::: {chunk_msg.name}")
                print(f"Tool status ::: {chunk_msg.status}")
                # print(f"Tool Args ::: {chunk_msg.additional_kwargs['tool_calls'][0]['function']['arguments']}")

                # if isinstance(chunk_msg.content, str):
                #     print(chunk_msg.content, end="\n", flush=True)
                #     print(">>> ToolMessage generated")
                #     chunk_msg.
                # elif isinstance(chunk_msg.content, list[str]):
                #     for content in chunk_msg.content:
                #         print(content, end="\n", flush=True)
                #         print(">>> ToolMessage generated")
    else:
        ...


async def print_astream_event(
    response: AsyncIterator[StreamEvent], config: RunnableConfig | None
) -> None:
    """Print the async stream event."""
    async for event in response:
        kind: str = event.get("event")
        data: EventData = event.get("data")
        name: str = event.get("name")
        # metadata: dict[str, Any] = event.get("metadata")
        # tags: list[str] = event.get("tags")

        input = data.get("input")
        output = data.get("output")

        if kind == "on_chat_model_start":
            print("\n========= on_chat_model_start =========")
            print(f"name ::: {name} started")
            messages = input.get("messages")
            if isinstance(messages, list):
                for message in messages:
                    if isinstance(message, list):
                        for i, msg in enumerate(message):
                            print(f"message {i} ::: {type(msg)}")
                    else:
                        print(f"message ::: {type(message)}")

        elif kind == "on_chat_model_stream":
            chunk: AIMessageChunk = data["chunk"]
            if chunk.content:
                print(chunk.content, end="", flush=True)
        elif kind == "on_chat_model_end":
            print("\n========= on_chat_model_end =========")
            print(f"name ::: {name} finished")
            if isinstance(output, AIMessage):
                if output.tool_calls:
                    print(f"Tool will be called ::: {output.tool_calls}")

        elif kind == "on_tool_start":
            print("\n========= tool_start =========")
            print(f"{name} started")

        elif kind == "on_tool_end":
            print("\n========= tool_end =========")
            print(f"{name} finished")
            if isinstance(output, ToolMessage):
                print(f"{name} result ::: {output.content}")

        # elif kind == "on_chain_start":
        #     print(f"\n========= on_chain_start =========\n")
        #     data = event["data"]
        #     print(data)
        # elif kind == "on_chain_end":
        #     print(f"\n========= on_chain_end =========\n")
        #     data = event["data"]
        #     print(data)
        # elif kind == "on_chain_stream":
        #     print(f"\n========= on_chain_stream =========\n")
        #     data = event["data"]
        #     print(data)
