import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

from constants import ADDITIONALS, FUSION_TYPES, LIMIT_MAX_VALUE, LIMIT_DEFAULT_VALUE, LIMIT_MIN_VALUE, SEARCH_TYPES, DEFAULT_SEARCH_TYPE
from utility.base import convert_response_to_df
from utility.weaviate import Weaviate

def home():
    # st.set_page_config(layout='wide')

    # Initialize session state variables
    session_vars = {
        "properties_options": [],
        "properties_disabled": True,
        "properties_default": [],
        "df": pd.DataFrame(),
        "show_table": True,
        "search_history": [],
        "query_stats": {"total_queries": 0, "avg_response_time": 0},
        "selected_visualization": "line"
    }
    
    for var, default in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default

    # Initialize Weaviate client
    weaviate = Weaviate(
        weaviate_host=st.session_state['host'], 
        weaviate_port=st.session_state['port'], 
        weaviate_api_key=st.session_state['api_key'],
        llm_provider=st.session_state.get('llm_provider', 'OpenAI'),
        llm_api_key=st.session_state.get('llm_api_key')
    )
    weaviate.connect()

    # Header with search type indicator
    current_search_type = st.session_state.get("search_type", DEFAULT_SEARCH_TYPE)
    llm_provider = st.session_state.get("llm_provider")
    
    # Create header with search mode and security indicator
    header_html = f"""
    <div style="background: linear-gradient(135deg, #2d2d2d 0%, #404040 100%); 
         padding: 1rem 1.5rem; border-radius: 10px; border: 1px solid #555555; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div>
                <span style="font-size: 1.2rem; font-weight: 600; color: #ffffff;">🔍 Weaviate Data Explorer</span>
            </div>
            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                <div style="background: rgba(76, 175, 80, 0.2); padding: 0.5rem 1rem; border-radius: 8px; border: 1px solid #4CAF50;">
                    <span style="color: #4CAF50; font-weight: 600;">Search: {SEARCH_TYPES[current_search_type]['label']}</span>
                </div>
    """
    
    # Add security badge if LLM is being used
    if llm_provider:
        header_html += f"""
                <div style="background: rgba(33, 150, 243, 0.2); padding: 0.5rem 1rem; border-radius: 8px; border: 1px solid #2196F3;">
                    <span style="color: #2196F3; font-weight: 600;">🔒 {llm_provider} API (Session Only)</span>
                </div>
        """
    
    header_html += """
            </div>
        </div>
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

    # Helper functions
    def handle_class_selection():
        selected_class = st.session_state.get("weaviate_class")
        if selected_class != "Select a class":
            update_properties()
        else:
            st.session_state["properties_disabled"] = True

    def update_properties():
        selected_class = st.session_state["weaviate_class"]
        if selected_class == "Select a class":
            st.session_state["properties_disabled"] = True
            return

        if selected_class:
            try:
                collection = weaviate.client.collections.get(selected_class)
                collection_config = collection.config.get()
                properties = [prop.name for prop in collection_config.properties]
                
                if properties:
                    st.session_state["properties_options"] = properties
                    st.session_state["properties_disabled"] = False
                else:
                    st.error("No properties found in the selected class 😔")
                    st.session_state["properties_disabled"] = True
            except Exception as e:
                st.error(f"Error fetching properties: {str(e)}")
                st.session_state["properties_disabled"] = True

    def apply():
        start_time = datetime.now()
        
        with st.spinner("🔍 Searching your data..."):
            data = weaviate.query(
                class_name=st.session_state["weaviate_class"],
                properties=st.session_state["properties"],
                with_additional=st.session_state["additionals"],
                alpha=st.session_state["alpha"],
                fusion=st.session_state["fusion"],
                query=st.session_state["prompt"],
                limit=st.session_state["limit"],
                search_type=st.session_state.get("search_type", DEFAULT_SEARCH_TYPE)
            )
            
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        if 'errors' in data:
            st.error(f"❌ Query Error: {data['errors'][0]['message']}")
        else:
            df = convert_response_to_df(data)
            if 'score' in df.columns:
                df['score'] = pd.to_numeric(df['score'])
            st.session_state["df"] = df.reset_index()
            
            # Update search history and stats
            search_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query": st.session_state["prompt"],
                "class": st.session_state["weaviate_class"],
                "results": len(df),
                "response_time": response_time
            }
            st.session_state["search_history"].insert(0, search_entry)
            if len(st.session_state["search_history"]) > 10:
                st.session_state["search_history"] = st.session_state["search_history"][:10]
            
            # Update query stats
            st.session_state["query_stats"]["total_queries"] += 1
            current_avg = st.session_state["query_stats"]["avg_response_time"]
            total_queries = st.session_state["query_stats"]["total_queries"]
            st.session_state["query_stats"]["avg_response_time"] = (
                (current_avg * (total_queries - 1) + response_time) / total_queries
            )
            
            st.success(f"✅ Found {len(df)} results in {response_time:.2f} seconds!")

    def select_all_properties():
        if st.session_state["properties_select_all"]:
            st.session_state["properties_default"] = st.session_state["properties_options"]
        else:
            st.session_state["properties_default"] = []

    def properties_changed():
        if len(st.session_state["properties"]) != len(st.session_state["properties_options"]):
            st.session_state["properties_select_all"] = False

    def export_data():
        if not st.session_state["df"].empty:
            csv = st.session_state["df"].to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"weaviate_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Sidebar with enhanced styling
    with st.sidebar:
        # st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        st.markdown("### 🎛️ Query Configuration")
        
        # Class selection
        weaviate_class_options = ["Select a class"] + weaviate.get_classes()
        weaviate_class = st.selectbox(
            label="📊 Weaviate Class",
            options=weaviate_class_options,
            key="weaviate_class",
            index=weaviate_class_options.index(st.session_state["weaviate_class"])
            if "weaviate_class" in st.session_state else 0,
            on_change=handle_class_selection,
            help="Select the Weaviate class to query"
        )

        if st.session_state["weaviate_class"] != "Select a class":
            
            # Properties selection
            properties = st.multiselect(
                "🏷️ Properties",
                options=st.session_state["properties_options"],
                disabled=st.session_state["properties_disabled"],
                key="properties",
                default=st.session_state["properties_default"],
                on_change=properties_changed,
                help="Select properties to retrieve"
            )
            
            select_all_properties = st.checkbox(
                "Select All Properties",
                on_change=select_all_properties,
                key="properties_select_all",
                disabled=st.session_state["properties_disabled"],
            )

            if st.session_state["properties"]:
                
                # Advanced options
                with st.expander("⚙️ Advanced Options", expanded=True):
                    additionals = st.multiselect(
                        "📋 Additional Metadata",
                        options=ADDITIONALS,
                        disabled=st.session_state["properties_disabled"],
                        key="additionals",
                        default=["id"],
                        help="Select additional metadata to include"
                    )
                    
                    # Get current search type
                    current_search_type = st.session_state.get("search_type", DEFAULT_SEARCH_TYPE)
                    
                    # Only show alpha and fusion for hybrid search
                    if current_search_type == "hybrid":
                        col1, col2 = st.columns(2)
                        with col1:
                            alpha = st.slider(
                                label="🎯 Alpha (Hybrid Balance)",
                                min_value=0.0,
                                max_value=1.0,
                                value=0.7,
                                step=0.01,
                                key="alpha",
                                disabled=st.session_state["properties_disabled"],
                                help="Balance between keyword (0) and vector (1) search"
                            )
                        
                        with col2:
                            fusion = st.selectbox(
                                "🔀 Fusion Type",
                                options=FUSION_TYPES,
                                disabled=st.session_state["properties_disabled"],
                                key="fusion",
                                help="Method for combining search results"
                            )
                    else:
                        # For non-hybrid searches, set defaults and show info
                        st.info(f"ℹ️ Using {SEARCH_TYPES[current_search_type]['label']} - Alpha and fusion settings not applicable")
                        # Set default values in session state if not present
                        if "alpha" not in st.session_state:
                            st.session_state["alpha"] = 0.7
                        if "fusion" not in st.session_state:
                            st.session_state["fusion"] = "ranked"
                    
                    limit = st.number_input(
                        "📊 Result Limit",
                        min_value=LIMIT_MIN_VALUE, 
                        max_value=LIMIT_MAX_VALUE,  
                        value=LIMIT_DEFAULT_VALUE,  
                        disabled=st.session_state["properties_disabled"],
                        key="limit",
                        help="Maximum number of results to return"
                    )
                
                # Query input
                prompt = st.text_area(
                    "🔍 Search Query",
                    disabled=st.session_state["properties_disabled"],
                    key="prompt",
                    placeholder="Enter your search query here...",
                    help="Enter your search query (leave empty for wildcard search)",
                    height=100
                )
                
                # Submit button
                apply_button = st.button(
                    label="🚀 Execute Search",
                    on_click=apply,
                    disabled=st.session_state["properties_disabled"],
                    use_container_width=True,
                    type="primary"
                )

        st.markdown('</div>', unsafe_allow_html=True)

    # Main content area
    if not st.session_state["df"].empty:
        # Statistics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(st.session_state["df"])}</div>
                <div class="metric-label">Results Found</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_score = st.session_state["df"]['score'].mean() if 'score' in st.session_state["df"].columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_score:.3f}</div>
                <div class="metric-label">Avg Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{st.session_state["query_stats"]["total_queries"]}</div>
                <div class="metric-label">Total Queries</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_time = st.session_state["query_stats"]["avg_response_time"]
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_time:.2f}s</div>
                <div class="metric-label">Avg Response</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Enhanced tabs for results
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Table", "📈 Visualizations", "📋 Export & History", "🔍 Data Insights"])

        with tab1:
            st.markdown("### 📊 Query Results")
            
            # Search and filter options
            col1, col2 = st.columns([3, 1])
            with col1:
                search_term = st.text_input("🔍 Filter results", placeholder="Search in results...")
            with col2:
                show_all = st.checkbox("Show all columns", value=True)
            
            # Filter dataframe based on search
            display_df = st.session_state["df"]
            if search_term:
                mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                display_df = display_df[mask]
            
            # Display dataframe
            st.dataframe(
                display_df, 
                use_container_width=True, 
                height=600, 
                hide_index=True,
                column_config={
                    "score": st.column_config.ProgressColumn(
                        "Score",
                        help="Relevance score",
                        min_value=0,
                        max_value=1,
                    ),
                }
            )

        with tab2:
            st.markdown("### 📈 Data Visualizations")
            
            if 'score' in st.session_state["df"].columns:
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    viz_type = st.selectbox(
                        "📊 Visualization Type",
                        ["Line Chart", "Bar Chart", "Scatter Plot", "Histogram", "Box Plot"],
                        key="viz_type"
                    )
                    
                    x_axis = st.selectbox(
                        "X-Axis",
                        options=st.session_state["df"].columns,
                        index=st.session_state['df'].columns.get_loc('index') if 'index' in st.session_state['df'].columns else 0
                    )
                    
                    y_axis = st.selectbox(
                        "Y-Axis", 
                        options=st.session_state["df"].columns,
                        index=st.session_state['df'].columns.get_loc('score') if 'score' in st.session_state['df'].columns else 0
                    )
                
                with col2:
                    # Create visualizations based on selection
                    if viz_type == "Line Chart":
                        fig = px.line(st.session_state["df"], x=x_axis, y=y_axis, 
                                     title=f"{y_axis} vs {x_axis}")
                    elif viz_type == "Bar Chart":
                        fig = px.bar(st.session_state["df"], x=x_axis, y=y_axis,
                                    title=f"{y_axis} by {x_axis}")
                    elif viz_type == "Scatter Plot":
                        fig = px.scatter(st.session_state["df"], x=x_axis, y=y_axis,
                                        title=f"{y_axis} vs {x_axis}")
                    elif viz_type == "Histogram":
                        fig = px.histogram(st.session_state["df"], x=y_axis,
                                          title=f"Distribution of {y_axis}")
                    elif viz_type == "Box Plot":
                        fig = px.box(st.session_state["df"], y=y_axis,
                                    title=f"Box Plot of {y_axis}")
                    
                    fig.update_layout(
                        template="plotly_white",
                        height=500,
                        font=dict(family="Inter, sans-serif")
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 Please choose Score column in Advanced Options for Visualizations.")

        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📥 Export Data")
                if not st.session_state["df"].empty:
                    export_data()
                    
                    # Export as JSON
                    json_data = st.session_state["df"].to_json(orient='records', indent=2)
                    st.download_button(
                        label="📄 Download JSON",
                        data=json_data,
                        file_name=f"weaviate_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                else:
                    st.info("No data to export. Run a query first!")
            
            with col2:
                st.markdown("### 📋 Search History")
                if st.session_state["search_history"]:
                    for i, entry in enumerate(st.session_state["search_history"]):
                        with st.expander(f"🔍 {entry['query'][:30]}... ({entry['timestamp']})"):
                            st.write(f"**Class:** {entry['class']}")
                            st.write(f"**Results:** {entry['results']}")
                            st.write(f"**Response Time:** {entry['response_time']:.2f}s")
                            st.write(f"**Query:** {entry['query']}")
                else:
                    st.info("No search history yet. Run some queries!")

        with tab4:
            st.markdown("### 🔍 Data Insights")
            
            if not st.session_state["df"].empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Data Summary")
                    st.write(st.session_state["df"].describe())
                
                with col2:
                    st.markdown("#### 🏷️ Column Information")
                    info_data = []
                    for col in st.session_state["df"].columns:
                        info_data.append({
                            "Column": col,
                            "Type": str(st.session_state["df"][col].dtype),
                            "Non-Null": st.session_state["df"][col].count(),
                            "Unique": st.session_state["df"][col].nunique()
                        })
                    st.dataframe(pd.DataFrame(info_data), hide_index=True)
                
                # Score distribution if available
                if 'score' in st.session_state["df"].columns:
                    st.markdown("#### 📈 Score Distribution")
                    fig = px.histogram(st.session_state["df"], x='score', nbins=20,
                                      title="Distribution of Relevance Scores")
                    fig.update_layout(template="plotly_white", height=400)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("🔍 Run a query to see data insights!")

    else:
        # Welcome screen when no data
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <h2>🚀 Ready to Explore Your Data?</h2>
            <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
                Select a class from the sidebar and start your first search to see beautiful visualizations and insights.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick tips
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🎯 Getting Started**
            1. Select a Weaviate class
            2. Choose properties to retrieve
            3. Enter your search query
            4. Click "Execute Search"
            """)
        
        with col2:
            st.markdown("""
            **💡 Pro Tips**
            - Use Alpha to balance keyword vs vector search
            - Try different fusion types for better results
            - Export your data for further analysis
            """)
        
        with col3:
            st.markdown("""
            **📊 Features**
            - Interactive visualizations
            - Data export (CSV/JSON)
            - Search history tracking
            - Real-time insights
            """)
