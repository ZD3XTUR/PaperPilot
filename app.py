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

# --- 3. UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #05070a; font-family: 'Inter', sans-serif; }
    
    .hero-box { padding: 40px 0 5px 0; text-align: center; }
    .hero-title { font-size: 3.5rem; font-weight: 200; color: #ffffff; margin-bottom: 0px; }
    .hero-subtitle { color: #4b5563; font-size: 0.9rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 25px; }

    /* Search Box */
    div[data-baseweb="input"] { background-color: transparent !important; border: none !important; }
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50px !important;
        padding: 18px 25px !important;
        color: white !important;
    }

    /* Trend Buttons Alignment */
    div.stButton > button {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #94a3b8 !important;
        border-radius: 20px !important;
        font-size: 11px !important;
        transition: 0.3s;
    }
    div.stButton > button:hover { border-color: #58a6ff !important; color: white !important; }

    /* Central Intel Card (YouTube & Web) */
    .intel-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 20px;
        text-align: center;
    }
    .intel-title { font-size: 1.2rem; font-weight: bold; margin-bottom: 15px; }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #58a6ff;'>HUB</h2>", unsafe_allow_html=True)
    tabs = st.tabs(["📜", "⭐", "📚"])
    # (Sidebardaki tarihçe/kütüphane mantığı aynı)

# --- 5. MAIN CONTENT ---
st.markdown('<div class="hero-box"><div class="hero-title">Research Pilot</div><div class="hero-subtitle">The Intelligence Engine</div></div>', unsafe_allow_html=True)

col_l, col_m, col_r = st.columns([0.2, 0.6, 0.2])
with col_m:
    # Arama Girişi
    main_query = st.text_input("", value=st.session_state.search_query, placeholder="Search intelligence...", label_visibility="collapsed")
    
    # --- TREND KEYWORDS (YAN YANA) ---
    t_cols = st.columns(5)
    trends = ["AI Agents", "Quantum", "BioTech", "SpaceX", "Solana"]
    for i, t in enumerate(trends):
        if t_cols[i].button(t, key=f"tr_{i}", use_container_width=True):
            st.session_state.search_query = t
            st.rerun()

# --- 6. SEARCH LOGIC ---
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    t_web, t_yt, t_gh, t_ar = st.tabs(["🌐 WEB", "🎥 YOUTUBE", "🐙 CODE", "📄 ACADEMIC"])

    with t_web:
        st.markdown(f"""
            <div class="intel-card">
                <div class="intel-title" style="color:#58a6ff;">Google Search Index</div>
                <p style="color:#94a3b8; margin-bottom:20px;">Deep scan for <b>{active_search}</b> across the global web.</p>
                <a href="https://www.google.com/search?q={quote(active_search)}" target="_blank" style="text-decoration:none;">
                    <button style="background:#58a6ff; color:black; border:none; padding:12px 30px; border-radius:30px; font-weight:bold; cursor:pointer;">
                        LAUNCH WEB SCAN ↗
                    </button>
                </a>
            </div>
        """, unsafe_allow_html=True)

    with t_yt:
        # İSTEDİĞİN SADE YÖNLENDİRME YAPISI
        yt_url = f"https://www.youtube.com/results?search_query={quote(active_search)}"
        st.markdown(f"""
            <div class="intel-card" style="border-color: #ff000033;">
                <div class="intel-title" style="color:#ff0000;">YouTube Video Archive</div>
                <p style="color:#94a3b8; margin-bottom:20px;">Accessing visual briefings, lectures and seminars for <b>{active_search}</b>.</p>
                <a href="{yt_url}" target="_blank" style="text-decoration:none;">
                    <button style="background:#ff0000; color:white; border:none; padding:12px 30px; border-radius:30px; font-weight:bold; cursor:pointer;">
                        OPEN IN YOUTUBE 🎥
                    </button>
                </a>
            </div>
        """, unsafe_allow_html=True)

    with t_gh:
        # GitHub Repo Listeleme...
        st.info(f"{active_search} için kod depoları aranıyor...")

    with t_ar:
        # Akademik Makale Listeleme...
        st.info(f"{active_search} için akademik veriler taranıyor...")
