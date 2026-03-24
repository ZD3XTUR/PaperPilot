import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import quote

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot Pro", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE (Hafıza Yönetimi) ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

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
    .res-card:hover { border-color: #58a6ff; }
    .res-title { color: #58a6ff; font-weight: 600; font-size: 18px; }
    
    /* Sidebar Button Styling */
    .stButton>button {
        width: 100%;
        text-align: left;
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
        font-size: 13px;
        margin-bottom: 2px;
    }
    .stButton>button:hover {
        border-color: #58a6ff;
        color: #58a6ff;
    }
    .lib-card {
        padding: 10px;
        background: #0d1117;
        border-left: 3px solid #3fb950;
        margin-bottom: 10px;
        border-radius: 0 5px 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (RESEARCH HUB - ACILIR KAPANIR) ---
with st.sidebar:
    st.title("🛰️ Research Hub")
    st.caption("Manage your intelligence data")
    
    # HUB İÇİNDE SEKMELER
    hub_tab1, hub_tab2 = st.tabs(["📜 History", "⭐ Library"])
    
    with hub_tab1:
        st.write("Click to re-scan:")
        if not st.session_state.history:
            st.caption("No history yet.")
        else:
            # GEÇMİŞE TIKLANDIĞINDA OTOMATİK ARAMA
            for h_query in reversed(st.session_state.history[-15:]):
                if st.button(f"🔍 {h_query}", key=f"h_{h_query}"):
                    st.session_state.search_query = h_query
                    st.rerun()
            
            if st.button("🗑️ Clear History", key="clear_h"):
                st.session_state.history = []
                st.session_state.search_query = ""
                st.rerun()

    with hub_tab2:
        st.write("Saved Intel:")
        if not st.session_state.library:
            st.caption("Star results to save them here.")
        else:
            for idx, item in enumerate(st.session_state.library):
                st.markdown(f"""
                    <div class="lib-card">
                        <div style="font-weight:bold; color:#f0f6fc; font-size:12px;">{item['title'][:50]}...</div>
                        <a href="{item['link']}" target="_blank" style="color:#58a6ff; font-size:11px; text-decoration:none;">Open Resource ↗</a>
                    </div>
                """, unsafe_allow_html=True)
            
            if st.button("🗑️ Empty Library", key="clear_l"):
                st.session_state.library = []
                st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🛰️ Research-Pilot Pro")

# Arama Çubuğu (Value session_state'den besleniyor)
query = st.text_input(
    "Global Search", 
    value=st.session_state.search_query, 
    placeholder="What are we analyzing today?",
    key="main_input"
)

# Depth Slider
result_count = st.select_slider("**Scan Depth**", options=[3, 5, 10, 15, 20], value=5)

# --- 6. SEARCH LOGIC ---
if query:
    # Geçmişe Ekleme
    if query not in st.session_state.history:
        st.session_state.history.append(query)
    st.session_state.search_query = query # Mevcut aramayı sabitle

    with st.spinner(f'🛸 Scanning for "{query}"...'):
        tab1, tab2, tab3 = st.tabs(["🌐 Web Index", "🐙 GitHub Code", "📄 ArXiv Papers"])

        # --- GITHUB TAB ---
        with tab2:
            gh_url = f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars"
            try:
                items = requests.get(gh_url, timeout=10).json().get('items', [])
                for item in items[:result_count]:
                    st.markdown(f"""
                        <div class="res-card">
                            <div style="font-size:12px; color:#8b949e;">GITHUB REPOSITORY</div>
                            <div class="res-title">{item['full_name']}</div>
                            <p style="color:#c9d1d9; font-size:14px; margin:10px 0;">{item['description'][:160] if item['description'] else 'No logs.'}...</p>
                            <span style="color:#3fb950; font-size:12px; font-weight:bold;">⭐ {item['stargazers_count']:,} | 🛠️ {item['language']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col_link, col_save = st.columns([0.2, 0.8])
                    with col_link:
                        st.link_button("View ↗", item['html_url'])
                    with col_save:
                        if st.button(f"⭐ Save to Library", key=f"s_gh_{item['id']}"):
                            fav = {"title": item['full_name'], "link": item['html_url']}
                            if fav not in st.session_state.library:
                                st.session_state.library.append(fav)
                                st.toast("Added to Library!")

            except: st.error("Link lost.")

        # --- ARXIV TAB ---
        with tab3:
            ar_url = f"http://export.arxiv.org/api/query?search_query=all:{quote(query)}&max_results={result_count}"
            try:
                response = requests.get(ar_url, timeout=10).text
                root = ET.fromstring(response)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                    l = entry.find('{http://www.w3.org/2005/Atom}id').text
                    
                    st.markdown(f"""<div class="res-card"><div class="res-title">{t[:100]}...</div></div>""", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([0.2, 0.8])
                    with c1: st.link_button("Read ↗", l)
                    with c2:
                        if st.button(f"⭐ Save Paper", key=f"s_ar_{l}"):
                            fav = {"title": t, "link": l}
                            if fav not in st.session_state.library:
                                st.session_state.library.append(fav)
                                st.toast("Paper saved!")
            except: st.error("Database offline.")

    st.balloons()
