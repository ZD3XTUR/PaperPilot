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
    st.session_state.library = [] # Yıldızlanan sonuçlar burada tutulacak
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
    }
    .res-title { color: #58a6ff; font-weight: 600; font-size: 18px; }
    .lib-item {
        padding: 10px;
        border-left: 3px solid #3fb950;
        background: #0d1117;
        margin-bottom: 8px;
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (HISTORY & LIBRARY) ---
with st.sidebar:
    st.title("🛰️ Research Hub")
    
    # --- TABLI SIDEBAR ---
    side_tab1, side_tab2 = st.tabs(["📜 History", "⭐ Library"])
    
    with side_tab1:
        if not st.session_state.history:
            st.caption("No recent searches.")
        for h_query in reversed(st.session_state.history[-10:]):
            if st.button(f"🔍 {h_query}", key=f"hist_{h_query}"):
                st.session_state.search_query = h_query
                st.rerun()

    with side_tab2:
        if not st.session_state.library:
            st.caption("Your library is empty. Star some results!")
        else:
            for idx, item in enumerate(st.session_state.library):
                st.markdown(f"""
                    <div class="lib-item">
                        <b>{item['title'][:40]}...</b><br>
                        <a href="{item['link']}" target="_blank" style="color:#58a6ff; font-size:11px;">Open Link ↗</a>
                    </div>
                """, unsafe_allow_html=True)
            if st.button("🗑️ Clear Library"):
                st.session_state.library = []
                st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🛰️ Research-Pilot Pro")
query = st.text_input("Search Topic", value=st.session_state.search_query, placeholder="Enter topic...", key="main_search")

result_count = st.select_slider("**Depth of Search**", options=[3, 5, 10, 15], value=5)

# --- 6. SEARCH LOGIC ---
if query:
    if query not in st.session_state.history:
        st.session_state.history.append(query)
    st.session_state.search_query = query

    with st.spinner('Scanning databases...'):
        tab1, tab2, tab3 = st.tabs(["🌐 Web", "🐙 GitHub", "📄 ArXiv"])

        # --- GITHUB SECTION (Örnek Kaydetme Mantığı) ---
        with tab2:
            gh_url = f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars"
            try:
                gh_res = requests.get(gh_url, timeout=10).json()
                for item in gh_res.get('items', [])[:result_count]:
                    st.markdown(f"""
                        <div class="res-card">
                            <div class="res-title">{item['full_name']}</div>
                            <p style="color:#c9d1d9; font-size:14px;">{item['description'] or 'No logs.'}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # KAYDETME BUTONU
                    if st.button(f"⭐ Star {item['full_name']}", key=f"save_{item['id']}"):
                        new_fav = {"title": item['full_name'], "link": item['html_url']}
                        if new_fav not in st.session_state.library:
                            st.session_state.library.append(new_fav)
                            st.toast(f"Saved to Library: {item['full_name']}")
            except: st.error("GitHub error.")

        # --- ARXIV SECTION ---
        with tab3:
            ar_url = f"http://export.arxiv.org/api/query?search_query=all:{quote(query)}&max_results={result_count}"
            try:
                ar_res = requests.get(ar_url, timeout=10).text
                root = ET.fromstring(ar_res)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                    link = entry.find('{http://www.w3.org/2005/Atom}id').text
                    
                    st.markdown(f"""
                        <div class="res-card">
                            <div class="res-title">{title[:100]}...</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"⭐ Star Paper", key=f"save_{link}"):
                        new_fav = {"title": title, "link": link}
                        if new_fav not in st.session_state.library:
                            st.session_state.library.append(new_fav)
                            st.toast("Academic paper saved!")
            except: st.error("ArXiv error.")

    st.balloons()
