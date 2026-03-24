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
    .hero-title { font-size: 3.5rem; font-weight: 200; color: #ffffff; }
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
    }

    /* Intel Card */
    .intel-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 15px;
    }
    .intel-title { font-size: 1.1rem; font-weight: bold; color: #58a6ff; margin-bottom: 8px; }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #58a6ff;'>HUB</h2>", unsafe_allow_html=True)
    tabs = st.tabs(["📜", "⭐", "📚"])
    with tabs[0]:
        for h in reversed(st.session_state.history[-10:]):
            if st.button(f"🔍 {h}", key=f"hist_{h}", use_container_width=True):
                st.session_state.search_query = h; st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown('<div class="hero-box"><div class="hero-title">Research Pilot</div><div class="hero-subtitle">The Intelligence Engine</div></div>', unsafe_allow_html=True)

_, col_m, _ = st.columns([0.2, 0.6, 0.2])
with col_m:
    main_query = st.text_input("", value=st.session_state.search_query, placeholder="Search intelligence...", label_visibility="collapsed")
    
    # TREND KEYWORDS (YAN YANA)
    t_cols = st.columns(5)
    trends = ["AI Agents", "Quantum", "BioTech", "SpaceX", "Solana"]
    for i, t in enumerate(trends):
        if t_cols[i].button(t, key=f"tr_{i}", use_container_width=True):
            st.session_state.search_query = t; st.rerun()

# --- 6. SEARCH LOGIC ---
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    t_web, t_yt, t_gh, t_ar = st.tabs(["🌐 WEB", "🎥 YOUTUBE", "🐙 CODE", "📄 ACADEMIC"])

    with t_web:
        st.markdown(f'<div class="intel-card"><div class="intel-title">Google Index</div><a href="https://www.google.com/search?q={quote(active_search)}" target="_blank"><button style="background:#58a6ff; border:none; padding:10px 20px; border-radius:20px; cursor:pointer; font-weight:bold;">LAUNCH SCAN ↗</button></a></div>', unsafe_allow_html=True)

    with t_yt:
        yt_url = f"https://www.youtube.com/results?search_query={quote(active_search)}"
        st.markdown(f"""
            <div class="intel-card" style="border-color: #ff000033; text-align:center;">
                <div class="intel-title" style="color:#ff0000;">YouTube Video Archive</div>
                <p style="color:#94a3b8;">Searching video briefings for <b>{active_search}</b>.</p>
                <a href="{yt_url}" target="_blank" style="text-decoration:none;">
                    <button style="background:#ff0000; color:white; border:none; padding:12px 30px; border-radius:30px; font-weight:bold; cursor:pointer;">OPEN IN YOUTUBE 🎥</button>
                </a>
            </div>
        """, unsafe_allow_html=True)

    with t_gh:
        try:
            res = requests.get(f"https://api.github.com/search/repositories?q={quote(active_search)}&sort=stars").json()
            for item in res.get('items', [])[:5]:
                st.markdown(f'<div class="intel-card"><div class="intel-title">{item["full_name"]}</div><span style="color:#94a3b8; font-size:12px;">⭐ {item["stargazers_count"]} stars</span></div>', unsafe_allow_html=True)
                st.link_button("VIEW CODE", item['html_url'])
        except: st.error("GitHub Error.")

    with t_ar:
        try:
            # Burası artık "taranıyor" demiyor, gerçekten tıyor!
            ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(active_search)}&max_results=5").text
            root = ET.fromstring(ar_res)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                link = entry.find('{http://www.w3.org/2005/Atom}id').text
                st.markdown(f'<div class="intel-card"><div class="intel-title">{title}</div></div>', unsafe_allow_html=True)
                st.link_button("READ PAPER", link)
        except: st.error("Academic Archive Error.")
