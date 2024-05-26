"""File loader module for the engine."""
import logging

from pydantic import BaseModel

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FileLoaderConfig(BaseModel):
    """Configuration definition for the s3 file loader."""

    # FIXME: Hardcoded needs to be parameterized
    bucket: str = 'rag-data'
    prefix: str = 'data'  # Assuming prefix might be used, if applicable
    aws_access_id: str = ''
    aws_access_secret: str = ''
    s3_endpoint_url: str = 'https://s3.tebi.io'
    filename_as_id: bool = True
    recursive: bool = True


def get_file_documents(config: FileLoaderConfig):
    """Retreive the files from an s3 bucket."""
    from llama_index.readers.s3 import S3Reader

    reader = S3Reader(
        bucket=config.bucket,
        s3_endpoint_url=config.s3_endpoint_url,
        aws_access_id=config.aws_access_id,
        aws_access_secret=config.aws_access_secret,
        recursive=config.recursive
    )

    # Load the data
    documents = reader.load_data()
    logger.debug(f'Documents retrieved: {documents}')
    return documents
