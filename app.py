import streamlit as st
from pages import connection, home

# Configure page settings
st.set_page_config(
    page_title="Weaviate Utility",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Custom CSS for beautiful styling with eye-friendly colors
# Custom CSS for beautiful styling with dark grey and black theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1f1f1f 100%);
        background-attachment: fixed;
        color: #e0e0e0;
    }
    
    /* Main container styling */
    .main-container {
        background: rgba(45, 45, 45, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        border: 1px solid #333333;
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        color: #ffffff;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
        color: #cccccc;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%);
    }
    
    .sidebar-content {
        background: rgba(45, 45, 45, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        border: 1px solid #404040;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #2d2d2d 0%, #404040 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        margin: 0.5rem 0;
        border: 1px solid #555555;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #cccccc;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #404040 0%, #2d2d2d 100%);
        color: white;
        border: 1px solid #555555;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #555555 0%, #404040 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        border-color: #666666;
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > div {
        background-color: #2d2d2d !important;
        color: #e0e0e0 !important;
        border-radius: 10px;
        border: 2px solid #555555;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #777777;
        box-shadow: 0 0 0 3px rgba(119, 119, 119, 0.2);
        background-color: #333333 !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        color: #e0e0e0;
        border-radius: 10px 10px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
        border: 1px solid #404040;
        border-bottom: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #404040 0%, #2d2d2d 100%);
        color: #ffffff;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        color: #ffffff;
        border-color: #555555;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: linear-gradient(135deg, #2d2d2d 0%, #404040 100%);
        border: 1px solid #4CAF50;
        border-radius: 10px;
        padding: 1rem;
        color: #4CAF50;
    }
    
    .stError {
        background: linear-gradient(135deg, #2d2d2d 0%, #404040 100%);
        border: 1px solid #f44336;
        border-radius: 10px;
        padding: 1rem;
        color: #f44336;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #2d2d2d 0%, #404040 100%);
        border: 1px solid #2196F3;
        border-radius: 10px;
        padding: 1rem;
        color: #2196F3;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .loading-spinner {
        border: 4px solid #404040;
        border-top: 4px solid #cccccc;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #555555 0%, #777777 100%);
    }
    
    /* Slider styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #555555 0%, #777777 100%);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #2d2d2d 0%, #404040 100%);
        border: 1px solid #555555;
        border-radius: 10px;
        font-weight: 600;
        color: #e0e0e0;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: #2d2d2d;
        border: 1px solid #555555;
        border-radius: 10px;
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div > div {
        background-color: #2d2d2d !important;
        border-color: #555555 !important;
    }
    
    /* Checkbox styling */
    .stCheckbox > label > div {
        background-color: #2d2d2d;
        border-color: #555555;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background-color: #2d2d2d !important;
        color: #e0e0e0 !important;
        border: 2px solid #555555;
        border-radius: 10px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #777777;
        box-shadow: 0 0 0 3px rgba(119, 119, 119, 0.2);
    }
    
    /* Number input styling */
    .stNumberInput > div > div > input {
        background-color: #2d2d2d !important;
        color: #e0e0e0 !important;
        border: 2px solid #555555;
        border-radius: 10px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #555555 0%, #777777 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #777777 0%, #999999 100%);
    }
    
    /* General text color */
    .stMarkdown, .stText {
        color: #e0e0e0;
    }
    
    /* Label styling */
    label {
        color: #cccccc !important;
    }
</style>
""", unsafe_allow_html=True)
# Main app logic to handle page navigation
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if st.session_state['authenticated']:
    home()  # If authenticated, go to home page
else:
    connection()  # If not authenticated, stay on connection page
