"""Streaming response handling overrides for Vercel."""
import json
from typing import Any

from fastapi.responses import StreamingResponse


class VercelStreamResponse(StreamingResponse):
    """Convert the response from the chat engine to the streaming format expected by Vercel."""

    TEXT_PREFIX = '0:'
    DATA_PREFIX = '8:'

    @classmethod
    def convert_text(cls, token: str):
        """Convert the token to the streaming format."""
        # Escape newlines and double quotes to avoid breaking the stream
        token = json.dumps(token)
        return f'{cls.TEXT_PREFIX}{token}\n'

    @classmethod
    def convert_data(cls, data: dict):
        """Convert the data to the streaming format."""
        data_str = json.dumps(data)
        return f'{cls.DATA_PREFIX}[{data_str}]\n'

    def __init__(self, content: Any, **kwargs):
        """Initialize the response."""
        super().__init__(
            content=content,
            **kwargs,
        )
