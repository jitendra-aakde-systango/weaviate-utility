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
    def __init__(self, weaviate_host: str, weaviate_port: str, weaviate_api_key: str, llm_provider: str = None, llm_api_key: str = None) -> None:
        self.weaviate_host = weaviate_host
        self.weaviate_port = weaviate_port
        self.weaviate_api_key = weaviate_api_key
        self.llm_provider = llm_provider.lower() if llm_provider else None
        self.llm_api_key = llm_api_key

    def _get_provider_header(self):
        """Get the appropriate header based on LLM provider selection"""
        if not self.llm_provider or not self.llm_api_key:
            return {}  # Return empty dict if no LLM provider configured
        
        if self.llm_provider == "gemini":
            return {"X-Google-Studio-Api-Key": self.llm_api_key}
        else:
            return {"X-OpenAI-Api-Key": self.llm_api_key}
    
    def connect(self):
        try:
            # Get the appropriate headers based on LLM provider
            provider_headers = self._get_provider_header()
            
            # Auto-detect if secure connection is needed (for cloud deployments)
            # Use secure if host is not localhost/127.0.0.1 or if port is 443/8443
            is_cloud_deployment = self.weaviate_host not in ['localhost', '127.0.0.1']
            use_secure = is_cloud_deployment or str(self.weaviate_port) in ['443', '8443']
            
            # Convert port to int
            port_int = int(self.weaviate_port) if self.weaviate_port else (443 if use_secure else 8080)
            
            st.info(f"🔄 Connecting to {self.weaviate_host}:{port_int} ({'secure' if use_secure else 'insecure'})...")
            
            self.client = weaviate.connect_to_custom(
                http_host=self.weaviate_host,
                http_port=port_int,
                http_secure=use_secure,
                grpc_host=GRPC_HOST if GRPC_HOST else self.weaviate_host,  
                grpc_port=int(GRPC_PORT) if GRPC_PORT else 50051,  
                grpc_secure=use_secure,
                auth_credentials=Auth.api_key(self.weaviate_api_key),
                skip_init_checks=False,  # Enable checks for better error messages
                headers=provider_headers
            )
            
            # Test the connection
            if self.client.is_ready():
                st.success("✅ Connection established successfully!")
                return True
            else:
                st.error("❌ Weaviate client created but not ready. Check if your instance is running.")
                return False
                
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Connection error: {error_msg}")
            
            # Provide helpful debugging information
            with st.expander("🔍 Debugging Information"):
                st.write(f"**Host:** {self.weaviate_host}")
                st.write(f"**Port:** {self.weaviate_port}")
                st.write(f"**Using secure connection:** {use_secure if 'use_secure' in locals() else 'Unknown'}")
                st.write(f"**Error type:** {type(e).__name__}")
                st.write(f"**Full error:** {error_msg}")
                
                st.markdown("""
                **Common issues:**
                - ❌ Firewall blocking connection from Streamlit Cloud
                - ❌ Incorrect host or port
                - ❌ Weaviate instance not running
                - ❌ API key is invalid
                - ❌ Security group rules not allowing external access (AWS)
                - ❌ Need to use HTTPS instead of HTTP for cloud deployments
                """)
            
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
        limit: int = DEFAULT_LIMIT,
        search_type: str = "keyword"
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

        # Execute different queries based on search type
        if search_type == "keyword":
            # BM25 keyword search
            result = collection.query.bm25(
                query=query,
                limit=limit,
                return_properties=properties,
                return_metadata=metadata_query
            )
        elif search_type == "near_text":
            # Near text semantic search
            result = collection.query.near_text(
                query=query,
                limit=limit,
                return_properties=properties,
                return_metadata=metadata_query
            )
        elif search_type == "hybrid":
            # Hybrid search (combination of keyword and vector)
            result = collection.query.hybrid(
                query=query,
                alpha=alpha,
                limit=limit,
                return_properties=properties,
                fusion_type=fusion_type,
                return_metadata=metadata_query
            )
        else:
            # Default to keyword search if unknown type
            result = collection.query.bm25(
                query=query,
                limit=limit,
                return_properties=properties,
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
