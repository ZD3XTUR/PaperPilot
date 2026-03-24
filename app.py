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

# CALLBACK for History Search
def trigger_history_search(query_from_button):
    st.session_state["search_bar_widget"] = query_from_button

# --- 3. UI STYLING (Minimalist & Clean) ---
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
    
    /* Sidebar Item Box */
    .side-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0d1117;
        padding: 5px 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        border: 1px solid #30363d;
    }
    .side-text { font-size: 12px; color: #c9d1d9; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 140px; }
    
    /* Hide Tab Labels (Make them icons only) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 20px; }
    
    /* Sidebar Buttons */
    div.stButton > button {
        background-color: transparent;
        border: none;
        color: #8b949e;
        padding: 0px;
    }
    div.stButton > button:hover { color: #ff7b72; border: none; background: transparent; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (ICON-ONLY NAVIGATION) ---
with st.sidebar:
    st.title("🛰️ Hub")
    
    # Tabs with Icons Only: 📜 (History), ⭐ (Starred), 📚 (Reading)
    hub_tabs = st.tabs(["📜", "⭐", "📚"])
    
    with hub_tabs[0]: # HISTORY
        col_h, col_del = st.columns([0.8, 0.2])
        with col_h: st.write("History")
        with col_del: 
            if st.button("🗑️", key="del_all_hist", help="Clear All History"):
                st.session_state.history = []
                st.rerun()
        
        for h in reversed(st.session_state.history[-15:]):
            st.button(f"🔍 {h}", key=f"btn_{h}", on_click=trigger_history_search, args=(h,))

    with hub_tabs[1]: # STARRED (Library)
        st.write("Library")
        for idx, item in enumerate(st.session_state.library):
            # Container for the starred item and the "remove" button
            c_text, c_remove = st.columns([0.8, 0.2])
            with c_text:
                st.markdown(f'<div class="side-text"><a href="{item["link"]}" target="_blank" style="color:#58a6ff; text-decoration:none;">{item["title"]}</a></div>', unsafe_allow_html=True)
            with c_remove:
                if st.button("✖️", key=f"rem_star_{idx}", help="Remove from Library"):
                    st.session_state.library.pop(idx)
                    st.rerun()

    with hub_tabs[2]: # READING LIST
        st.write("Reading")
        for idx, paper in enumerate(st.session_state.reading_list):
            c_text, c_check = st.columns([0.8, 0.2])
            with c_text:
                st.markdown(f'<div class="side-text">{paper["title"]}</div>', unsafe_allow_html=True)
            with c_check:
                if st.button("✔️", key=f"chk_read_{idx}", help="Mark as Read"):
                    st.session_state.reading_list.pop(idx)
                    st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🛰️ Research-Pilot Pro")

query = st.text_input(
    "Global Search", 
    placeholder="Type keywords...",
    key="search_bar_widget" 
)

depth = st.select_slider("Scan Depth", options=[3, 5, 10, 15], value=5)

# --- 6. SEARCH ENGINE ---
if query:
    if query not in st.session_state.history:
        st.session_state.history.append(query)

    with st.spinner(f'Searching...'):
        t_web, t_gh, t_ar = st.tabs(["🌐 Web", "🐙 Code", "📄 Paper"])

        # WEB
        with t_web:
            url = f"https://www.google.com/search?q={quote(query)}"
            st.markdown(f'<div class="res-card"><div class="res-title">Web Scan: {query}</div><a href="{url}" target="_blank" style="color:#58a6ff;">Launch ↗</a></div>', unsafe_allow_html=True)

        # GITHUB
        with t_gh:
            try:
                gh_res = requests.get(f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars", timeout=10).json()
                for item in gh_res.get('items', [])[:depth]:
                    st.markdown(f'<div class="res-card"><div class="res-title">{item["full_name"]}</div></div>', unsafe_allow_html=True)
                    c1, c2, c3, _ = st.columns([0.1, 0.1, 0.1, 0.7])
                    with c1: st.link_button("👁️", item['html_url'])
                    with c2: 
                        if st.button("📚", key=f"r_gh_{item['id']}"):
                            st.session_state.reading_list.append({"title": item['full_name'], "link": item['html_url']})
                    with c3:
                        if st.button("⭐", key=f"s_gh_{item['id']}"):
                            st.session_state.library.append({"title": item['full_name'], "link": item['html_url']})
            except: st.error("GitHub Error")

        # ARXIV
        with t_ar:
            try:
                ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(query)}&max_results={depth}", timeout=10).text
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
                    with c3:
                        if st.button("⭐", key=f"s_ar_{link}"):
                            st.session_state.library.append({"title": title, "link": link})
            except: st.error("Paper Error")
