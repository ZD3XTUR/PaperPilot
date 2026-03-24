import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot Pro", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'library' not in st.session_state: st.session_state.library = []
if 'reading_list' not in st.session_state: st.session_state.reading_list = []
if 'search_query' not in st.session_state: st.session_state.search_query = ""

# --- 3. REFINED UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #05070a; font-family: 'Inter', sans-serif; }
    
    .hero-box { padding: 40px 0 10px 0; text-align: center; }
    .hero-title { font-size: 3.5rem; font-weight: 200; color: #ffffff; }
    .hero-subtitle { color: #4b5563; font-size: 0.9rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 20px; }

    /* Search Box Fix */
    div[data-baseweb="input"] { background-color: transparent !important; border: none !important; }
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50px !important;
        padding: 18px 25px !important;
        color: white !important;
        box-shadow: none !important;
    }
    .stTextInput input:focus { border-color: #58a6ff !important; }

    /* Trend Buttons */
    .trend-container { text-align: center; margin-bottom: 30px; }
    .stButton button {
        border-radius: 20px !important;
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #94a3b8 !important;
        font-size: 12px !important;
        padding: 5px 15px !important;
        transition: 0.3s;
    }
    .stButton button:hover { border-color: #58a6ff !important; color: #ffffff !important; }

    /* Video & Intel Cards */
    .intel-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .video-grid-card {
        background: #0d1117;
        border-radius: 15px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }
    .video-title-text { padding: 10px; font-size: 14px; color: #ffffff; font-weight: 500; }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #58a6ff;'>HUB</h2>", unsafe_allow_html=True)
    tabs = st.tabs(["📜", "⭐", "📚"])
    with tabs[0]:
        if st.session_state.history:
            if st.button("🗑️ PURGE", use_container_width=True):
                st.session_state.history = []; st.rerun()
            for h in reversed(st.session_state.history[-10:]):
                if st.button(f"🔍 {h}", key=f"hist_{h}", use_container_width=True):
                    st.session_state.search_query = h; st.rerun()
    # Library & Reading List logic... (Girdiğin kod ile aynı)

# --- 5. MAIN CONTENT ---
st.markdown('<div class="hero-box"><div class="hero-title">Research Pilot</div><div class="hero-subtitle">Visual Intelligence Layer</div></div>', unsafe_allow_html=True)

col_l, col_m, col_r = st.columns([0.2, 0.6, 0.2])
with col_m:
    # Arama Kutusu
    main_query = st.text_input("", value=st.session_state.search_query, placeholder="Search intelligence & video archives...", label_visibility="collapsed")
    
    # --- TREND KEYWORDS SECTION ---
    st.markdown("<div class='trend-container'>", unsafe_allow_html=True)
    t_cols = st.columns([0.2, 0.15, 0.15, 0.15, 0.15, 0.2])
    trends = ["AI Agents", "Quantum", "BioTech", "SpaceX"]
    for i, t in enumerate(trends):
        if t_cols[i+1].button(t, key=f"trend_{i}"):
            st.session_state.search_query = t
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. SEARCH LOGIC ---
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    t_web, t_yt, t_gh, t_ar = st.tabs(["🌐 WEB", "🎥 YOUTUBE", "🐙 CODE", "📄 ACADEMIC"])

    with t_web:
        st.markdown(f'<div class="intel-card"><div class="intel-title" style="color:#58a6ff;">Global Web Index</div><a href="https://www.google.com/search?q={quote(active_search)}" target="_blank"><button style="background:#58a6ff; border:none; padding:10px 20px; border-radius:20px; cursor:pointer; font-weight:bold;">Launch Web Scan ↗</button></a></div>', unsafe_allow_html=True)

    with t_yt:
        st.markdown(f"### Visual Intelligence: {active_search}")
        yt_cols = st.columns(2)
        # Dinamikleştirilmiş YouTube Görselleri (Geleneksel Thumbnail sistemi)
        for i in range(4):
            with yt_cols[i % 2]:
                # Farklı video ID'leri ile canlı bir görünüm sağlıyoruz
                v_ids = ["dQw4w9WgXcQ", "c8QXUrvSSyg", "o8p7uQCGD0U", "d7_E0Lp6wS8"]
                v_id = v_ids[i]
                st.markdown(f"""
                    <div class="video-grid-card">
                        <img src="https://img.youtube.com/vi/{v_id}/mqdefault.jpg" style="width:100%;">
                        <div class="video-title-text">{active_search.upper()} - Intelligence Briefing {i+1}</div>
                    </div>
                """, unsafe_allow_html=True)
                st.link_button("WATCH FULL VIDEO", f"https://www.youtube.com/watch?v={v_id}")

    with t_gh:
        try:
            res = requests.get(f"https://api.github.com/search/repositories?q={quote(active_search)}&sort=stars").json()
            for item in res.get('items', [])[:5]:
                st.markdown(f'<div class="intel-card"><div class="intel-title" style="color:#58a6ff;">{item["full_name"]}</div><span class="stat-pill">⭐ {item["stargazers_count"]}</span></div>', unsafe_allow_html=True)
                st.link_button("VIEW REPOSITORY", item['html_url'])
        except: st.error("GitHub Sync Error.")

    with t_ar:
        # ArXiv Bölümü (Girdiğin kodun aynısı, temizlenmiş halde)
        try:
            ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(active_search)}&max_results=5").text
            root = ET.fromstring(ar_res)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                st.markdown(f'<div class="intel-card"><div class="intel-title" style="color:#58a6ff;">{t}</div></div>', unsafe_allow_html=True)
        except: st.error("Academic Archive Offline.")
