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
if 'search_query' not in st.session_state: st.session_state.search_query = ""

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
    
    /* Minimalist Emoji Button Styling */
    div.stButton > button {
        background-color: #21262d;
        border: 1px solid #30363d;
        color: white;
        padding: 2px 10px;
    }
    div.stButton > button:hover {
        border-color: #58a6ff;
        color: #58a6ff;
    }
    .lib-box {
        padding: 8px;
        background: #0d1117;
        border-left: 3px solid #3fb950;
        margin-bottom: 8px;
        border-radius: 0 5px 5px 0;
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (RESEARCH HUB) ---
with st.sidebar:
    st.title("🛰️ Research Hub")
    st.caption("Intelligence Management System")
    
    hub_tabs = st.tabs(["📜 History", "⭐ Starred", "📚 Reading"])
    
    with hub_tabs[0]: # HISTORY
        st.write("Click to re-scan:")
        if not st.session_state.history:
            st.caption("No history available.")
        for h in reversed(st.session_state.history[-15:]):
            # Update the search query state and rerun to sync with the input box
            if st.button(f"🔍 {h}", key=f"hbtn_{h}"):
                st.session_state.search_query = h
                st.rerun()
        
        if st.session_state.history:
            if st.button("🗑️ Clear History"):
                st.session_state.history = []
                st.session_state.search_query = ""
                st.rerun()

    with hub_tabs[1]: # STARRED / LIBRARY
        if not st.session_state.library:
            st.caption("No starred items.")
        for item in st.session_state.library:
            st.markdown(f'<div class="lib-box"><b>{item["title"][:40]}...</b><br><a href="{item["link"]}" target="_blank" style="color:#58a6ff; text-decoration:none;">Open ↗</a></div>', unsafe_allow_html=True)

    with hub_tabs[2]: # READING LIST
        if not st.session_state.reading_list:
            st.caption("Reading list is empty.")
        for idx, paper in enumerate(st.session_state.reading_list):
            st.markdown(f'<div class="lib-box" style="border-left-color:#ffaa00;"><b>{paper["title"][:40]}...</b></div>', unsafe_allow_html=True)
            if st.button("✅ Mark as Read", key=f"read_fin_{idx}"):
                st.session_state.reading_list.pop(idx)
                st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🛰️ Research-Pilot Pro")

# The search bar value is synced with session_state.search_query
query = st.text_input(
    "Global Search", 
    value=st.session_state.search_query, 
    placeholder="Enter keywords (e.g., Large Language Models)...",
    key="search_input_main"
)

# Manual sync if user types directly
if query != st.session_state.search_query:
    st.session_state.search_query = query

depth = st.select_slider("Scan Depth", options=[3, 5, 10, 15, 20], value=5)

# --- 6. SEARCH LOGIC ---
if st.session_state.search_query:
    active_q = st.session_state.search_query
    
    if active_q not in st.session_state.history:
        st.session_state.history.append(active_q)

    with st.spinner(f'Scanning global networks for "{active_q}"...'):
        t1, t2, t3 = st.tabs(["🌐 Web Index", "🐙 GitHub Code", "📄 Academic (ArXiv)"])

        # TAB 1: WEB (GOOGLE REDIRECT)
        with t1:
            google_url = f"https://www.google.com/search?q={quote(active_q)}"
            st.markdown(f"""
                <div class="res-card">
                    <div class="res-title">External Intelligence: {active_q}</div>
                    <p style="color:#8b949e; font-size:14px;">Access real-time web results and news on Google.</p>
                    <a href="{google_url}" target="_blank" style="color:#58a6ff; text-decoration:none; font-weight:bold;">Launch External Scan ↗</a>
                </div>
            """, unsafe_allow_html=True)

        # TAB 2: GITHUB
        with t2:
            gh_url = f"https://api.github.com/search/repositories?q={quote(active_q)}&sort=stars"
            try:
                gh_data = requests.get(gh_url, timeout=10).json().get('items', [])
                for item in gh_data[:depth]:
                    st.markdown(f'<div class="res-card"><div class="res-title">{item["full_name"]}</div><p style="font-size:14px; color:#c9d1d9;">{item["description"][:160] if item["description"] else "No logs."}...</p></div>', unsafe_allow_html=True)
                    
                    c1, c2, c3, c_sp = st.columns([0.1, 0.1, 0.1, 0.7])
                    with c1: st.link_button("👁️", item['html_url'], help="View Code")
                    with c2: 
                        if st.button("📚", key=f"r_gh_{item['id']}", help="Add to Reading List"):
                            st.session_state.reading_list.append({"title": item['full_name'], "link": item['html_url']})
                            st.toast("Saved to Reading List")
                    with c3:
                        if st.button("⭐", key=f"s_gh_{item['id']}", help="Star to Library"):
                            st.session_state.library.append({"title": item['full_name'], "link": item['html_url']})
                            st.toast("Saved to Library")
            except: st.error("GitHub connection error.")

        # TAB 3: ACADEMIC (ARXIV)
        with t3:
            ar_url = f"http://export.arxiv.org/api/query?search_query=all:{quote(active_q)}&max_results={depth}"
            try:
                root = ET.fromstring(requests.get(ar_url, timeout=10).text)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                    l = entry.find('{http://www.w3.org/2005/Atom}id').text
                    
                    st.markdown(f'<div class="res-card"><div class="res-title">{t[:120]}...</div></div>', unsafe_allow_html=True)
                    
                    c1, c2, c3, c_sp = st.columns([0.1, 0.1, 0.1, 0.7])
                    with c1: st.link_button("👁️", l, help="Read Paper")
                    with c2:
                        if st.button("📚", key=f"r_ar_{l}", help="Add to Reading List"):
                            st.session_state.reading_list.append({"title": t, "link": l})
                            st.toast("Added to Reading List")
                    with c3:
                        if st.button("⭐", key=f"s_ar_{l}", help="Star to Library"):
                            st.session_state.library.append({"title": t, "link": l})
                            st.toast("Starred to Library")
            except: st.error("ArXiv database unreachable.")

    st.balloons()
