"""Vector index loader."""
import logging
import os

from llama_index.core.indices import VectorStoreIndex
from llama_index.vector_stores.milvus import MilvusVectorStore

logger = logging.getLogger('uvicorn')

index_config = {
    # FIXME: Parameterize
    'index_name': 'embedding'
}


def get_index():
    """Connect to a milvus store index."""
    logger.info('Connecting to index from Milvus...')
    store = MilvusVectorStore(
        uri=os.getenv('MILVUS_ADDRESS'),
        user=os.getenv('MILVUS_USERNAME'),
        password=os.getenv('MILVUS_PASSWORD'),
        collection_name=os.getenv('MILVUS_COLLECTION'),
        dim=int(os.getenv('EMBEDDING_DIM')),
        index_config=index_config,
    )
    index = VectorStoreIndex.from_vector_store(store)
    logger.info('Finished connecting to index from Milvus.')
    return index
