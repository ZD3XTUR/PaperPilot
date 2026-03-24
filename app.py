import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
import random

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Research-Pilot Pro", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'search_query' not in st.session_state: st.session_state.search_query = ""

# --- 3. CSS (TASARIM - PÜRÜZSÜZ ÇUBUK VE KARTLAR) ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Hero Section */
    .hero-box { padding: 30px 0 10px 0; text-align: center; }
    .hero-title { font-size: 2.8rem; font-weight: 200; color: #ffffff; margin-bottom: 0px; }
    .hero-subtitle { color: #4b5563; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 20px; }

    /* Arama Kutusu Fix */
    div[data-baseweb="input"] { background-color: transparent !important; border: none !important; }
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50px !important;
        padding: 15px 25px !important;
        color: white !important;
        box-shadow: none !important;
    }

    /* Video Kartı Tasarımı */
    .video-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 15px;
        transition: 0.3s ease;
    }
    .video-card:hover {
        border-color: #ff0000;
        background: rgba(255, 0, 0, 0.05);
        transform: translateY(-3px);
    }
    .video-img {
        width: 100%;
        border-radius: 10px;
        aspect-ratio: 16/9;
        object-fit: cover;
    }
    .video-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #ffffff;
        margin-top: 10px;
        height: 40px;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. YARDIMCI FONKSİYONLAR ---
# Bu fonksiyon, popüler video ID'lerinden rastgele seçerek "canlı yayın" hissi verir
def get_dynamic_thumb(index):
    # Örnek popüler eğitim/teknoloji video ID'leri
    sample_ids = ["d7_E0Lp6wS8", "C_vIuW8NkhM", "l9AZ0068p2s", "m8_D8eE7YcE", "7p_VvA1pD0Y", "k5Vn_v8p9Yw"]
    video_id = sample_ids[index % len(sample_ids)]
    return f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"

# --- 5. ANA EKRAN ---
st.markdown('<div class="hero-box"><div class="hero-title">Research Pilot</div><div class="hero-subtitle">Visual Intelligence Station</div></div>', unsafe_allow_html=True)

_, col_m, _ = st.columns([0.15, 0.7, 0.15])
with col_m:
    main_query = st.text_input("", value=st.session_state.search_query, placeholder="Search videos and data...", label_visibility="collapsed")
    
    # TRENDLER (Geri Geldi)
    t_cols = st.columns([0.2, 0.15, 0.15, 0.15, 0.15, 0.2])
    trends = ["Python AI", "SpaceX", "Solana", "Web3"]
    for i, t in enumerate(trends):
        if t_cols[i+1].button(t, key=f"trend_{i}"):
            st.session_state.search_query = t
            st.rerun()

# --- 6. ARAMA MANTIĞI ---
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    t_yt, t_gh, t_ar = st.tabs(["🎥 YOUTUBE LIVE", "🐙 GITHUB", "📄 ACADEMIC"])

    with t_yt:
        st.markdown(f"#### Results for: `{active_search}`")
        v_cols = st.columns(3)
        yt_link = f"https://www.youtube.com/results?search_query={quote(active_search)}"
        
        for i in range(6):
            with v_cols[i % 3]:
                # Görseli index'e göre dinamikleştiriyoruz
                thumb_url = get_dynamic_thumb(i + len(active_search)) 
                
                st.markdown(f"""
                <div class="video-card">
                    <img src="{thumb_url}" class="video-img">
                    <div class="video-title">{active_search.upper()} - Intelligence Report #{i+1}</div>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("WATCH VIDEO", yt_link, use_container_width=True)

    with t_gh:
        # Önceki GitHub kodu...
        st.info(f"{active_search} için kod depoları taranıyor...")

    with t_ar:
        # Önceki Akademik kod...
        st.info(f"{active_search} için makaleler listeleniyor...")
