import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import quote

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot Pro", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE MANAGEMENT ---
if 'history' not in st.session_state: st.session_state.history = []
if 'library' not in st.session_state: st.session_state.library = []
if 'reading_list' not in st.session_state: st.session_state.reading_list = []
if 'active_query' not in st.session_state: st.session_state.active_query = ""

# --- 3. DARK MODE & UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .res-card {
        background-color: #1a1c24;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
    .res-title { color: #58a6ff; font-weight: 600; font-size: 16px; margin-bottom: 5px; }
    .res-desc { color: #c9d1d9; font-size: 14px; margin-bottom: 10px; }
    div.stButton > button {
        background-color: #21262d;
        border: 1px solid #30363d;
        color: white;
        padding: 5px 10px;
        width: 100%;
        text-align: left;
    }
    div.stButton > button:hover { border-color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (RESEARCH HUB) ---
with st.sidebar:
    st.title("🛰️ Research Hub")
    hub_tabs = st.tabs(["📜 History", "⭐ Starred", "📚 Reading"])
    
    with hub_tabs[0]:
        if not st.session_state.history:
            st.caption("No history.")
        for h in reversed(st.session_state.history[-15:]):
            if st.button(f"🔍 {h}", key=f"hbtn_{h}"):
                st.session_state.active_query = h
                st.rerun()
    
    with hub_tabs[1]:
        for item in st.session_state.library:
            st.markdown(f'<div style="font-size:12px; margin-bottom:8px;">⭐ {item["title"][:40]}...<br><a href="{item["link"]}" target="_blank">Open ↗</a></div>', unsafe_allow_html=True)

    with hub_tabs[2]:
        for idx, paper in enumerate(st.session_state.reading_list):
            st.caption(f"📚 {paper['title'][:40]}...")
            if st.button("✅ Mark as Read", key=f"read_fin_{idx}"):
                st.session_state.reading_list.pop(idx)
                st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🛰️ Research-Pilot Pro")

query = st.text_input(
    "Global Search", 
    value=st.session_state.active_query, 
    placeholder="Type and press Enter...",
    key="search_bar_widget"
)

# Sync input with state
if query != st.session_state.active_query:
    st.session_state.active_query = query
    st.rerun()

depth = st.select_slider("Scan Depth", options=[3, 5, 10, 15], value=5)

# --- 6. SEARCH ENGINE (ALL TABS) ---
if st.session_state.active_query:
    search_term = st.session_state.active_query
    if search_term not in st.session_state.history:
        st.session_state.history.append(search_term)

    with st.spinner(f'Searching for "{search_term}"...'):
        tab_web, tab_gh, tab_ar = st.tabs(["🌐 Web Index", "🐙 GitHub Code", "📄 Academic (ArXiv)"])

        # --- WEB INDEX TAB ---
        with tab_web:
            # Note: For real Google results, you'd usually use Google Custom Search API.
            # Here we provide the Direct Intel Hub.
            st.info("Direct External Intelligence Hub:")
            google_search_url = f"https://www.google.com/search?q={quote(search_term)}"
            bing_search_url = f"https://www.bing.com/search?q={quote(search_term)}"
            
            st.markdown(f"""
                <div class="res-card">
                    <div class="res-title">Launch Live Web Scan</div>
                    <div class="res-desc">Scans global web indices for real-time news and articles related to "{search_term}".</div>
                    <a href="{google_search_url}" target="_blank" style="color:#58a6ff; margin-right:20px;">Open on Google ↗</a>
                    <a href="{bing_search_url}" target="_blank" style="color:#58a6ff;">Open on Bing ↗</a>
                </div>
            """, unsafe_allow_html=True)

        # --- GITHUB TAB (REAL API SEARCH) ---
        with tab_gh:
            gh_api_url = f"https://api.github.com/search/repositories?q={quote(search_term)}&sort=stars"
            try:
                gh_res = requests.get(gh_api_url, timeout=10).json()
                for item in gh_res.get('items', [])[:depth]:
                    st.markdown(f"""
                        <div class="res-card">
                            <div class="res-title">{item['full_name']}</div>
                            <div class="res-desc">{item['description'] or 'No description provided.'}</div>
                            <span style="color:#3fb950; font-size:12px;">⭐ {item['stargazers_count']:,} | 🛠️ {item['language']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3, _ = st.columns([0.1, 0.1, 0.1, 0.7])
                    with c1: st.link_button("👁️", item['html_url'], help="View Code")
                    with c2: 
                        if st.button("📚", key=f"r_gh_{item['id']}"):
                            st.session_state.reading_list.append({"title": item['full_name'], "link": item['html_url']})
                            st.toast("Added to Reading List")
                    with c3:
                        if st.button("⭐", key=f"s_gh_{item['id']}"):
                            st.session_state.library.append({"title": item['full_name'], "link": item['html_url']})
                            st.toast("Starred")
            except: st.error("GitHub API is currently unreachable.")

        # --- ACADEMIC TAB (REAL API SEARCH) ---
        with tab_ar:
            ar_api_url = f"http://export.arxiv.org/api/query?search_query=all:{quote(search_term)}&max_results={depth}"
            try:
                ar_res = requests.get(ar_api_url, timeout=10).text
                root = ET.fromstring(ar_res)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                    link = entry.find('{http://www.w3.org/2005/Atom}id').text
                    
                    st.markdown(f'<div class="res-card"><div class="res-title">{title}</div></div>', unsafe_allow_html=True)
                    
                    c1, c2, c3, _ = st.columns([0.1, 0.1, 0.1, 0.7])
                    with c1: st.link_button("👁️", link)
                    with c2:
                        if st.button("📚", key=f"r_ar_{link}"):
                            st.session_state.reading_list.append({"title": title, "link": link})
                            st.toast("Added to Reading List")
                    with c3:
                        if st.button("⭐", key=f"s_ar_{link}"):
                            st.session_state.library.append({"title": title, "link": link})
                            st.toast("Starred")
            except: st.error("Academic database connection error.")

    st.balloons()
