import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot Pro", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE (TAM HAFIZA) ---
if 'history' not in st.session_state: st.session_state.history = []
if 'library' not in st.session_state: st.session_state.library = []
if 'reading_list' not in st.session_state: st.session_state.reading_list = []
if 'search_query' not in st.session_state: st.session_state.search_query = ""

# --- 3. UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #05070a; font-family: 'Inter', sans-serif; }
    .hero-box { padding: 30px 0 5px 0; text-align: center; }
    .hero-title { font-size: 3.2rem; font-weight: 200; color: #ffffff; }
    .hero-subtitle { color: #4b5563; font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 20px; }

    /* Search Box */
    div[data-baseweb="input"] { background-color: transparent !important; border: none !important; }
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50px !important;
        padding: 18px 25px !important;
        color: white !important;
    }

    /* Trend Buttons */
    div.stButton > button {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #94a3b8 !important;
        border-radius: 20px !important;
        font-size: 11px !important;
    }

    /* Intel Card */
    .intel-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 10px;
    }
    .intel-title { font-size: 1rem; font-weight: 600; color: #58a6ff; }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (HUB - TÜM ÖZELLİKLER AKTİF) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #58a6ff;'>HUB</h2>", unsafe_allow_html=True)
    tab_hist, tab_fav, tab_read = st.tabs(["📜", "⭐", "📚"])
    
    with tab_hist:
        # ÇÖP KUTUSU (PURGE) - GERİ GELDİ
        if st.session_state.history:
            if st.button("🗑️ PURGE HISTORY", use_container_width=True):
                st.session_state.history = []
                st.session_state.search_query = ""
                st.rerun()
            st.divider()
            for h in reversed(st.session_state.history[-10:]):
                if st.button(f"🔍 {h}", key=f"hist_btn_{h}", use_container_width=True):
                    st.session_state.search_query = h
                    st.rerun()
                
    with tab_fav:
        for idx, item in enumerate(st.session_state.library):
            c1, c2 = st.columns([0.8, 0.2])
            c1.markdown(f"<small>[{item['title'][:20]}...]({item['link']})</small>", unsafe_allow_html=True)
            if c2.button("✖", key=f"fav_rm_{idx}"):
                st.session_state.library.pop(idx); st.rerun()

    with tab_read:
        for idx, p in enumerate(st.session_state.reading_list):
            c1, c2 = st.columns([0.8, 0.2])
            c1.markdown(f"<small>📖 {p['title'][:20]}...</small>", unsafe_allow_html=True)
            if c2.button("✔", key=f"read_rm_{idx}"):
                st.session_state.reading_list.pop(idx); st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown('<div class="hero-box"><div class="hero-title">Research Pilot</div><div class="hero-subtitle">The Intelligence Engine</div></div>', unsafe_allow_html=True)

_, col_m, _ = st.columns([0.15, 0.7, 0.15])
with col_m:
    main_query = st.text_input("", value=st.session_state.search_query, placeholder="Search intelligence...", label_visibility="collapsed")
    
    # TREND KEYWORDS (YAN YANA - SABİT)
    t_cols = st.columns(5)
    trends = ["AI Agents", "Quantum", "BioTech", "SpaceX", "Solana"]
    for i, t in enumerate(trends):
        if t_cols[i].button(t, key=f"trend_btn_{i}", use_container_width=True):
            st.session_state.search_query = t
            st.rerun()

# --- 6. SEARCH LOGIC ---
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    t_web, t_yt, t_gh, t_ar = st.tabs(["🌐 WEB", "🎥 YOUTUBE", "🐙 CODE", "📄 ACADEMIC"])

    with t_web:
        st.markdown(f'<div class="intel-card"><div class="intel-title">Google Search</div><a href="https://www.google.com/search?q={quote(active_search)}" target="_blank"><button style="background:#58a6ff; border:none; padding:10px 25px; border-radius:25px; cursor:pointer; font-weight:bold; color:black;">LAUNCH SCAN ↗</button></a></div>', unsafe_allow_html=True)

    with t_yt:
        yt_url = f"https://www.youtube.com/results?search_query={quote(active_search)}"
        st.markdown(f"""
            <div class="intel-card" style="border-color: #ff000033;
