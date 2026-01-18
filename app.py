import streamlit as st
import tempfile
import json
import pandas as pd

from ml_matcher import (
    load_movie_dialogues,
    load_chat_dialogues,
    match_characters
)

st.set_page_config(
    page_title="WhatsApp Character Mapper",
    layout="centered"
)

# Custom CSS for dark creative theme
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 50%, #0a0a0a 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated background particles */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 20%, rgba(138, 43, 226, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(219, 39, 119, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%);
        pointer-events: none;
        animation: pulse 8s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.6; }
    }
    
    /* Title styling */
    h1 {
        background: linear-gradient(135deg, #a78bfa 0%, #ec4899 50%, #60a5fa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        font-size: 3.5rem !important;
        text-align: center;
        margin-bottom: 1rem !important;
        letter-spacing: -0.02em;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #94a3b8;
        font-size: 1.1rem;
        line-height: 1.8;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(100, 116, 139, 0.3);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: rgba(168, 85, 247, 0.5);
        background: rgba(30, 41, 59, 0.7);
        transform: translateY(-2px);
        box-shadow: 0 10px 40px rgba(168, 85, 247, 0.2);
    }
    
    .stFileUploader label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* Upload section */
    section[data-testid="stFileUploader"] > div {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(219, 39, 119, 0.1) 100%);
        border: 2px dashed rgba(168, 85, 247, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    section[data-testid="stFileUploader"] > div:hover {
        border-color: rgba(236, 72, 153, 0.5);
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(219, 39, 119, 0.15) 100%);
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.3);
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(236, 72, 153, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: rgba(30, 41, 59, 0.7);
        border: 2px solid rgba(100, 116, 139, 0.5);
        color: #e2e8f0;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.7);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }
    
    /* Success message */
    .stSuccess {
        background: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22c55e;
        border-radius: 8px;
        padding: 1rem;
        color: #86efac;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(100, 116, 139, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: rgba(168, 85, 247, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(168, 85, 247, 0.2);
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #a78bfa !important;
        font-weight: 900 !important;
        font-size: 2.5rem !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #8b5cf6 transparent #ec4899 transparent !important;
    }
    
    /* Subheader */
    h2, h3 {
        background: linear-gradient(135deg, #a78bfa 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        margin-top: 2rem !important;
    }
    
    /* DataFrame */
    .stDataFrame {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        overflow: hidden;
        border: 2px solid rgba(100, 116, 139, 0.3);
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: transparent !important;
    }
    
    /* Table styling */
    table {
        color: #e2e8f0 !important;
    }
    
    thead tr th {
        background: rgba(139, 92, 246, 0.2) !important;
        color: #a78bfa !important;
        font-weight: 700 !important;
        border-bottom: 2px solid rgba(168, 85, 247, 0.5) !important;
    }
    
    tbody tr {
        border-bottom: 1px solid rgba(100, 116, 139, 0.2) !important;
        transition: all 0.2s ease;
    }
    
    tbody tr:hover {
        background: rgba(139, 92, 246, 0.1) !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
    }
    
    /* Info badge */
    .stMarkdown p {
        position: relative;
        padding-left: 1rem;
    }
    
    /* Add glow effect to interactive elements */
    .stFileUploader:hover,
    .stButton > button:hover,
    [data-testid="stMetric"]:hover {
        animation: glow 2s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.3);
        }
        50% {
            box-shadow: 0 0 40px rgba(236, 72, 153, 0.5);
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("🎬 WhatsApp → Movie Character Mapper")

st.markdown("""
Upload:
• WhatsApp chat (.txt)  
• Movie dialogues (.txt)  

The app will automatically match WhatsApp users
to movie characters using AI.
""")

# Upload WhatsApp chat
chat_file = st.file_uploader(
    "Upload WhatsApp Chat (.txt)",
    type=["txt"]
)

# Upload movie dialogues
movie_file = st.file_uploader(
    "Upload Movie Dialogues (.txt)",
    type=["txt"]
)

if chat_file and movie_file:

    # Save uploaded files temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(chat_file.read())
        chat_path = f.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(movie_file.read())
        movie_path = f.name

    st.success("Files uploaded successfully")

    if st.button("🚀 Run Character Matching"):

        with st.spinner("Reading dialogues..."):
            chat_data = load_chat_dialogues(chat_path)
            movie_data = load_movie_dialogues(movie_path)

        st.metric("WhatsApp Users", len(chat_data))
        st.metric("Movie Characters", len(movie_data))

        with st.spinner("Running AI similarity matching..."):
            mapping = match_characters(chat_data, movie_data)

        st.success("Matching completed")

        df = pd.DataFrame(
            mapping.items(),
            columns=["Movie Character", "WhatsApp User"]
        )

        st.subheader("🎭 Final Result")
        st.dataframe(df)

        st.download_button(
            "⬇️ Download JSON",
            json.dumps(mapping, indent=2),
            file_name="character_mapping.json",
            mime="application/json"
        )

        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False),
            file_name="character_mapping.csv",
            mime="text/csv"
        )