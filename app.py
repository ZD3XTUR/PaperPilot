import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import quote

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot Dark", page_icon="🚀", layout="wide")

# --- 2. DARK MODE UI STYLING (CSS) ---
st.markdown("""
    <style>
    /* Dark Background and Text Colors */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Modern Dark Card Style */
    .res-card {
        background-color: #1a1c24;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .res-card:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
        box-shadow: 0 8px 24px rgba(88,166,255,0.1);
    }
    .res-source {
        font-size: 11px;
        letter-spacing: 1px;
        font-weight: 800;
        color: #8b949e;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    .res-title {
        font-size: 20px;
        font-weight: 600;
        color: #58a6ff;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    .res-desc {
        font-size: 14px;
        color: #c9d1d9;
        margin-bottom: 15px;
        line-height: 1.6;
    }
    .res-meta {
        font-size: 13px;
        color: #3fb950; /* Success Green for stats */
        font-weight: 600;
    }
    .res-link {
        text-decoration: none;
        color: #1f6feb;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    .res-link:hover {
        text-decoration: underline;
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        background-color: #0d1117;
        color: white;
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("# 🛰️ Mission Control")
    st.write("Adjust your scanning parameters.")
    result_count = st.select_slider("Depth of Search:", options=[3, 5, 10, 15], value=5)
    st.divider()
    st.success("System: Online")
    st.caption("v2.1 Dark Mode | 2026 Edition")

# --- 4. MAIN HEADER ---
st.title("🛰️ Research-Pilot: Dark Matter")
st.markdown("Unified Intelligence Dashboard for the Modern Researcher.")

# --- 5. SEARCH LOGIC ---
query = st.text_input("", placeholder="Search the galaxy of information...")

if query:
    encoded_query = quote(query)
    all_results = []

    with st.spinner('🚀 Navigating through data...'):
        tab1, tab2, tab3 = st.tabs(["🌐 Web Explorer", "🐙 GitHub Repos", "📄 Academic Papers"])

        # --- TAB 1: GOOGLE ---
        with tab1:
            st.markdown("### 🌐 Web Intelligence")
            google_url = f"https://www.google.com/search?q={encoded_query}"
            st.markdown(f"""
                <div class="res-card">
                    <div class="res-source">Manual Search Required</div>
                    <div class="res-title">Google Web Index for: {query}</div>
                    <div class="res-desc">Our sensors indicate more data is available on the main Google hub.</div>
                    <a href="{google_url}" target="_blank" class="res-link">Open External Link ↗</a>
                </div>
                """, unsafe_allow_html=True)

        # --- TAB 2: GITHUB ---
        with tab2:
            st.markdown("### 🐙 Code Repositories")
            gh_url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars"
            try:
                gh_res = requests.get(gh_url, timeout=10).json()
                for item in gh_res.get('items', [])[:result_count]:
                    all_results.append({"Source": "GitHub", "Title": item['full_name'], "Link": item['html_url']})
                    st.markdown(f"""
                        <div class="res-card">
                            <div class="res-source">GitHub Archive</div>
                            <div class="res-title">{item['full_name']}</div>
                            <div class="res-desc">{item['description'][:180] if item['description'] else 'No transmission received.'}...</div>
                            <div class="res-meta">⭐ {item['stargazers_count']:,} Stars | 🛠️ {item['language']}</div>
                            <a href="{item['html_url']}" target="_blank" class="res-link">Explore Code ↗</a>
                        </div>
                        """, unsafe_allow_html=True)
            except: st.error("Link to GitHub lost.")

        # --- TAB 3: ARXIV ---
        with tab3:
            st.markdown("### 📄 Research Papers")
            ar_url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&max_results={result_count}"
            try:
                ar_res = requests.get(ar_url, timeout=10).text
                root = ET.fromstring(ar_res)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns).text.strip().replace('\n', '')
                    link = entry.find('atom:id', ns).text
                    summary = entry.find('atom:summary', ns).text[:220].strip()
                    all_results.append({"Source": "ArXiv", "Title": title, "Link": link})
                    st.markdown(f"""
                        <div class="res-card">
                            <div class="res-source">ArXiv Database</div>
                            <div class="res-title">{title}</div>
                            <div class="res-desc">{summary}...</div>
                            <a href="{link}" target="_blank" class="res-link">Read Publication ↗</a>
                        </div>
                        """, unsafe_allow_html=True)
            except: st.error("ArXiv transmission interrupted.")

    # --- 6. EXPORT ---
    if all_results:
        st.divider()
        csv = pd.DataFrame(all_results).to_csv(index=False).encode('utf-8')
        st.download_button("📥 Extract Data (CSV)", csv, "intel_report.csv", "text/csv")
    
    st.balloons()
