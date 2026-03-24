import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Research-Pilot Pro", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE (HAFIZA) ---
if 'history' not in st.session_state: st.session_state.history = []
if 'library' not in st.session_state: st.session_state.library = []
if 'reading_list' not in st.session_state: st.session_state.reading_list = []
if 'search_query' not in st.session_state: st.session_state.search_query = ""

# --- 3. GÜÇLÜ VE TEMİZ CSS (TASARIM) ---
st.markdown("""
    <style>
    /* Arka Plan ve Genel Font */
    .stApp { background-color: #05070a; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Hero Alanı */
    .hero-box { padding: 40px 0 20px 0; text-align: center; }
    .hero-title { font-size: 3.2rem; font-weight: 200; letter-spacing: -1px; margin-bottom: 5px; }
    .hero-subtitle { color: #4b5563; font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; }

    /* Arama Kutusu Fix (Tek Katman, Pürüzsüz) */
    div[data-baseweb="input"] { background-color: transparent !important; border: none !important; }
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50px !important;
        padding: 15px 25px !important;
        color: white !important;
        box-shadow: none !important;
    }
    .stTextInput input:focus { border-color: #58a6ff !important; box-shadow: 0 0 15px rgba(88, 166, 255, 0.1) !important; }

    /* Video Kartları */
    .video-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 12px;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .video-card:hover { border-color: #ff0000; background: rgba(255, 0, 0, 0.03); }
    .video-title { font-size: 0.9rem; font-weight: 600; color: #ffffff; margin: 10px 0 5px 0; height: 40px; overflow: hidden; }

    /* Akademik ve Kod Kartları */
    .intel-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .intel-title { color: #58a6ff; font-weight: bold; margin-bottom: 5px; }

    /* Gizlemeler */
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SOL MENÜ (HUB) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #58a6ff;'>HUB</h2>", unsafe_allow_html=True)
    tab_h, tab_s, tab_r = st.tabs(["📜", "⭐", "📚"])
    
    with tab_h:
        if st.session_state.history:
            if st.button("🗑️ TEMİZLE", use_container_width=True):
                st.session_state.history = []; st.rerun()
            for h in reversed(st.session_state.history[-10:]):
                if st.button(f"🔍 {h}", key=f"h_{h}", use_container_width=True):
                    st.session_state.search_query = h; st.rerun()

    with tab_s:
        for idx, item in enumerate(st.session_state.library):
            if st.button(f"🔗 {item['title'][:20]}...", key=f"s_{idx}", use_container_width=True):
                st.session_state.library.pop(idx); st.rerun()

    with tab_r:
        for idx, p in enumerate(st.session_state.reading_list):
            if st.button(f"📖 {p['title'][:20]}...", key=f"r_{idx}", use_container_width=True):
                st.session_state.reading_list.pop(idx); st.rerun()

# --- 5. ANA EKRAN ---
st.markdown('<div class="hero-box"><div class="hero-title">Research Pilot</div><div class="hero-subtitle">The Intelligence Engine</div></div>', unsafe_allow_html=True)

_, col_m, _ = st.columns([0.1, 0.8, 0.1])
with col_m:
    main_query = st.text_input("", value=st.session_state.search_query, placeholder="Search intelligence, videos, and code...", label_visibility="collapsed")

# --- 6. ARAMA MANTIĞI ---
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    t_yt, t_gh, t_ar = st.tabs(["🎥 YOUTUBE", "🐙 CODE", "📄 ACADEMIC"])

    with t_yt:
        st.write(f"### Video Intelligence for: {active_search}")
        v_cols = st.columns(2)
        # YouTube simülasyonu (Gerçek linklerle)
        for i in range(4):
            with v_cols[i % 2]:
                st.markdown(f"""
                <div class="video-card">
                    <img src="https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg" style="width:100%; border-radius:10px;">
                    <div class="video-title">YouTube Briefing: {active_search} - Segment {i+1}</div>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("WATCH ON YOUTUBE", f"https://www.youtube.com/results?search_query={quote(active_search)}")

    with t_gh:
        try:
            res = requests.get(f"https://api.github.com/search/repositories?q={quote(active_search)}&sort=stars").json()
            for item in res.get('items', [])[:5]:
                st.markdown(f'<div class="intel-card"><div class="intel-title">{item["full_name"]}</div><p style="font-size:12px; color:#94a3b8;">{item["description"]}</p></div>', unsafe_allow_html=True)
                st.link_button("VIEW REPO", item['html_url'])
        except: st.error("GitHub connection lost.")

    with t_ar:
        try:
            ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(active_search)}&max_results=5").text
            root = ET.fromstring(ar_res)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                st.markdown(f'<div class="intel-card"><div class="intel-title">{t}</div></div>', unsafe_allow_html=True)
        except: st.error("ArXiv connection lost.")
