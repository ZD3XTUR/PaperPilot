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
        padding: 2px 10px;
        width: 100%;
        text-align: left;
    }
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
            # FIXED: Manually updating the widget's state via its KEY
            if st.button(f"🔍 {h}", key=f"hbtn_{h}"):
                st.session_state["search_input_main"] = h # Force the text input to show this
                st.rerun()

    with hub_tabs[1]: # STARRED
        for item in st.session_state.library:
            st.caption(f"⭐ {item['title'][:40]}...")
            st.write(f"[Open ↗]({item['link']})")

    with hub_tabs[2]: # READING LIST
        for idx, paper in enumerate(st.session_state.reading_list):
            st.caption(f"📚 {paper['title'][:40]}...")
            if st.button("✅ Mark as Read", key=f"read_fin_{idx}"):
                st.session_state.reading_list.pop(idx)
                st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🛰️ Research-Pilot Pro")

# FIXED: We use 'key' to sync the input box with session_state directly
query = st.text_input(
    "Global Search", 
    placeholder="Enter keywords...",
    key="search_input_main" # This key is now the source of truth
)

depth = st.select_slider("Scan Depth", options=[3, 5, 10, 15], value=5)

# --- 6. SEARCH LOGIC ---
if query:
    if query not in st.session_state.history:
        st.session_state.history.append(query)

    with st.spinner(f'Scanning global networks for "{query}"...'):
        t1, t2, t3 = st.tabs(["🌐 Web Index", "🐙 GitHub Code", "📄 Academic (ArXiv)"])

        # TAB: ACADEMIC (ARXIV)
        with t3:
            ar_url = f"http://export.arxiv.org/api/query?search_query=all:{quote(query)}&max_results={depth}"
            try:
                root = ET.fromstring(requests.get(ar_url, timeout=10).text)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                    l = entry.find('{http://www.w3.org/2005/Atom}id').text
                    
                    st.markdown(f'<div class="res-card"><div class="res-title">{t[:110]}...</div></div>', unsafe_allow_html=True)
                    
                    c1, c2, c3, c_sp = st.columns([0.1, 0.1, 0.1, 0.7])
                    with c1: st.link_button("👁️", l, help="Read Paper")
                    with c2:
                        if st.button("📚", key=f"r_ar_{l}", help="Reading List"):
                            st.session_state.reading_list.append({"title": t, "link": l})
                            st.toast("Added to Reading List")
                    with c3:
                        if st.button("⭐", key=f"s_ar_{l}", help="Star"):
                            st.session_state.library.append({"title": t, "link": l})
                            st.toast("Starred")
            except: st.error("Database error.")

    st.balloons()
