import os
from dotenv import load_dotenv

load_dotenv()

CUSTOM_DEPLOYMENT = os.environ.get("CUSTOM_DEPLOYMENT", "false").lower() == "true"
PROJECT_NAME = os.environ.get("PROJECT_NAME")
if CUSTOM_DEPLOYMENT and not PROJECT_NAME:
    PROJECT_NAME = "Custom"
WEAVIATE_HOST = os.environ.get("WEAVIATE_HOST", "localhost")
WEAVIATE_PORT= os.environ.get("WEAVIATE_PORT")
WEAVIATE_API_KEY = os.environ.get("WEAVIATE_API_KEY")
MASTER_PASSWORD = os.environ.get("MASTER_PASSWORD")
GRPC_PORT= os.environ.get("GRPC_PORT", "50051")
GRPC_HOST= os.environ.get("GRPC_HOST", "localhost")
