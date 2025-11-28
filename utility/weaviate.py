import traceback
import weaviate
import warnings

import streamlit as st
import weaviate.classes as wvc
from weaviate.classes.query import HybridFusion
from weaviate.classes.init import Auth
from urllib.parse import urlparse

from env import GRPC_HOST, GRPC_PORT
from constants import ADDITIONALS, DEFAULT_ALPHA, DEFAULT_FUSION, DEFAULT_LIMIT, DEFAULT_WITH_ADDITIONAL

warnings.filterwarnings("ignore", category=ResourceWarning)

class Weaviate:
    def __init__(self, weaviate_host: str, weaviate_port: str, weaviate_api_key: str, llm_provider: str = "openai", llm_api_key: str = None) -> None:
        self.weaviate_host = weaviate_host
        self.weaviate_port = weaviate_port
        self.weaviate_api_key = weaviate_api_key
        self.llm_provider = llm_provider.lower()
        self.llm_api_key = llm_api_key

    def _get_provider_header(self):
        """Get the appropriate header based on LLM provider selection"""
        if not self.llm_api_key:
            raise ValueError(f"LLM API key is required for {self.llm_provider} provider")
        
        if self.llm_provider == "gemini":
            return {"X-Google-Studio-Api-Key": self.llm_api_key}
        else:
            return {"X-OpenAI-Api-Key": self.llm_api_key}
    
    def connect(self):
        try:
            # Get the appropriate headers based on LLM provider
            provider_headers = self._get_provider_header()
            
            self.client = weaviate.connect_to_custom(
                http_host=self.weaviate_host,
                http_port=self.weaviate_port,
                http_secure=False,
                grpc_host=GRPC_HOST if GRPC_HOST else self.weaviate_host,  
                grpc_port=GRPC_PORT if GRPC_PORT else 50051,  
                grpc_secure=False,
                auth_credentials=Auth.api_key(self.weaviate_api_key),
                skip_init_checks=True,
                headers=provider_headers
            )
            return True
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            return False

    def get_classes(self) -> list:
        objects = self.client.collections.list_all()
        return list(objects.keys()) 

    def query(
        self,
        class_name,
        query: str = None,
        properties: list = None,
        alpha: float = DEFAULT_ALPHA,
        with_additional: list = DEFAULT_WITH_ADDITIONAL,
        fusion: str = DEFAULT_FUSION,
        limit: int = DEFAULT_LIMIT
    ):
        collection = self.client.collections.get(class_name)

        fusion_type = HybridFusion.RELATIVE_SCORE if fusion == "relative" else HybridFusion.RANKED
        
        metadata_query = wvc.query.MetadataQuery(score=False,explain_score=False, certainty=False, distance=False)

        for prop in ADDITIONALS:
            if prop in with_additional and prop != "id":
                setattr(metadata_query, prop, True)

        if not query:
            query = "*"
            
        if not properties:
            properties = st.session_state.get("properties_options", [])

        result = collection.query.hybrid(
                    query=query,
                    alpha=alpha,
                    limit=limit,
                    return_properties=properties,
                    fusion_type=fusion_type,
                    return_metadata=metadata_query
                )
        try:
            objects_dict = []

            for obj in result.objects:
                if hasattr(obj, 'properties') and hasattr(obj, 'metadata'):
                    obj_data = {}

                    # Check if 'with_additional' contains 'id' and if so, add it to obj_data
                    if 'id' in with_additional:
                        obj_data["id"] = str(obj.uuid)

                    # Add metadata attributes, skipping '__dict__' and None values
                    for key, value in obj.metadata.__dict__.items():
                        if key != '__dict__' and value is not None:
                            obj_data[key] = value

                    # Add properties to the object data
                    for key, value in obj.properties.items():
                        obj_data[key] = value

                    # Append the object data to the result list
                    objects_dict.append(obj_data)

            return objects_dict

        except Exception as e:
            st.error(f"Query failed: {str(e)}")
            return None
