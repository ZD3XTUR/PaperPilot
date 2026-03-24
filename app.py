import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
import random

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot Ultra", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'library' not in st.session_state: st.session_state.library = []
if 'reading_list' not in st.session_state: st.session_state.reading_list = []

def trigger_history_search(query_text):
    st.session_state["search_bar_widget"] = query_text

# --- 3. CYBER-TECH UI STYLING ---
st.markdown("""
    <style>
    /* Global Styles */
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #020617 100%);
        color: #e2e8f0;
    }
    
    /* Hero Header */
    .hero-container {
        padding: 40px;
        text-align: center;
        background: rgba(30, 41, 59, 0.4);
        border-radius: 20px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    /* Metric Cards */
    .stat-card {
        background: rgba(15, 23, 42, 0.8);
        border-left: 3px solid #38bdf8;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        transition: 0.3s;
    }
    .stat-card:hover { transform: scale(1.05); border-left-color: #818cf8; }
    
    /* Result Cards */
    .res-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(12px);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 15px;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .res-card:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: #38bdf8;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
    }

    /* Sidebar Enhancement */
    [data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid rgba(56, 189, 248, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (MINIMALIST HUB) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #38bdf8;'>HUB</h2>", unsafe_allow_html=True)
    
    tabs = st.tabs(["📜", "⭐", "📚"])
    
    with tabs[0]: # HISTORY
        if st.session_state.history:
            if st.button("🗑️ PURGE", use_container_width=True):
                st.session_state.history = []
                st.rerun()
            for h in reversed(st.session_state.history[-10:]):
                st.button(f"🔍 {h}", key=f"hist_{h}", on_click=trigger_history_search, args=(h,))
    
    with tabs[1]: # LIBRARY
        for idx, item in enumerate(st.session_state.library):
            col_t, col_r = st.columns([0.8, 0.2])
            with col_t: st.markdown(f"**[{item['title'][:30]}...]({item['link']})**")
            with col_r: 
                if st.button("✖️", key=f"rl_{idx}"):
                    st.session_state.library.pop(idx); st.rerun()

    with tabs[2]: # READING
        for idx, p in enumerate(st.session_state.reading_list):
            if st.button(f"✔️ {p['title'][:35]}...", key=f"rd_{idx}", use_container_width=True):
                st.session_state.reading_list.pop(idx); st.rerun()

# --- 5. MAIN CONTENT ---

# HERO SECTION (Always visible)
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">RESEARCH PILOT</div>
        <p style="color: #94a3b8; font-size: 1.1rem;">Decentralized Intelligence Engine & Academic Archive</p>
    </div>
    """, unsafe_allow_html=True)

# LIVE STATS (Keeps the page from looking empty)
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="stat-card"><small>HISTORY</small><h4>{len(st.session_state.history)}</h4></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="stat-card"><small>LIBRARY</small><h4>{len(st.session_state.library)}</h4></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="stat-card"><small>QUEUED</small><h4>{len(st.session_state.reading_list)}</h4></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="stat-card"><small>STATUS</small><h4 style="color:#3fb950;">ONLINE</h4></div>', unsafe_allow_html=True)

st.divider()

# SEARCH AREA
query = st.text_input("", placeholder="🔍 Search global repositories, papers, or web indices...", key="search_bar_widget")

# SUGGESTION CHIPS (Creative touch)
st.markdown("<small style='color:#64748b;'>TRENDING:</small>", unsafe_allow_html=True)
cols = st.columns(5)
suggestions = ["Quantum AI", "Rust Web Frameworks", "Neural Radiance Fields", "DeFi Security", "LLM Fine-tuning"]
for i, s in enumerate(suggestions):
    if cols[i].button(s, key=f"sug_{i}"):
        st.session_state.active_query = s
        st.session_state["search_bar_widget"] = s
        st.rerun()

# --- 6. SEARCH LOGIC ---
if query:
    if query not in st.session_state.history:
        st.session_state.history.append(query)

    with st.spinner('📡 Intercepting Data...'):
        t_web, t_gh, t_ar = st.tabs(["🌐 WEB INDEX", "🐙 GITHUB", "📄 ARXIV"])

        # GITHUB LOGIC (Simplified for clarity)
        with t_gh:
            try:
                res = requests.get(f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars").json()
                for item in res.get('items', [])[:5]:
                    st.markdown(f"""
                        <div class="res-card">
                            <div style="display:flex; justify-content:space-between;">
                                <span style="color:#38bdf8; font-weight:bold; font-size:18px;">{item['full_name']}</span>
                                <span style="color:#3fb950;">⭐ {item['stargazers_count']}</span>
                            </div>
                            <p style="color:#94a3b8; font-size:14px; margin-top:10px;">{item['description'] or 'No description.'}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    btn_c1, btn_c2, btn_c3, _ = st.columns([0.15, 0.1, 0.1, 0.65])
                    with btn_c1: st.link_button("VIEW ↗", item['html_url'])
                    with btn_c2: 
                        if st.button("📚", key=f"r_g_{item['id']}"):
                            st.session_state.reading_list.append({"title": item['full_name'], "link": item['html_url']})
                    with btn_c3:
                        if st.button("⭐", key=f"s_g_{item['id']}"):
                            st.session_state.library.append({"title": item['full_name'], "link": item['html_url']})
            except: st.error("Link Lost.")

        # ARXIV LOGIC
        with t_ar:
            try:
                ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(query)}&max_results=5").text
                root = ET.fromstring(ar_res)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                    l = entry.find('{http://www.w3.org/2005/Atom}id').text
                    st.markdown(f'<div class="res-card"><div style="color:#38bdf8; font-weight:bold;">{t}</div></div>', unsafe_allow_html=True)
                    bc1, bc2, bc3, _ = st.columns([0.15, 0.1, 0.1, 0.65])
                    with bc1: st.link_button("READ ↗", l)
                    with bc2:
                        if st.button("📚", key=f"r_a_{l}"):
                            st.session_state.reading_list.append({"title": t, "link": l})
                    with bc3:
                        if st.button("⭐", key=f"s_a_{l}"):
                            st.session_state.library.append({"title": t, "link": l})
            except: st.error("Database Error.")

    st.balloons()
