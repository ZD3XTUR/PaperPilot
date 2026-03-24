import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import quote

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot Pro", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE (Arama Geçmişi İçin) ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. DARK MODE & UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .res-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .res-card:hover { border-color: #58a6ff; background-color: #21262d; }
    .res-title { color: #58a6ff; font-weight: 600; font-size: 18px; margin-bottom: 8px; }
    .history-item { 
        padding: 8px; 
        border-radius: 5px; 
        background: #21262d; 
        margin-bottom: 5px; 
        font-size: 14px;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (SEARCH HISTORY) ---
with st.sidebar:
    st.title("📜 Search History")
    if not st.session_state.history:
        st.write("No recent searches.")
    else:
        for h_query in reversed(st.session_state.history[-10:]): # Son 10 aramayı göster
            st.markdown(f'<div class="history-item">🔍 {h_query}</div>', unsafe_allow_html=True)
    
    st.divider()
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🛰️ Research-Pilot Pro")
st.caption("Unified Dark Matter Intelligence Engine")

# Arama Çubuğu
query = st.text_input("", placeholder="Enter your research topic...", key="main_search")

# --- DEPTH OF SEARCH (Arama Çubuğu Altına Entegre) ---
col_slider, col_info = st.columns([0.7, 0.3])
with col_slider:
    result_count = st.select_slider(
        "**Depth of Search (Results per source)**", 
        options=[3, 5, 10, 15, 20], 
        value=5,
        help="Higher depth increases scanning time but provides more data."
    )
with col_info:
    st.write(f"📡 Status: **Ready to Scan**")

# --- 6. SEARCH LOGIC ---
if query:
    # Arama geçmişine ekle (Eğer zaten yoksa)
    if query not in st.session_state.history:
        st.session_state.history.append(query)

    encoded_query = quote(query)
    all_results = []

    with st.spinner(f'🛰️ Orbiting around "{query}"...'):
        tab1, tab2, tab3 = st.tabs(["🌐 Web Index", "🐙 GitHub Code", "📄 ArXiv Papers"])

        # --- TAB 1: GOOGLE ---
        with tab1:
            google_url = f"https://www.google.com/search?q={encoded_query}"
            st.markdown(f"""
                <div class="res-card">
                    <div class="res-title">External Intelligence: {query}</div>
                    <p style="color:#8b949e;">Deep web scanning requires manual verification via Google's hub.</p>
                    <a href="{google_url}" target="_blank" style="color:#58a6ff; text-decoration:none; font-weight:bold;">Launch External Scan ↗</a>
                </div>
                """, unsafe_allow_html=True)

        # --- TAB 2: GITHUB ---
        with tab2:
            gh_url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars"
            try:
                gh_res = requests.get(gh_url, timeout=10).json()
                for item in gh_res.get('items', [])[:result_count]:
                    all_results.append({"Source": "GitHub", "Title": item['full_name'], "Link": item['html_url']})
                    st.markdown(f"""
                        <div class="res-card">
                            <div class="res-title">{item['full_name']}</div>
                            <p style="color:#c9d1d9; font-size:14px;">{item['description'][:150] if item['description'] else 'No logs available.'}...</p>
                            <span style="color:#3fb950; font-size:12px;">⭐ {item['stargazers_count']:,} | 🛠️ {item['language']}</span><br>
                            <a href="{item['html_url']}" target="_blank" style="color:#1f6feb; text-decoration:none; font-size:13px;">Open Source Code ↗</a>
                        </div>
                        """, unsafe_allow_html=True)
            except: st.error("GitHub connection timed out.")

        # --- TAB 3: ARXIV ---
        with tab3:
            ar_url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&max_results={result_count}"
            try:
                ar_res = requests.get(ar_url, timeout=10).text
                root = ET.fromstring(ar_res)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns).text.strip().replace('\n', '')
                    link = entry.find('atom:id', ns).text
                    all_results.append({"Source": "ArXiv", "Title": title, "Link": link})
                    st.markdown(f"""
                        <div class="res-card">
                            <div class="res-title">{title}</div>
                            <p style="color:#c9d1d9; font-size:14px;">{entry.find('atom:summary', ns).text[:200].strip()}...</p>
                            <a href="{link}" target="_blank" style="color:#1f6feb; text-decoration:none; font-size:13px;">Read Full Paper ↗</a>
                        </div>
                        """, unsafe_allow_html=True)
            except: st.error("Academic database unreachable.")

    # --- 7. EXPORT DATA ---
    if all_results:
        st.divider()
        csv = pd.DataFrame(all_results).to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Intel Report", csv, "report.csv", "text/csv")
    
    st.balloons()
