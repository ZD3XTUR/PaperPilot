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
    
    .hero-box { padding: 40px 0 5px 0; text-align: center; }
    .hero-title { font-size: 3.5rem; font-weight: 200; color: #ffffff; margin-bottom: 0px; }
    .hero-subtitle { color: #4b5563; font-size: 0.9rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 25px; }

    /* Arama Çubuğu - Kusursuz Tek Katman */
    div[data-baseweb="input"] { background-color: transparent !important; border: none !important; }
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50px !important;
        padding: 18px 25px !important;
        color: white !important;
        box-shadow: none !important;
    }
    .stTextInput input:focus { border-color: #58a6ff !important; box-shadow: 0 0 15px rgba(88, 166, 255, 0.1) !important; }

    /* Trend Kelimeler İçin Özel Grid */
    .trend-wrapper {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: -15px;
        margin-bottom: 30px;
    }
    
    /* Streamlit Butonlarını Trend Stiline Sokma */
    div.stButton > button {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #94a3b8 !important;
        border-radius: 20px !important;
        padding: 4px 15px !important;
        font-size: 12px !important;
        transition: 0.3s !important;
    }
    div.stButton > button:hover {
        border-color: #58a6ff !important;
        color: white !important;
        background-color: rgba(88, 166, 255, 0.1) !important;
    }

    /* Kartlar */
    .intel-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
    }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (Girdiğin Kararlı Sürüm) ---
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
    # Library ve Reading List kısımları aynı kalıyor...

# --- 5. ANA EKRAN ---
st.markdown('<div class="hero-box"><div class="hero-title">Research Pilot</div><div class="hero-subtitle">The Intelligence Layer</div></div>', unsafe_allow_html=True)

col_l, col_m, col_r = st.columns([0.2, 0.6, 0.2])
with col_m:
    # Arama Girişi
    main_query = st.text_input("", value=st.session_state.search_query, placeholder="Search intelligence & video archives...", label_visibility="collapsed")
    
    # --- TREND KEYWORDS (YAN YANA VE DÜZGÜN) ---
    # Streamlit'te yan yana butonlar için küçük sütunlar en güvenli yoldur:
    t1, t2, t3, t4, t5 = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])
    trends = ["AI Agents", "Quantum", "BioTech", "SpaceX", "Solana"]
    
    with t1: 
        if st.button(trends[0], use_container_width=True): st.session_state.search_query = trends[0]; st.rerun()
    with t2: 
        if st.button(trends[1], use_container_width=True): st.session_state.search_query = trends[1]; st.rerun()
    with t3: 
        if st.button(trends[2], use_container_width=True): st.session_state.search_query = trends[2]; st.rerun()
    with t4: 
        if st.button(trends[3], use_container_width=True): st.session_state.search_query = trends[3]; st.rerun()
    with t5: 
        if st.button(trends[4], use_container_width=True): st.session_state.search_query = trends[4]; st.rerun()

# --- 6. ARAMA MANTIĞI ---
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    t_web, t_yt, t_gh, t_ar = st.tabs(["🌐 WEB", "🎥 YOUTUBE", "🐙 CODE", "📄 ACADEMIC"])

    with t_web:
        st.markdown(f'<div class="intel-card"><div class="intel-title" style="color:#58a6ff; font-weight:bold; margin-bottom:10px;">Global Web Index</div><a href="https://www.google.com/search?q={quote(active_search)}" target="_blank"><button style="background:#58a6ff; border:none; padding:10px 20px; border-radius:20px; cursor:pointer; color:black; font-weight:bold;">Launch Web Scan ↗</button></a></div>', unsafe_allow_html=True)

    with t_yt:
        yt_url = f"https://www.youtube.com/results?search_query={quote(active_search)}"
        st.markdown(f"""
            <div class="intel-card" style="border-color: #ff000033;">
                <div class="intel-title" style="color:#ff0000; font-weight:bold; margin-bottom:10px;">YouTube Visual Intelligence</div>
                <img src="https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg" style="width:100%; border-radius:15px; margin-bottom:15px; border: 1px solid rgba(255,255,255,0.1);">
                <p style="color:#94a3b8; font-size:14px;">Broadcasting video intelligence for <b>{active_search}</b>.</p>
                <a href="{yt_url}" target="_blank" style="text-decoration:none;">
                    <button style="background:#ff0000; color:white; border:none; padding:10px 25px; border-radius:20px; font-weight:bold; cursor:pointer;">
                        OPEN CHANNEL 🎥
                    </button>
                </a>
            </div>
        """, unsafe_allow_html=True)

    with t_gh:
        try:
            res = requests.get(f"https://api.github.com/search/repositories?q={quote(active_search)}&sort=stars").json()
            for item in res.get('items', [])[:5]:
                st.markdown(f'<div class="intel-card"><div style="color:#58a6ff; font-weight:bold;">{item["full_name"]}</div><span style="background:rgba(88,166,255,0.1); color:#58a6ff; padding:2px 8px; border-radius:10px; font-size:10px;">⭐ {item["stargazers_count"]}</span></div>', unsafe_allow_html=True)
                st.link_button("VIEW REPO", item['html_url'])
        except: st.error("GitHub Sync Error.")

    with t_ar:
        try:
            ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(active_search)}&max_results=5").text
            root = ET.fromstring(ar_res)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                st.markdown(f'<div class="intel-card"><div style="color:#58a6ff; font-weight:bold;">{t}</div></div>', unsafe_allow_html=True)
        except: st.error("ArXiv Error.")
