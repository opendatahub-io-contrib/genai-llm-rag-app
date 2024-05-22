"""API definition for chatbot interaction with the underlying LLM."""
import logging
from typing import Any, Dict, List, Optional, Tuple

from aiostream import stream

from app.api.routers.messaging import EventCallbackHandler
from app.api.routers.vercel_response import VercelStreamResponse
from app.engine import get_chat_engine

from fastapi import APIRouter, Depends, HTTPException, Request, status

from pydantic import BaseModel

from vllm.core.chat_engine.types import StreamingAgentChatResponse
from vllm.core.llms import ChatMessage, MessageRole
from vllm.core.schema import NodeWithScore

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

chat_router = r = APIRouter()


class _Message(BaseModel):
    """Message data model."""

    role: MessageRole
    content: str


class _ChatData(BaseModel):
    """Chat data data model."""

    messages: List[_Message]

    class Config:
        json_schema_extra = {
            'example': {
                'messages': [{
                    'role': 'user',
                    'content': 'What standards for letters exist?',
                }]
            }
        }


class _SourceNodes(BaseModel):
    """Source nodes data model."""

    # FIXME: A003: don't override the id builtin
    id: str  # noqa: A003
    metadata: Dict[str, Any]
    score: Optional[float]
    text: str

    @classmethod
    def from_source_node(cls, source_node: NodeWithScore):
        return cls(
            id=source_node.node.node_id,
            metadata=source_node.node.metadata,
            score=source_node.score,
            text=source_node.node.text,  # type: ignore
        )

    @classmethod
    def from_source_nodes(cls, source_nodes: List[NodeWithScore]):
        return [cls.from_source_node(node) for node in source_nodes]


class _Result(BaseModel):
    """Result data model."""

    result: _Message
    nodes: List[_SourceNodes]


async def parse_chat_data(data: _ChatData) -> Tuple[str, List[ChatMessage]]:
    """Restructure and parse chat data."""
    # Log input data
    logger.debug(f'Received chat data: {data.json()}')

    # Check preconditions and get last message
    if len(data.messages) == 0:
        logger.error('No messages provided')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No messages provided')
    last_message = data.messages.pop()
    if last_message.role != MessageRole.USER:
        logger.error('Last message must be from user')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Last message must be from user',
        )

    # Convert messages coming from the request to type ChatMessage
    messages = [ChatMessage(role=m.role, content=m.content) for m in data.messages]

    # Log parsed messages
    logger.debug(f'Parsed last message content: {last_message.content}')
    logger.debug(f'Parsed messages: {[msg.dict() for msg in messages]}')

    return last_message.content, messages


@r.post('')
async def chat(
    request: Request,
    data: _ChatData,
    chat_engine: StreamingAgentChatResponse = Depends(get_chat_engine)  # noqa: B008
):
    """Handle a question to the RAG APP."""
    # FIXME: Check logic of the depends code above.
    try:
        last_message_content, messages = await parse_chat_data(data)

        event_handler = EventCallbackHandler()
        chat_engine.callback_manager.handlers.append(event_handler)  # type: ignore
        response = await chat_engine.astream_chat(last_message_content, messages)

        async def content_generator():
            # Yield the text response
            async def _text_generator():
                async for token in response.async_response_gen():
                    yield VercelStreamResponse.convert_text(token)
                # the text_generator is the leading stream, once it's finished, also finish the event stream
                event_handler.is_done = True

            # Yield the events from the event handler
            async def _event_generator():
                async for event in event_handler.async_event_gen():
                    yield VercelStreamResponse.convert_data({
                        'type': 'events',
                        'data': {
                            'title': event.get_title()
                        },
                    })

            combine = stream.merge(_text_generator(), _event_generator())
            async with combine.stream() as streamer:
                async for item in streamer:
                    if await request.is_disconnected():
                        break
                    logger.debug(f'Streaming response item: {item}')
                    yield item

            # Yield the source nodes
            source_nodes_data = {
                'type': 'sources',
                'data': {
                    'nodes': [_SourceNodes.from_source_node(node).dict() for node in response.source_nodes]
                },
            }
            logger.debug(f'Source nodes data: {source_nodes_data}')
            yield VercelStreamResponse.convert_data(source_nodes_data)

        return VercelStreamResponse(content=content_generator())

    except Exception as e:
        logger.error(f'Error processing chat request: {e}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='An error occurred while processing the request.'
        )
