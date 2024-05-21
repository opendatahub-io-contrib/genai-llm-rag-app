import os
from llama_parse import LlamaParse
from pydantic import BaseModel, validator


class FileLoaderConfig(BaseModel):
    bucket: str = "rag-data"
    prefix: str = "data"  # Assuming prefix might be used, if applicable
    aws_access_id: str = "oAlJVAeAYLhXzkR6"
    aws_access_secret: str = "uDApf6OmReJu9h6K1PH9ChbTsz5GBciPjccgvfyP"
    s3_endpoint_url: str = "https://s3.tebi.io"
    filename_as_id: bool = True
    recursive: bool = True
    




def get_file_documents(config: FileLoaderConfig):
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
    print(f"Documents retrieved: {documents}")  # Debug: Check what is being loaded

   

    return documents