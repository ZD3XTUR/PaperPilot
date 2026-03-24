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

# --- 3. THE "SINGLE-LAYER" CSS FIX ---
st.markdown("""
    <style>
    .stApp { background: #05070a; font-family: 'Inter', sans-serif; }
    
    /* 1. Etiket alanını ve boşlukları tamamen yok et (Üst üste binme hissini siler) */
    div[data-testid="stWidgetLabel"] { display: none !important; }
    div[data-baseweb="input"] { background-color: transparent !important; border: none !important; }
    
    /* 2. Arama Kutusu - Saf Tek Katman Tasarımı */
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50px !important;
        padding: 20px 25px !important;
        color: white !important;
        font-size: 1.1rem !important;
        
        /* Her türlü gölge ve tarayıcı efektini sıfırla */
        box-shadow: none !important;
        outline: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
    }

    /* 3. Focus durumunda sadece dış ince bir çizgi kalsın (Çift görüntü oluşmaz) */
    .stTextInput input:focus {
        border: 1px solid #58a6ff !important;
        background-color: #0d1117 !important;
        box-shadow: 0 0 10px rgba(88, 166, 255, 0.2) !important;
    }

    /* Kartlar ve Diğer Tasarım */
    .intel-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
    }
    .hero-box { padding: 50px 0 20px 0; text-align: center; }
    .hero-title { font-size: 3rem; font-weight: 200; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (DEĞİŞMEDİ) ---
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
    # Library ve Reading List kısımları aynı...
    with tabs[1]:
        for idx, item in enumerate(st.session_state.library):
            c_txt, c_rm = st.columns([0.8, 0.2])
            c_txt.markdown(f"**[{item['title'][:30]}...]({item['link']})**")
            if c_rm.button("✖️", key=f"lib_rm_{idx}"): st.session_state.library.pop(idx); st.rerun()
    with tabs[2]:
        for idx, p in enumerate(st.session_state.reading_list):
            if st.button(f"✔️ {p['title'][:35]}...", key=f"rd_fin_{idx}", use_container_width=True):
                st.session_state.reading_list.pop(idx); st.rerun()

# --- 5. ANA EKRAN ---
st.markdown('<div class="hero-box"><div class="hero-title">Research Pilot</div></div>', unsafe_allow_html=True)

c_left, c_mid, c_right = st.columns([0.2, 0.6, 0.2])
with c_mid:
    # Arama kutusu artık tamamen izole edilmiş durumda
    main_query = st.text_input(
        "label_hidden", # İçerideki label'ı da tamamen temizliyoruz
        value=st.session_state.search_query,
        placeholder="Enter keywords...",
        label_visibility="collapsed"
    )

# Arama Mantığı ve Sonuçlar
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    t_web, t_gh, t_ar = st.tabs(["🌐 WEB", "🐙 CODE", "📄 ACADEMIC"])
    
    with t_gh:
        try:
            res = requests.get(f"https://api.github.com/search/repositories?q={quote(active_search)}&sort=stars").json()
            for item in res.get('items', [])[:5]:
                st.markdown(f'<div class="intel-card"><div style="color:#58a6ff; font-weight:bold;">{item["full_name"]}</div><p style="font-size:14px; color:#94a3b8;">{item["description"]}</p></div>', unsafe_allow_html=True)
                i1, i2, i3, _ = st.columns([0.05, 0.05, 0.05, 0.85])
                with i1: st.link_button("👁️", item['html_url'])
                with i2: 
                    if st.button("📚", key=f"r_gh_{item['id']}"): st.session_state.reading_list.append({"title": item['full_name'], "link": item['html_url']})
                with i3:
                    if st.button("⭐", key=f"s_gh_{item['id']}"): st.session_state.library.append({"title": item['full_name'], "link": item['html_url']})
        except: st.error("Search error.")
    
    with t_ar:
        try:
            ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(active_search)}&max_results=5").text
            root = ET.fromstring(ar_res)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                l = entry.find('{http://www.w3.org/2005/Atom}id').text
                st.markdown(f'<div class="intel-card"><div style="color:#58a6ff; font-weight:bold;">{t}</div></div>', unsafe_allow_html=True)
                i1, i2, i3, _ = st.columns([0.05, 0.05, 0.05, 0.85])
                with i1: st.link_button("👁️", l)
                with i2:
                    if st.button("📚", key=f"r_ar_{l}"): st.session_state.reading_list.append({"title": t, "link": l})
                with i3:
                    if st.button("⭐", key=f"s_ar_{l}"): st.session_state.library.append({"title": t, "link": l})
        except: st.error("ArXiv error.")
