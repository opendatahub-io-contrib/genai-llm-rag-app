"""Database document loader."""
import logging
from typing import List

from llama_index.readers.database import DatabaseReader

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DBLoaderConfig(BaseModel):
    """Data model for a DB."""

    uri: str
    queries: List[str]


def get_db_documents(configs: list[DBLoaderConfig]):
    """Retreive the documents from a database."""
    docs = []
    for entry in configs:
        loader = DatabaseReader(uri=entry.uri)
        for query in entry.queries:
            logger.info(f'Loading data from database with query: {query}')
            documents = loader.load_data(query=query)
            docs.extend(documents)

    return documents
