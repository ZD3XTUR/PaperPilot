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

# This variable will hold our current active search term
if 'active_query' not in st.session_state:
    st.session_state.active_query = ""

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
    .res-title { color: #58a6ff; font-weight: 600; font-size: 16px; margin-bottom: 8px; }
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
    
    with hub_tabs[0]: # HISTORY
        st.write("Click to re-scan:")
        if not st.session_state.history:
            st.caption("No history available.")
        for h in reversed(st.session_state.history[-15:]):
            # FIXED: When clicked, update the state and rerun. Simple and effective.
            if st.button(f"🔍 {h}", key=f"hbtn_{h}"):
                st.session_state.active_query = h
                st.rerun()
        
        if st.session_state.history:
            if st.button("🗑️ Clear All"):
                st.session_state.history = []
                st.session_state.active_query = ""
                st.rerun()

    with hub_tabs[1]: # STARRED
        for item in st.session_state.library:
            st.markdown(f'<div style="font-size:12px; margin-bottom:8px;">⭐ {item["title"][:40]}...<br><a href="{item["link"]}" target="_blank">Open ↗</a></div>', unsafe_allow_html=True)

    with hub_tabs[2]: # READING LIST
        for idx, paper in enumerate(st.session_state.reading_list):
            st.caption(f"📚 {paper['title'][:40]}...")
            if st.button("✅ Mark as Read", key=f"read_fin_{idx}"):
                st.session_state.reading_list.pop(idx)
                st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🛰️ Research-Pilot Pro")

# THE FIX: We use 'value' to show the state, but 'query' captures the NEW input.
query = st.text_input(
    "Global Search", 
    value=st.session_state.active_query, 
    placeholder="Enter keywords and press Enter...",
    key="search_bar_widget"
)

# Update the state if the user types something new
if query != st.session_state.active_query:
    st.session_state.active_query = query
    st.rerun()

depth = st.select_slider("Scan Depth", options=[3, 5, 10, 15], value=5)

# --- 6. SEARCH LOGIC ---
if st.session_state.active_query:
    search_term = st.session_state.active_query
    
    # Save to history
    if search_term not in st.session_state.history:
        st.session_state.history.append(search_term)

    with st.spinner(f'Searching for "{search_term}"...'):
        t1, t2, t3 = st.tabs(["🌐 Web Index", "🐙 GitHub Code", "📄 Academic (ArXiv)"])

        with t3: # ACADEMIC
            ar_url = f"http://export.arxiv.org/api/query?search_query=all:{quote(search_term)}&max_results={depth}"
            try:
                root = ET.fromstring(requests.get(ar_url, timeout=10).text)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                    l = entry.find('{http://www.w3.org/2005/Atom}id').text
                    
                    st.markdown(f'<div class="res-card"><div class="res-title">{t[:120]}...</div></div>', unsafe_allow_html=True)
                    
                    # 👁️ Read | 📚 Reading List | ⭐ Star
                    c1, c2, c3, c_sp = st.columns([0.1, 0.1, 0.1, 0.7])
                    with c1: st.link_button("👁️", l, help="Open Paper")
                    with c2:
                        if st.button("📚", key=f"r_ar_{l}", help="Reading List"):
                            st.session_state.reading_list.append({"title": t, "link": l})
                            st.toast("Saved to Reading List")
                    with c3:
                        if st.button("⭐", key=f"s_ar_{l}", help="Star"):
                            st.session_state.library.append({"title": t, "link": l})
                            st.toast("Starred")
            except: st.error("Connection failed.")

    st.balloons()
