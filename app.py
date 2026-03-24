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

# --- 3. CSS (TASARIM) ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Hero */
    .hero-box { padding: 30px 0 10px 0; text-align: center; }
    .hero-title { font-size: 3rem; font-weight: 200; color: #ffffff; margin-bottom: 0px; }
    .hero-subtitle { color: #4b5563; font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 20px; }

    /* Arama Kutusu - Tek Katman Fix */
    div[data-baseweb="input"] { background-color: transparent !important; border: none !important; }
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50px !important;
        padding: 15px 25px !important;
        color: white !important;
        box-shadow: none !important;
    }
    .stTextInput input:focus { border-color: #58a6ff !important; }

    /* Trend Butonları */
    .stButton button {
        border-radius: 20px !important;
        text-transform: uppercase;
        font-size: 10px !important;
        letter-spacing: 1px;
    }

    /* Kartlar */
    .video-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 12px;
        margin-bottom: 15px;
    }
    .video-title { font-size: 0.85rem; font-weight: 600; color: #ffffff; margin-top: 8px; height: 35px; overflow: hidden; }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #58a6ff;'>CONTROL HUB</h3>", unsafe_allow_html=True)
    tab_h, tab_s = st.tabs(["GEÇMİŞ", "KÜTÜPHANE"])
    with tab_h:
        for h in reversed(st.session_state.history[-8:]):
            if st.button(f"🔍 {h}", key=f"hist_{h}", use_container_width=True):
                st.session_state.search_query = h
                st.rerun()
    with tab_s:
        for idx, item in enumerate(st.session_state.library):
            st.markdown(f"<small>• {item['title'][:25]}</small>", unsafe_allow_html=True)

# --- 5. ANA EKRAN ---
st.markdown('<div class="hero-box"><div class="hero-title">Research Pilot</div><div class="hero-subtitle">The Intelligence Engine</div></div>', unsafe_allow_html=True)

_, col_m, _ = st.columns([0.15, 0.7, 0.15])
with col_m:
    # Arama kutusu
    main_query = st.text_input("", value=st.session_state.search_query, placeholder="Search intelligence, videos, and code...", label_visibility="collapsed")
    
    # Trend Aramalar (Geri Getirildi)
    st.markdown("<div style='text-align:center; margin-top:-10px; margin-bottom:20px;'>", unsafe_allow_html=True)
    t_cols = st.columns([0.2, 0.15, 0.15, 0.15, 0.15, 0.2])
    trends = ["AI Agents", "Next.js 15", "Quantum", "CyberSec"]
    for i, t in enumerate(trends):
        if t_cols[i+1].button(t, key=f"tr_{i}"):
            st.session_state.search_query = t
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. ARAMA MANTIĞI ---
# Eğer arama çubuğuna bir şey yazıldıysa o geçerli olur
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    t_yt, t_gh, t_ar = st.tabs(["🎥 YOUTUBE EXPLORER", "🐙 GITHUB REPOS", "📄 ACADEMIC"])

    with t_yt:
        st.markdown(f"#### Video Analysis for: `{active_search}`")
        v_cols = st.columns(3)
        # Dinamik YouTube linkleri
        yt_search_base = f"https://www.youtube.com/results?search_query={quote(active_search)}"
        
        for i in range(6): # 6 video kartı
            with v_cols[i % 3]:
                st.markdown(f"""
                <div class="video-card">
                    <img src="https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg" style="width:100%; border-radius:10px; filter: grayscale(30%);">
                    <div class="video-title">Intelligence Report: {active_search} - Part {i+1}</div>
                </div>
                """, unsafe_allow_html=True)
                # Buradaki link artık aktif arama terimini YouTube'a gönderiyor
                st.link_button("WATCH NOW", f"{yt_search_base}", use_container_width=True)

    with t_gh:
        try:
            res = requests.get(f"https://api.github.com/search/repositories?q={quote(active_search)}&sort=stars").json()
            for item in res.get('items', [])[:5]:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02); padding:15px; border-radius:10px; margin-bottom:10px; border-left: 2px solid #58a6ff;">
                    <div style="color:#58a6ff; font-weight:bold;">{item['full_name']}</div>
                    <div style="font-size:12px; color:#94a3b8;">{item['description'][:100] if item['description'] else 'No description'}</div>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("OPEN CODE", item['html_url'])
        except: st.error("API Limit reached.")

    with t_ar:
        try:
            ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(active_search)}&max_results=5").text
            root = ET.fromstring(ar_res)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                link = entry.find('{http://www.w3.org/2005/Atom}id').text
                st.markdown(f"<div style='margin-bottom:15px;'><b>• {title}</b></div>", unsafe_allow_html=True)
                st.link_button("READ PAPER", link)
        except: st.error("Database connection error.")
