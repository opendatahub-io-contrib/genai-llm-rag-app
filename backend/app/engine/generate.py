from dotenv import load_dotenv

load_dotenv()

import os
import logging
from pymilvus import Collection, utility, connections, CollectionSchema, FieldSchema, DataType
from llama_index.core.storage import StorageContext
from llama_index.core.indices import VectorStoreIndex
from llama_index.vector_stores.milvus import MilvusVectorStore
from app.settings import init_settings
from app.engine.loaders import get_documents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
"""
def vdb_init():
    # Ensure environment variables are loaded correctly
    host = os.getenv("MILVUS_ADDRESSS")
    port = 19530  # Default port for Milvus, adjust if necessary
    username = os.getenv("MILVUS_USERNAME")
    password = os.getenv("MILVUS_PASSWORD")

    # Debugging: Print the environment variables
    logger.info(f"MILVUS_ADDRESS: {host}")
    logger.info(f"MILVUS_USERNAME: {username}")
    logger.info(f"MILVUS_PASSWORD: {password}")
    logger.info(f"MILVUS_COLLECTION: {os.getenv('MILVUS_COLLECTION')}")
    logger.info(f"EMBEDDING_DIM: {os.getenv('EMBEDDING_DIM')}")

    # Check if host is correctly set
    if not isinstance(host, str) or not host:
        raise ValueError("MILVUS_ADDRESS environment variable is not set or is not a valid string.")

    # Connect to Milvus with authentication details
    connections.connect(
        alias="default",
        host=host,
        port=port,
        user=username,
        password=password,
        secure=False  # Adjust if SSL/TLS is used
    )

    collection_name = os.getenv("MILVUS_COLLECTION")

    # Check if the specified collection exists
    if utility.has_collection(collection_name):
        logger.info(f"Collection {collection_name} exists. Deleting...")
        utility.drop_collection(collection_name)
        logger.info(f"Collection {collection_name} deleted.")

"""


def generate_datasource():
   # vdb_init()
    init_settings()
    logger.info("Creating new index")
    # load the documents and create the index
    documents = get_documents()
    store = MilvusVectorStore(
        uri=os.environ["MILVUS_ADDRESS"],
        user=os.getenv("MILVUS_USERNAME"),
        password=os.getenv("MILVUS_PASSWORD"),
        collection_name=os.getenv("MILVUS_COLLECTION"),
        dim=int(os.getenv("EMBEDDING_DIM")),
        overwrite=True,
    )
    storage_context = StorageContext.from_defaults(vector_store=store)
    
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,  # this will show you a progress bar as the embeddings are created
        
    )
    logger.info(f"Successfully created embeddings in the Milvus")
    


if __name__ == "__main__":
    generate_datasource()
