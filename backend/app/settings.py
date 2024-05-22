import os
from typing import Dict
from llama_index.core.settings import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def init_settings():
    model_provider = os.getenv("MODEL_PROVIDER")
    if model_provider == "openai":
        init_openai()
    elif model_provider == "ollama":
        init_ollama()
    elif model_provider == "anthropic":
        init_anthropic()
    elif model_provider == "gemini":
        init_gemini()
    else:
        raise ValueError(f"Invalid model provider: {model_provider}")
    Settings.chunk_size = int(os.getenv("CHUNK_SIZE", "1024"))
    Settings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "20"))

# Save the original requests.post method
original_post = requests.post

def patched_post(*args, **kwargs):
    kwargs['verify'] = False  # Disable SSL verification
    return original_post(*args, **kwargs)

# Apply the monkey patch
requests.post = patched_post

def init_ollama():

    # Apply the monkey patch
    import httpx

    original_client_init = httpx.Client.__init__
    original_async_client_init = httpx.AsyncClient.__init__

    def new_client_init(self, *args, **kwargs):
        if 'verify' not in kwargs:
            kwargs['verify'] = False
        if 'timeout' not in kwargs:
            kwargs['timeout'] = httpx.Timeout(300.0)  # Set timeout to 300 seconds
        original_client_init(self, *args, **kwargs)

    def new_async_client_init(self, *args, **kwargs):
        if 'verify' not in kwargs:
            kwargs['verify'] = False
        if 'timeout' not in kwargs:
            kwargs['timeout'] = httpx.Timeout(300.0)  # Set timeout to 300 seconds
        original_async_client_init(self, *args, **kwargs)

    httpx.Client.__init__ = new_client_init
    httpx.AsyncClient.__init__ = new_async_client_init

   
    from llama_index.llms.ollama import Ollama
    #from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.llms.vllm import Vllm
    Settings.embed_model = HuggingFaceEmbedding(model_name="mixedbread-ai/mxbai-embed-large-v1")
    logger.debug(f"Embedding model set to: {Settings.embed_model}")
    """
    Settings.llm = Ollama(
    base_url="https://llama3-rag-validated-pattern.apps.rosa-9nlmt.6808.p1.openshiftapps.com",
    model="llama3",
    request_timeout=300.0,
    context_window=8052,
    temperature=1.0,
    

    )
    logger.debug(f"LLM set to: {Settings.llm}")
    """

    Settings.llm =Vllm(
        model="/mnt/models/",
        api_url="https://mistral-rag-validated-pattern.apps.rosa-9nlmt.6808.p1.openshiftapps.com",
        temperature=1.0,
        max_new_tokens=2048,
        
    )
    logger.debug(f"LLM set to: {Settings.llm}")
   



def init_openai():
    from llama_index.llms.openai import OpenAI
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.core.constants import DEFAULT_TEMPERATURE

    max_tokens = os.getenv("LLM_MAX_TOKENS")
    config = {
        "model": os.getenv("MODEL"),
        "temperature": float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_tokens": int(max_tokens) if max_tokens is not None else None,
    }
    Settings.llm = OpenAI(**config)

    dimensions = os.getenv("EMBEDDING_DIM")
    config = {
        "model": os.getenv("EMBEDDING_MODEL"),
        "dimensions": int(dimensions) if dimensions is not None else None,
    }
    Settings.embed_model = OpenAIEmbedding(**config)


def init_anthropic():
    from llama_index.llms.anthropic import Anthropic
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    model_map: Dict[str, str] = {
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
        "claude-2.1": "claude-2.1",
        "claude-instant-1.2": "claude-instant-1.2",
    }

    embed_model_map: Dict[str, str] = {
        "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
        "all-mpnet-base-v2": "sentence-transformers/all-mpnet-base-v2",
    }

    Settings.llm = Anthropic(model=model_map[os.getenv("MODEL")])
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=embed_model_map[os.getenv("EMBEDDING_MODEL")]
    )


def init_gemini():
    from llama_index.llms.gemini import Gemini
    from llama_index.embeddings.gemini import GeminiEmbedding

    model_map: Dict[str, str] = {
        "gemini-1.5-pro-latest": "models/gemini-1.5-pro-latest",
        "gemini-pro": "models/gemini-pro",
        "gemini-pro-vision": "models/gemini-pro-vision",
    }

    embed_model_map: Dict[str, str] = {
        "embedding-001": "models/embedding-001",
        "text-embedding-004": "models/text-embedding-004",
    }

    Settings.llm = Gemini(model=model_map[os.getenv("MODEL")])
    Settings.embed_model = GeminiEmbedding(
        model_name=embed_model_map[os.getenv("EMBEDDING_MODEL")]
    )
