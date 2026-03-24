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

# --- CALLBACK: The Secret Sauce ---
def trigger_history_search(query_from_button):
    # This force-updates the widget's internal state
    st.session_state["search_bar_widget"] = query_from_button

# --- 3. UI STYLING ---
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
    /* Sidebar History Buttons */
    div.stButton > button {
        background-color: #21262d;
        border: 1px solid #30363d;
        color: white;
        text-align: left;
        width: 100%;
        font-size: 13px;
    }
    div.stButton > button:hover { border-color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (RESEARCH HUB) ---
with st.sidebar:
    st.title("🛰️ Research Hub")
    tabs = st.tabs(["📜 History", "⭐ Starred", "📚 Reading"])
    
    with tabs[0]:
        if not st.session_state.history:
            st.caption("History is empty.")
        for h in reversed(st.session_state.history[-15:]):
            # ON_CLICK is the only way to guarantee the text box updates instantly
            st.button(f"🔍 {h}", key=f"btn_{h}", on_click=trigger_history_search, args=(h,))

    with tabs[1]:
        for item in st.session_state.library:
            st.markdown(f'<div style="font-size:12px; margin-bottom:5px;">⭐ {item["title"][:40]}...</div>', unsafe_allow_html=True)

    with tabs[2]:
        for idx, paper in enumerate(st.session_state.reading_list):
            st.caption(f"📚 {paper['title'][:40]}...")
            if st.button("✅ Done", key=f"rd_{idx}"):
                st.session_state.reading_list.pop(idx)
                st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🛰️ Research-Pilot Pro")

# The 'key' here connects directly to the trigger_history_search function
query = st.text_input(
    "Global Search", 
    placeholder="Type and press Enter...",
    key="search_bar_widget" 
)

depth = st.select_slider("Scan Depth", options=[3, 5, 10, 15], value=5)

# --- 6. SEARCH ENGINE ---
if query:
    if query not in st.session_state.history:
        st.session_state.history.append(query)

    with st.spinner(f'Analyzing "{query}"...'):
        t_web, t_gh, t_ar = st.tabs(["🌐 Web Index", "🐙 GitHub Code", "📄 Academic (ArXiv)"])

        # WEB TAB
        with t_web:
            st.info("Direct Web Scanning enabled.")
            url = f"https://www.google.com/search?q={quote(query)}"
            st.markdown(f'<div class="res-card"><div class="res-title">Web Results for: {query}</div><a href="{url}" target="_blank" style="color:#58a6ff;">Launch Live Scan ↗</a></div>', unsafe_allow_html=True)

        # GITHUB TAB
        with t_gh:
            try:
                gh_res = requests.get(f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars", timeout=10).json()
                for item in gh_res.get('items', [])[:depth]:
                    st.markdown(f'<div class="res-card"><div class="res-title">{item["full_name"]}</div><div style="font-size:13px; color:#8b949e;">{item["description"] or "No logs."}</div></div>', unsafe_allow_html=True)
                    c1, c2, c3, _ = st.columns([0.1, 0.1, 0.1, 0.7])
                    with c1: st.link_button("👁️", item['html_url'])
                    with c2: 
                        if st.button("📚", key=f"r_gh_{item['id']}"):
                            st.session_state.reading_list.append({"title": item['full_name'], "link": item['html_url']})
                            st.toast("Added to Reading List")
                    with c3:
                        if st.button("⭐", key=f"s_gh_{item['id']}"):
                            st.session_state.library.append({"title": item['full_name'], "link": item['html_url']})
                            st.toast("Starred")
            except: st.error("GitHub API offline.")

        # ARXIV TAB
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
                            st.toast("Added to Reading List")
                    with c3:
                        if st.button("⭐", key=f"s_ar_{link}"):
                            st.session_state.library.append({"title": title, "link": link})
                            st.toast("Starred")
            except: st.error("Academic database error.")

    st.balloons()
