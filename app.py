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

# --- 3. UI STYLING (Dokunulmadı) ---
st.markdown("""
    <style>
    .stApp { background: #05070a; font-family: 'Inter', sans-serif; }
    .hero-box { padding: 30px 0 5px 0; text-align: center; }
    .hero-title { font-size: 3.2rem; font-weight: 200; color: #ffffff; }
    div.stButton > button {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #94a3b8 !important;
        border-radius: 20px !important;
    }
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

# --- 4. API FUNCTIONS (CACHED - Hataları Önleyen Kısım) ---
@st.cache_data(ttl=600) # Veriyi 10 dakika hafızada tutar, butona basınca hata vermez
def fetch_github(query):
    try:
        headers = {'User-Agent': 'ResearchPilot-App'}
        res = requests.get(f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars", headers=headers, timeout=10)
        return res.json().get('items', [])[:5] if res.status_code == 200 else []
    except: return []

@st.cache_data(ttl=600)
def fetch_arxiv(query):
    try:
        res = requests.get(f"https://export.arxiv.org/api/query?search_query=all:{quote(query)}&max_results=5", timeout=10).text
        root = ET.fromstring(res)
        results = []
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            results.append({
                'title': entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ''),
                'link': entry.find('{http://www.w3.org/2005/Atom}id').text
            })
        return results
    except: return []

# --- 5. SIDEBAR (HUB - Tüm Butonlar Aktif) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #58a6ff;'>HUB</h2>", unsafe_allow_html=True)
    tab_hist, tab_fav, tab_read = st.tabs(["📜", "⭐", "📚"])
    
    with tab_hist:
        if st.session_state.history:
            if st.button("🗑️ PURGE HISTORY", use_container_width=True):
                st.session_state.history = []; st.session_state.search_query = ""; st.rerun()
            for h in reversed(st.session_state.history[-10:]):
                if st.button(f"🔍 {h}", key=f"h_btn_{h}", use_container_width=True):
                    st.session_state.search_query = h; st.rerun()
                
    with tab_fav:
        for idx, item in enumerate(st.session_state.library):
            c1, c2 = st.columns([0.8, 0.2])
            c1.markdown(f"<small>[{item['title'][:20]}...]({item['link']})</small>", unsafe_allow_html=True)
            if c2.button("✖", key=f"fav_del_{idx}"):
                st.session_state.library.pop(idx); st.rerun()

    with tab_read:
        for idx, p in enumerate(st.session_state.reading_list):
            c1, c2 = st.columns([0.8, 0.2])
            c1.markdown(f"<small>📖 {p['title'][:20]}...</small>", unsafe_allow_html=True)
            if c2.button("✔", key=f"read_done_{idx}"):
                st.session_state.reading_list.pop(idx); st.rerun()

# --- 6. MAIN CONTENT ---
st.markdown('<div class="hero-box"><div class="hero-title">Research Pilot</div></div>', unsafe_allow_html=True)

_, col_m, _ = st.columns([0.15, 0.7, 0.15])
with col_m:
    main_query = st.text_input("", value=st.session_state.search_query, placeholder="Search intelligence...", label_visibility="collapsed")
    t_cols = st.columns(5)
    trends = ["AI Agents", "Quantum", "BioTech", "SpaceX", "Solana"]
    for i, t in enumerate(trends):
        if t_cols[i].button(t, key=f"t_btn_{i}", use_container_width=True):
            st.session_state.search_query = t; st.rerun()

# --- 7. SEARCH LOGIC ---
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    t_web, t_yt, t_gh, t_ar = st.tabs(["🌐 WEB", "🎥 YOUTUBE", "🐙 CODE", "📄 ACADEMIC"])

    with t_web:
        st.markdown(f'<div class="intel-card"><div class="intel-title">Google Search</div><a href="https://www.google.com/search?q={quote(active_search)}" target="_blank"><button style="background:#58a6ff; border:none; padding:10px 25px; border-radius:25px; cursor:pointer; font-weight:bold;">SCAN WEB ↗</button></a></div>', unsafe_allow_html=True)

    with t_yt:
        yt_url = f"https://www.youtube.com/results?search_query={quote(active_search)}"
        st.markdown(f'<div class="intel-card" style="text-align:center;"><div class="intel-title" style="color:#ff0000;">YouTube Archive</div><a href="{yt_url}" target="_blank"><button style="background:#ff0000; color:white; border:none; padding:15px 40px; border-radius:30px; font-weight:bold; cursor:pointer;">OPEN IN YOUTUBE 🎥</button></a></div>', unsafe_allow_html=True)

    with t_gh:
        gh_data = fetch_github(active_search)
        if gh_data:
            for item in gh_data:
                st.markdown(f'<div class="intel-card"><div class="intel-title">{item["full_name"]}</div><p style="color:#94a3b8; font-size:11px;">⭐ {item["stargazers_count"]}</p></div>', unsafe_allow_html=True)
                c1, c2, c3, _ = st.columns([0.1, 0.1, 0.1, 0.7])
                with c1: st.link_button("👁️", item['html_url'])
                with c2: 
                    if st.button("📚", key=f"gh_r_{item['id']}"): 
                        st.session_state.reading_list.append({"title": item['full_name'], "link": item['html_url']}); st.rerun()
                with c3:
                    if st.button("⭐", key=f"gh_f_{item['id']}"): 
                        st.session_state.library.append({"title": item['full_name'], "link": item['html_url']}); st.rerun()
        else: st.info("No GitHub data available or limit reached.")

    with t_ar:
        ar_data = fetch_arxiv(active_search)
        if ar_data:
            for item in ar_data:
                st.markdown(f'<div class="intel-card"><div class="intel-title">{item["title"]}</div></div>', unsafe_allow_html=True)
                c1, c2, c3, _ = st.columns([0.1, 0.1, 0.1, 0.7])
                with c1: st.link_button("👁️", item['link'])
                with c2:
                    if st.button("📚", key=f"ar_r_{item['link'][-10:]}"): 
                        st.session_state.reading_list.append({"title": item['title'], "link": item['link']}); st.rerun()
                with c3:
                    if st.button("⭐", key=f"ar_f_{item['link'][-10:]}"): 
                        st.session_state.library.append({"title": item['title'], "link": item['link']}); st.rerun()
        else: st.info("No ArXiv papers found.")
