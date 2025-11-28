import streamlit as st
from utility.weaviate import Weaviate
from env import CUSTOM_DEPLOYMENT, MASTER_PASSWORD, PROJECT_NAME, WEAVIATE_API_KEY, WEAVIATE_HOST, WEAVIATE_PORT

def connection():
    title = "Weaviate Utility"
    if CUSTOM_DEPLOYMENT and PROJECT_NAME:
        title = f"{PROJECT_NAME} {title}"

    # Hiding sidebar
    # st.set_page_config(
    #     initial_sidebar_state="collapsed",
    #     page_title=title.lower()
    # )

    st.markdown(
        """
        <style>
            [data-testid="collapsedControl"] {
                display: none
            }
            
            /* Toggle buttons container */
            .toggle-buttons-container {
                display: flex;
                justify-content: center;
                margin: 2rem 0;
                padding: 2rem;
                background: rgba(45, 45, 45, 0.8);
                border-radius: 15px;
                border: 1px solid #555555;
                flex-direction: column;
                gap: 1.5rem;
                align-items: center;
            }

            .toggle-label {
                color: #cccccc;
                font-weight: 600;
                margin: 0;
                font-size: 1.3rem;
                text-align: center;
            }

            .toggle-description {
                color: #999999;
                font-size: 0.9rem;
                text-align: center;
                margin-top: 0.5rem;
            }

            .buttons-row {
                display: flex;
                gap: 1rem;
                width: 100%;
                max-width: 500px;
            }

            /* Custom button styling for toggle buttons */
            .toggle-button {
                flex: 1;
                padding: 1rem 2rem;
                border-radius: 12px;
                border: 2px solid #555555;
                background: linear-gradient(135deg, #2d2d2d 0%, #404040 100%);
                color: #cccccc;
                font-weight: 600;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: center;
                min-height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-decoration: none;
            }

            .toggle-button:hover {
                background: linear-gradient(135deg, #404040 0%, #555555 100%);
                border-color: #777777;
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            }

            .toggle-button.active {
                background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 100%);
                border-color: #4CAF50;
                color: #4CAF50;
                box-shadow: 0 5px 20px rgba(76, 175, 80, 0.3);
            }

            .toggle-button.active:hover {
                background: linear-gradient(135deg, #2d5a3d 0%, #1a472a 100%);
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
            }

            .toggle-button.manual.active {
                background: linear-gradient(135deg, #1a2a47 0%, #2d3d5a 100%);
                border-color: #2196F3;
                color: #2196F3;
                box-shadow: 0 5px 20px rgba(33, 150, 243, 0.3);
            }

            .toggle-button.manual.active:hover {
                background: linear-gradient(135deg, #2d3d5a 0%, #1a2a47 100%);
                box-shadow: 0 8px 25px rgba(33, 150, 243, 0.4);
            }
            
            .connection-mode-indicator {
                background: linear-gradient(135deg, #2d2d2d 0%, #404040 100%);
                padding: 0.8rem 1.5rem;
                border-radius: 10px;
                border: 1px solid #555555;
                color: #ffffff;
                font-weight: 600;
                text-align: center;
                margin: 0.5rem 0;
                font-size: 1.1rem;
            }
            
            .custom-deployment {
                background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 100%);
                border-color: #4CAF50;
                color: #4CAF50;
            }
            
            .manual-connection {
                background: linear-gradient(135deg, #1a2a47 0%, #2d3d5a 100%);
                border-color: #2196F3;
                color: #2196F3;
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

    # Initialize session state for connection mode
    if 'connection_mode' not in st.session_state:
        st.session_state['connection_mode'] = CUSTOM_DEPLOYMENT

    # Beautiful header
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title" style="font-size:24px; font-weight:600;">🔍 {title}</div>
        <div class="header-subtitle" style="font-size:16px; color:gray;">
            Connect to your Weaviate instance and explore your data
        </div>
    </div>
    """, unsafe_allow_html=True)


    # Connection mode toggle buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # st.markdown("""
        # <div class="toggle-buttons-container">
        #     <span class="toggle-label">🔄 Connection Mode Selection</span>
        #     <span class="toggle-description">Choose your preferred connection method</span>
        # </div>
        # """, unsafe_allow_html=True)
        
        # Two button approach
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button(
                "🏢 Custom Deployment",
                key="custom_deployment_btn",
                use_container_width=True,
                type="primary" if st.session_state['connection_mode'] else "secondary"
            ):
                st.session_state['connection_mode'] = True
                st.rerun()
        
        with col_btn2:
            if st.button(
                "🔧 Manual Connection",
                key="manual_connection_btn", 
                use_container_width=True,
                type="primary" if not st.session_state['connection_mode'] else "secondary"
            ):
                st.session_state['connection_mode'] = False
                st.rerun()
        
        # Connection mode indicator
        # if st.session_state['connection_mode']:
        #     st.markdown("""
        #     <div class="connection-mode-indicator custom-deployment">
        #         🏢 Custom Deployment Mode Active
        #     </div>
        #     """, unsafe_allow_html=True)
        # else:
        #     st.markdown("""
        #     <div class="connection-mode-indicator manual-connection">
        #         🔧 Manual Connection Mode Active
        #     </div>
        #     """, unsafe_allow_html=True)

    # Create centered container for connection form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        # Connection form based on mode
        if st.session_state['connection_mode']:
            # Custom Deployment Mode
            st.markdown("### 🏢 Custom Deployment Connection")
            # st.markdown("---")
            
            # Show deployment information
            st.markdown("""
            <div class="connection-info">
                <h4>📋 Deployment Information</h4>
                <p><strong>Host:</strong> {}</p>
                <p><strong>Port:</strong> {}</p>
                <p><strong>Status:</strong> Pre-configured deployment</p>
            </div>
            """.format(WEAVIATE_HOST or "Not configured", WEAVIATE_PORT or "Not configured"), unsafe_allow_html=True)
            
            st.markdown("#### 🤖 LLM Provider Selection")
            llm_provider = st.selectbox(
                "Choose LLM Provider",
                options=["OpenAI", "Gemini"],
                help="Select the LLM provider for vectorization and generative queries",
                key="custom_llm_provider"
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
                key="custom_llm_api_key"
            )
            
            st.markdown("#### 🔐 Authentication Required")
            input_password = st.text_input(
                "Master Password: systango", 
                type="password",
                placeholder="Enter your master password",
                help="Enter the master password to access this custom deployment",
                key="custom_password"
            )
            
            # Set pre-configured values
            host = WEAVIATE_HOST
            port = WEAVIATE_PORT
            api_key = WEAVIATE_API_KEY
            
            # Show benefits of custom deployment
            # st.markdown("""
            # **✅ Custom Deployment Benefits:**
            # - Pre-configured connection settings
            # - Enhanced security with master password
            # - Optimized for your specific use case
            # - Managed infrastructure
            # """)
            
        else:
            # Manual Connection Mode
            st.markdown("### 🔧 Manual Weaviate Connection")
            # st.markdown("---")
            
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
            
            st.markdown("#### 🤖 LLM Provider Selection")
            llm_provider = st.selectbox(
                "Choose LLM Provider",
                options=["OpenAI", "Gemini"],
                help="Select the LLM provider for vectorization and generative queries",
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
            
            # Show manual connection tips
            # st.markdown("""
            # **💡 Connection Tips:**
            # - Ensure Weaviate is running on the specified host and port
            # - Check firewall settings if connection fails
            # - Verify your API key is correct
            # - Use localhost or 127.0.0.1 for local instances
            # """)

        st.markdown("---")
        
        # Connection button with loading state
        connect_button_text = "🏢 Connect to Custom Deployment" if st.session_state['connection_mode'] else "🔧 Connect to Weaviate"
        
        if st.button(connect_button_text, use_container_width=True, type="primary"):
            with st.spinner("🔄 Establishing connection..."):
                # Validation based on connection mode
                if st.session_state['connection_mode']:
                    if not input_password:
                        st.error("❌ Please enter the master password!")
                        st.stop()
                    if input_password != MASTER_PASSWORD:
                        st.error("❌ Invalid master password! Please try again.")
                        st.stop()
                    if not host or not api_key:
                        st.error("❌ Custom deployment configuration is incomplete. Please contact administrator.")
                        st.stop()
                    if not llm_api_key:
                        st.error(f"❌ Please provide your {llm_provider} API key!")
                        st.stop()
                else:
                    if not host or not api_key:
                        st.error("❌ Please provide both host and API key!")
                        st.stop()
                    if not port:
                        port = "8080"  # Default port
                    if not llm_api_key:
                        st.error(f"❌ Please provide your {llm_provider} API key!")
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
                        st.session_state['llm_provider'] = llm_provider
                        st.session_state['llm_api_key'] = llm_api_key
                        st.session_state['connection_type'] = "Custom Deployment" if st.session_state['connection_mode'] else "Manual Connection"
                        st.session_state['authenticated'] = True
                        
                        success_message = f"✅ Successfully connected via {'Custom Deployment' if st.session_state['connection_mode'] else 'Manual Connection'}!"
                        st.success(success_message)
                        # st.balloons()
                        
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

        st.markdown('</div>', unsafe_allow_html=True)

    # Footer with connection mode comparison
    st.markdown("---")
    st.markdown("### 🔄 Connection Modes Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🏢 Custom Deployment**
        - ✅ Pre-configured settings
        - ✅ Enhanced security
        - ✅ Managed infrastructure  
        - ✅ Single password authentication
        - ✅ Optimized performance
        """)
    
    with col2:
        st.markdown("""
        **🔧 Manual Connection**
        - ✅ Full control over settings
        - ✅ Connect to any Weaviate instance
        - ✅ Flexible configuration
        - ✅ Development friendly
        - ✅ Custom deployments support
        """)

    # Additional features section
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔍 Features**
        - Hybrid Search Capabilities
        - Advanced Data Visualization
        - Real-time Query Performance
        - Export & Download Options
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
        - Advanced Filtering Options
        """)
