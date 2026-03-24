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

# --- CALLBACK FUNCTION ---
# This function runs BEFORE the rest of the app when a history button is clicked
def load_search(query_text):
    st.session_state["search_input_main"] = query_text

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
    div.stButton > button:hover {
        border-color: #58a6ff;
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
            # FIXED: Using on_click callback to update state safely
            st.button(f"🔍 {h}", key=f"hbtn_{h}", on_click=load_search, args=(h,))

    with hub_tabs[1]: # STARRED
        for item in st.session_state.library:
            st.markdown(f'<div style="font-size:12px; margin-bottom:5px;">⭐ {item["title"][:40]}... <br> <a href="{item["link"]}" target="_blank">Open ↗</a></div>', unsafe_allow_html=True)

    with hub_tabs[2]: # READING LIST
        for idx, paper in enumerate(st.session_state.reading_list):
            st.caption(f"📚 {paper['title'][:40]}...")
            if st.button("✅ Done", key=f"read_fin_{idx}"):
                st.session_state.reading_list.pop(idx)
                st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🛰️ Research-Pilot Pro")

# SOURCE OF TRUTH: The search input uses the 'search_input_main' key
query = st.text_input(
    "Global Search", 
    placeholder="Enter keywords...",
    key="search_input_main" 
)

depth = st.select_slider("Scan Depth", options=[3, 5, 10, 15], value=5)

# --- 6. SEARCH LOGIC ---
if query:
    # Add to history if not duplicate
    if query not in st.session_state.history:
        st.session_state.history.append(query)

    with st.spinner(f'Scanning global networks for "{query}"...'):
        t1, t2, t3 = st.tabs(["🌐 Web Index", "🐙 GitHub Code", "📄 Academic (ArXiv)"])

        # TAB: ACADEMIC (ARXIV)
        with t3:
            ar_url = f"http://export.arxiv.org/api/query?search_query=all:{quote(query)}&max_results={depth}"
            try:
                response = requests.get(ar_url, timeout=10).text
                root = ET.fromstring(response)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                    l = entry.find('{http://www.w3.org/2005/Atom}id').text
                    
                    st.markdown(f'<div class="res-card"><div class="res-title">{t[:110]}...</div></div>', unsafe_allow_html=True)
                    
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
            except: st.error("Search failed. Check your connection.")

    st.balloons()
