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
            st.info("🔄 **Step 1/6:** Initializing connection...")
            
            # Get the appropriate headers based on LLM provider
            provider_headers = self._get_provider_header()
            if provider_headers:
                st.success(f"✅ **Step 2/6:** LLM provider headers configured ({list(provider_headers.keys())[0]})")
            else:
                st.info("ℹ️ **Step 2/6:** No LLM provider configured (using keyword search)")
            
            # Auto-detect if secure connection is needed (for cloud deployments)
            # Only use secure for standard HTTPS ports or cloud domains
            is_cloud_deployment = self.weaviate_host not in ['localhost', '127.0.0.1']
            # Use secure only if port is explicitly 443/8443 
            use_secure = str(self.weaviate_port) in ['443', '8443']
            
            # Convert port to int
            port_int = int(self.weaviate_port) if self.weaviate_port else (443 if use_secure else 8080)
            
            # GRPC configuration - use same host and calculate GRPC port
            # For cloud: typically HTTP + 10000 or use 50051
            grpc_host = self.weaviate_host
            if GRPC_PORT:
                grpc_port = int(GRPC_PORT)
            else:
                # Default GRPC port calculation
                grpc_port = 50051 if not is_cloud_deployment else (port_int + 10000 if port_int < 40000 else 50051)
            
            st.info(f"""
            ℹ️ **Step 3/6:** Connection parameters calculated:
            - **Host:** {self.weaviate_host}
            - **HTTP Port:** {port_int}
            - **GRPC Port:** {grpc_port}
            - **Protocol:** {'HTTPS/WSS (secure)' if use_secure else 'HTTP/WS (insecure)'}
            - **Mode:** {'Cloud Deployment' if is_cloud_deployment else 'Local Deployment'}
            """)
            
            st.info("🔄 **Step 4/6:** Creating Weaviate client...")
            
            self.client = weaviate.connect_to_custom(
                http_host=self.weaviate_host,
                http_port=port_int,
                http_secure=use_secure,
                grpc_host=grpc_host,  
                grpc_port=grpc_port,  
                grpc_secure=use_secure,
                auth_credentials=Auth.api_key(self.weaviate_api_key),
                skip_init_checks=False,  # Enable checks for better error messages
                headers=provider_headers
            )
            
            st.success("✅ **Step 5/6:** Weaviate client created successfully!")
            st.info("🔄 **Step 6/6:** Testing connection readiness...")
            
            # Test the connection
            if self.client.is_ready():
                st.success("✅ **Connection Successful!** All steps completed. Weaviate is ready to use.")
                return True
            else:
                st.error("❌ **Step 6/6 Failed:** Weaviate client created but not ready. Instance may not be running or accessible.")
                return False
                
        except Exception as e:
            import traceback
            error_msg = str(e) if str(e) else "Unknown error"
            error_type = type(e).__name__
            error_traceback = traceback.format_exc()
            
            # Display actual error prominently
            st.error(f"""
            ❌ **Connection Failed!**
            
            **Error Type:** {error_type}
            
            **Error Message:** {error_msg}
            """)
            
            # Show full traceback prominently
            st.markdown("### 📋 Full Error Traceback (Actual Error Details):")
            st.code(error_traceback, language="python")
            
            # Check if using private IP from cloud
            if self.weaviate_host.startswith(('192.168.', '10.', '172.')):
                st.warning(f"""
                ⚠️ **Private IP Detected:** `{self.weaviate_host}`
                
                Private IPs (192.168.x.x, 10.x.x, 172.x.x) are NOT accessible from Streamlit Cloud.
                Use a public IP or domain instead.
                """)
            
            # Connection details for debugging
            st.info(f"""
            **Connection Attempted:**
            - Host: `{self.weaviate_host}`
            - HTTP Port: `{port_int if 'port_int' in locals() else self.weaviate_port}`
            - GRPC Port: `{grpc_port if 'grpc_port' in locals() else 'Unknown'}`
            - Secure: `{use_secure if 'use_secure' in locals() else 'Unknown'}`
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
