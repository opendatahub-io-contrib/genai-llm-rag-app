"""Entry point for batch load of data into milvus."""
import logging
import os

from app.engine.loaders import get_documents
from app.settings import init_settings

from dotenv import load_dotenv

from llama_index.core.indices import VectorStoreIndex
from llama_index.core.storage import StorageContext
from llama_index.vector_stores.milvus import MilvusVectorStore

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def generate_datasource():
    """Load the documents and create the index."""
    init_settings()
    logger.info('Creating new index')
    documents = get_documents()
    store = MilvusVectorStore(
        uri=os.environ['MILVUS_ADDRESS'],
        user=os.getenv('MILVUS_USERNAME'),
        password=os.getenv('MILVUS_PASSWORD'),
        collection_name=os.getenv('MILVUS_COLLECTION'),
        dim=int(os.getenv('EMBEDDING_DIM')),
        overwrite=True,
    )
    storage_context = StorageContext.from_defaults(vector_store=store)

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,  # this will show you a progress bar as the embeddings are created
    )
    logger.info('Successfully created embeddings in the Milvus')


if __name__ == '__main__':
    generate_datasource()
