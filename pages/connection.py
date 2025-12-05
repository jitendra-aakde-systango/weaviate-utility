import streamlit as st
from utility.weaviate import Weaviate
from constants import SEARCH_TYPES, DEFAULT_SEARCH_TYPE

def connection():
    st.markdown(
        """
        <style>
            [data-testid="collapsedControl"] {
                display: none
            }
            
            .connection-info {
                background: rgba(45, 45, 45, 0.6);
                padding: 1rem;
                border-radius: 10px;
                border: 1px solid #555555;
                margin: 1rem 0;
            }
            
            .connection-info h4 {
                color: #ffffff;
                margin-bottom: 0.5rem;
            }
            
            .connection-info p {
                color: #cccccc;
                margin: 0.25rem 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Beautiful header
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title" style="font-size:24px; font-weight:600;">🔍 Weaviate Utility</div>
        <div class="header-subtitle" style="font-size:16px; color:gray;">
            Connect to your Weaviate instance and explore your data
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Create centered container for connection form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔧 Weaviate Connection")
        
        st.markdown("""
        <div class="connection-info">
            <h4>ℹ️ Connection Requirements</h4>
            <p>Please provide your Weaviate instance details</p>
            <p>Make sure your Weaviate instance is running and accessible</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🌐 Connection Details")
        
        col_host, col_port = st.columns(2)
        with col_host:
            host = st.text_input(
                "Connection Host", 
                placeholder="127.0.0.1 or localhost",
                help="Enter your Weaviate host address",
                key="manual_host"
            )
        with col_port:
            port = st.text_input(
                "Connection Port", 
                placeholder="8080",
                help="Enter your Weaviate port number",
                key="manual_port"
            )
        
        api_key = st.text_input(
            "API Key", 
            type="password", 
            placeholder="Your Weaviate API Key",
            help="Enter your Weaviate API key for authentication",
            key="manual_api_key"
        )
        
        st.markdown("#### 🔍 Search Configuration")
        search_type = st.selectbox(
            "Search Type",
            options=list(SEARCH_TYPES.keys()),
            format_func=lambda x: SEARCH_TYPES[x]["label"],
            help="Select your preferred search method. Near Text and Hybrid searches require an LLM API key for vectorization. Only Keyword (BM25) search works without an LLM API key.",
            key="manual_search_type",
            index=0  # Default to keyword search
        )
        
        # Show info about search type
        if SEARCH_TYPES[search_type]["needs_llm"]:
            st.warning("""
            **⚠️ LLM API Key Required** - Your query needs to be vectorized using the same provider (OpenAI/Gemini) that embedded your collection.
            
            🔒 **Security:** Stored in session only • Never saved to disk • Auto-cleared on page refresh
            """)
            
            st.markdown("#### 🤖 LLM Provider Selection")
            llm_provider = st.selectbox(
                "Choose LLM Provider",
                options=["OpenAI", "Gemini"],
                help="Select the LLM provider that was used to embed your Weaviate collection",
                key="manual_llm_provider"
            )
            
            # Dynamic API key input based on provider selection
            llm_api_key_label = f"{llm_provider} API Key"
            llm_api_key_placeholder = f"Enter your {llm_provider} API key"
            llm_api_key_help = f"Enter your {llm_provider} API key for LLM operations"
            
            llm_api_key = st.text_input(
                llm_api_key_label,
                type="password",
                placeholder=llm_api_key_placeholder,
                help=llm_api_key_help,
                key="manual_llm_api_key"
            )
        else:
            st.success("✅ This search type doesn't require an LLM API key")
            llm_provider = None
            llm_api_key = None

        st.markdown("---")
        
        # Connection button with loading state
        if st.button("🔧 Connect to Weaviate", use_container_width=True, type="primary"):
            with st.spinner("🔄 Establishing connection..."):
                # Validation
                if not host or not api_key:
                    st.error("❌ Please provide both host and API key!")
                    st.stop()
                if not port:
                    port = "8080"  # Default port
                
                # Only validate LLM API key if search type needs it
                search_type = st.session_state.get("manual_search_type", DEFAULT_SEARCH_TYPE)
                if SEARCH_TYPES[search_type]["needs_llm"]:
                    if not llm_api_key:
                        st.error(f"❌ Please provide your {llm_provider} API key for {SEARCH_TYPES[search_type]['label']}!")
                        st.stop()

                # Test connection
                try:
                    weaviate_client = Weaviate(
                        weaviate_host=host, 
                        weaviate_port=port, 
                        weaviate_api_key=api_key,
                        llm_provider=llm_provider,
                        llm_api_key=llm_api_key
                    )
                    if weaviate_client.connect():
                        st.session_state['host'] = host
                        st.session_state['port'] = port
                        st.session_state['api_key'] = api_key
                        st.session_state['search_type'] = st.session_state.get('manual_search_type', DEFAULT_SEARCH_TYPE)
                        st.session_state['llm_provider'] = llm_provider
                        st.session_state['llm_api_key'] = llm_api_key
                        st.session_state['connection_type'] = "Manual Connection"
                        st.session_state['authenticated'] = True
                        
                        st.success("✅ Successfully connected to Weaviate!")
                        
                        # Show connection summary
                        st.info(f"🔗 Connected to: {host}:{port}")
                        
                        # Auto-redirect after 2 seconds
                        import time
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Connection failed. Please check your credentials and try again.")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")

    # Footer with features
    st.markdown("---")
    st.markdown("### ✨ Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔍 Search Options**
        - Keyword Search (BM25)
        - Near Text (Semantic)
        - Hybrid Search
        - Advanced Filtering
        """)
    
    with col2:
        st.markdown("""
        **📊 Analytics**
        - Query Performance Metrics
        - Result Insights & Statistics
        - Search History Tracking
        - Data Distribution Analysis
        """)
    
    with col3:
        st.markdown("""
        **🛠️ Tools**
        - Interactive Property Explorer
        - Dynamic Class Browser
        - Multi-format Data Export
        - Real-time Visualizations
        """)
