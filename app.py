import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot Pro", page_icon="🚀", layout="wide")

# --- CUSTOM CSS (Professional Branding) ---
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #f8f9fa;
    }
    /* Custom Card Style */
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .result-title {
        color: #1e1e1e;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .result-link {
        color: #007bff;
        text-decoration: none;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1085/1085810.png", width=80)
    st.title("Settings")
    result_count = st.slider("Results per source", min_value=3, max_value=20, value=5)
    st.divider()
    st.info("Tip: Use English keywords for better results in GitHub and ArXiv.")

# --- UI HEADER ---
st.title("🚀 Research-Pilot Pro")
st.caption("The ultimate unified dashboard for developers and researchers.")

# --- SEARCH INPUT ---
query = st.text_input("", placeholder="Type your research topic here (e.g., Deep Learning)...")

if query:
    encoded_query = quote(query)
    
    with st.spinner('Scanning global databases...'):
        tab1, tab2, tab3 = st.tabs(["🌐 Web (Google)", "🐙 Code (GitHub)", "📄 Science (ArXiv)"])

        # --- GOOGLE TAB ---
        with tab1:
            st.markdown(f"### 🔍 Google Search Results")
            google_url = f"https://www.google.com/search?q={encoded_query}"
            
            st.markdown(f"""
                <div class="result-card">
                    <div class="result-title">External Web Search</div>
                    <p>Access millions of articles, news, and tutorials on Google.</p>
                    <a href="{google_url}" target="_blank" class="result-link">👉 Open Full Results in New Tab</a>
                </div>
                """, unsafe_allow_html=True)

        # --- GITHUB TAB ---
        with tab2:
            st.markdown(f"### 🐙 Top Open Source Projects")
            github_api_url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars"
            try:
                response = requests.get(github_api_url, timeout=10).json()
                items = response.get('items', [])
                if items:
                    for item in items[:result_count]:
                        st.markdown(f"""
                            <div class="result-card" style="border-left-color: #24292e;">
                                <div class="result-title">⭐ {item['stargazers_count']:,} | {item['full_name']}</div>
                                <p>{item['description'] if item['description'] else 'No description available.'}</p>
                                <a href="{item['html_url']}" target="_blank" class="result-link">📂 View Source Code</a>
                            </div>
                            """, unsafe_allow_html=True)
                else: st.warning("No repos found.")
            except: st.error("GitHub API error.")

        # --- ARXIV TAB ---
        with tab3:
            st.markdown(f"### 📄 Scientific Publications")
            arxiv_api_url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&max_results={result_count}"
            try:
                response = requests.get(arxiv_api_url, timeout=10).text
                root = ET.fromstring(response)
                entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                if entries:
                    for entry in entries:
                        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                        link = entry.find('{http://www.w3.org/2005/Atom}id').text
                        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text[:200] + "..."
                        st.markdown(f"""
                            <div class="result-card" style="border-left-color: #B31B1B;">
                                <div class="result-title">{title}</div>
                                <p style="font-size: 14px; color: #666;">{summary}</p>
                                <a href="{link}" target="_blank" class="result-link">📖 Read Full Paper</a>
                            </div>
                            """, unsafe_allow_html=True)
                else: st.warning("No papers found.")
            except: st.error("ArXiv API error.")

    st.balloons()
