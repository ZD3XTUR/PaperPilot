import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot Pro", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE MANAGEMENT ---
if 'history' not in st.session_state: st.session_state.history = []
if 'library' not in st.session_state: st.session_state.library = []
if 'reading_list' not in st.session_state: st.session_state.reading_list = []

def trigger_history_search(query_from_button):
    st.session_state["search_bar_widget"] = query_from_button

# --- 3. PREMIUM ADVANCED UI STYLING ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background: radial-gradient(circle at top right, #1e222d, #0e1117); color: #fafafa; }
    
    /* Neumorphic / Glass Cards for Results */
    .res-card {
        background: rgba(26, 28, 36, 0.6);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(88, 166, 255, 0.2);
        margin-bottom: 15px;
        transition: 0.3s all ease;
    }
    .res-card:hover {
        border-color: #58a6ff;
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.3);
        transform: translateY(-2px);
    }
    
    /* Professional Sidebar Item Styling */
    .hub-item {
        background: linear-gradient(90deg, rgba(33, 38, 45, 0.8), rgba(22, 27, 34, 0.8));
        border-left: 4px solid #58a6ff;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        position: relative;
        transition: 0.3s;
    }
    .hub-item:hover { background: rgba(88, 166, 255, 0.1); }
    
    .hub-title { font-size: 13px; font-weight: bold; color: #f0f6fc; margin-bottom: 4px; display: block; }
    .hub-meta { font-size: 11px; color: #8b949e; }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }

    /* Icon-only Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; justify-content: center; background: transparent; }
    .stTabs [data-baseweb="tab"] { font-size: 22px !important; border-bottom: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR: THE VISUAL HUB ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #58a6ff;'>INTEL HUB</h1>", unsafe_allow_html=True)
    st.divider()
    
    hub_tabs = st.tabs(["📜", "⭐", "📚"])
    
    # --- HISTORY TAB ---
    with hub_tabs[0]:
        st.markdown("<p style='font-size:12px; color:#58a6ff; font-weight:bold;'>RECENT SCANS</p>", unsafe_allow_html=True)
        if st.session_state.history:
            if st.button("🗑️ PURGE HISTORY", type="secondary", use_container_width=True):
                st.session_state.history = []
                st.rerun()
            
            for h in reversed(st.session_state.history[-10:]):
                if st.button(f"🔎 {h}", key=f"hist_{h}", on_click=trigger_history_search, args=(h,)):
                    pass
        else:
            st.caption("No data logged.")

    # --- LIBRARY TAB ---
    with hub_tabs[1]:
        st.markdown("<p style='font-size:12px; color:#3fb950; font-weight:bold;'>SAVED INTELLIGENCE</p>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.library):
            with st.container():
                st.markdown(f"""
                    <div class="hub-item" style="border-left-color: #3fb950;">
                        <span class="hub-title">{item['title'][:40]}...</span>
                    </div>
                """, unsafe_allow_html=True)
                col_btn1, col_btn2 = st.columns([0.8, 0.2])
                with col_btn1: st.link_button("OPEN SOURCE ↗", item['link'], use_container_width=True)
                with col_btn2: 
                    if st.button("✖️", key=f"rm_lib_{idx}"):
                        st.session_state.library.pop(idx)
                        st.rerun()

    # --- READING LIST TAB ---
    with hub_tabs[2]:
        st.markdown("<p style='font-size:12px; color:#ffaa00; font-weight:bold;'>READING QUEUE</p>", unsafe_allow_html=True)
        for idx, paper in enumerate(st.session_state.reading_list):
            with st.container():
                st.markdown(f"""
                    <div class="hub-item" style="border-left-color: #ffaa00;">
                        <span class="hub-title">{paper['title'][:40]}...</span>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"✔️ MARK AS COMPLETE", key=f"fin_{idx}", use_container_width=True):
                    st.session_state.reading_list.pop(idx)
                    st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🛰️ Research-Pilot Pro")
st.caption("Unified Intelligence Engine for Researchers & Developers")

query = st.text_input(
    "GLOBAL SEARCH", 
    placeholder="Search the decentralized web and academic archives...",
    key="search_bar_widget" 
)

depth = st.select_slider("SCAN DEPTH", options=[3, 5, 10, 15], value=5)

if query:
    if query not in st.session_state.history:
        st.session_state.history.append(query)

    with st.spinner('Synchronizing Data...'):
        t_web, t_gh, t_ar = st.tabs(["🌐 WEB INDEX", "🐙 GITHUB", "📄 ARXIV"])

        # TAB 1: WEB
        with t_web:
            url = f"https://www.google.com/search?q={quote(query)}"
            st.markdown(f"""
                <div class="res-card">
                    <h3 style="color:#58a6ff;">Live Web Analysis</h3>
                    <p style="color:#8b949e;">Deep scanning results for <b>{query}</b></p>
                    <a href="{url}" target="_blank" style="text-decoration:none;">
                        <button style="background:#238636; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">
                            LAUNCH SCAN ↗
                        </button>
                    </a>
                </div>
            """, unsafe_allow_html=True)

        # TAB 2: GITHUB
        with t_gh:
            try:
                gh_res = requests.get(f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars", timeout=10).json()
                for item in gh_res.get('items', [])[:depth]:
                    st.markdown(f"""
                        <div class="res-card">
                            <div class="res-title">{item['full_name']}</div>
                            <div style="font-size:13px; color:#8b949e; margin-bottom:10px;">{item['description'] or 'No description available.'}</div>
                            <span style="color:#3fb950; font-weight:bold;">⭐ {item['stargazers_count']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    c1, c2, c3, _ = st.columns([0.2, 0.1, 0.1, 0.6])
                    with c1: st.link_button("VIEW ↗", item['html_url'])
                    with c2: 
                        if st.button("📚", key=f"r_gh_{item['id']}", help="Add to Reading List"):
                            st.session_state.reading_list.append({"title": item['full_name'], "link": item['html_url']})
                            st.toast("Reading List Updated")
                    with c3:
                        if st.button("⭐", key=f"s_gh_{item['id']}", help="Save to Library"):
                            st.session_state.library.append({"title": item['full_name'], "link": item['html_url']})
                            st.toast("Saved to Library")
            except: st.error("GitHub Index Offline")

        # TAB 3: ARXIV
        with t_ar:
            try:
                ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(query)}&max_results={depth}", timeout=10).text
                root = ET.fromstring(ar_res)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                    link = entry.find('{http://www.w3.org/2005/Atom}id').text
                    st.markdown(f'<div class="res-card"><div class="res-title">{title}</div></div>', unsafe_allow_html=True)
                    c1, c2, c3, _ = st.columns([0.2, 0.1, 0.1, 0.6])
                    with c1: st.link_button("READ ↗", link)
                    with c2:
                        if st.button("📚", key=f"r_ar_{link}"):
                            st.session_state.reading_list.append({"title": title, "link": link})
                            st.toast("Reading List Updated")
                    with c3:
                        if st.button("⭐", key=f"s_ar_{link}"):
                            st.session_state.library.append({"title": title, "link": link})
                            st.toast("Saved to Library")
            except: st.error("Academic Database Error")

    st.balloons()
