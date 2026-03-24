import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot Ultra", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE INITIALIZATION ---
# Bu kısım hatayı önlemek için kritik:
if 'history' not in st.session_state: st.session_state.history = []
if 'library' not in st.session_state: st.session_state.library = []
if 'reading_list' not in st.session_state: st.session_state.reading_list = []
# Widget'ın değerini tutacak ana state
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# --- 3. UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #020617 100%); color: #e2e8f0; }
    .hero-container {
        padding: 40px; text-align: center; background: rgba(30, 41, 59, 0.4);
        border-radius: 20px; border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 30px;
    }
    .hero-title {
        font-size: 3rem; font-weight: 800;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stat-card {
        background: rgba(15, 23, 42, 0.8); border-left: 3px solid #38bdf8;
        padding: 15px; border-radius: 10px; text-align: center;
    }
    .res-card {
        background: rgba(30, 41, 59, 0.5); backdrop-filter: blur(12px);
        padding: 20px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { font-size: 22px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR LOGIC ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #38bdf8;'>HUB</h2>", unsafe_allow_html=True)
    tabs = st.tabs(["📜", "⭐", "📚"])
    
    with tabs[0]: # HISTORY
        if st.session_state.history:
            if st.button("🗑️ PURGE", use_container_width=True):
                st.session_state.history = []
                st.rerun()
            for h in reversed(st.session_state.history[-10:]):
                # HATA ÇÖZÜMÜ: Callback yerine state'i doğrudan güncelleyip rerun yapıyoruz
                if st.button(f"🔍 {h}", key=f"hist_{h}", use_container_width=True):
                    st.session_state.search_query = h
                    st.rerun()

    with tabs[1]: # LIBRARY
        for idx, item in enumerate(st.session_state.library):
            c_txt, c_rm = st.columns([0.8, 0.2])
            c_txt.markdown(f"**[{item['title'][:30]}...]({item['link']})**")
            if c_rm.button("✖️", key=f"lib_rm_{idx}"):
                st.session_state.library.pop(idx); st.rerun()

    with tabs[2]: # READING
        for idx, p in enumerate(st.session_state.reading_list):
            if st.button(f"✔️ {p['title'][:35]}...", key=f"rd_fin_{idx}", use_container_width=True):
                st.session_state.reading_list.pop(idx); st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown('<div class="hero-container"><div class="hero-title">RESEARCH PILOT</div><p style="color: #94a3b8;">Unified Intelligence Engine</p></div>', unsafe_allow_html=True)

# STATS
s1, s2, s3, s4 = st.columns(4)
s1.markdown(f'<div class="stat-card"><small>HISTORY</small><h4>{len(st.session_state.history)}</h4></div>', unsafe_allow_html=True)
s2.markdown(f'<div class="stat-card"><small>LIBRARY</small><h4>{len(st.session_state.library)}</h4></div>', unsafe_allow_html=True)
s3.markdown(f'<div class="stat-card"><small>QUEUED</small><h4>{len(st.session_state.reading_list)}</h4></div>', unsafe_allow_html=True)
s4.markdown(f'<div class="stat-card"><small>STATUS</small><h4 style="color:#3fb950;">ONLINE</h4></div>', unsafe_allow_html=True)

st.divider()

# SEARCH INPUT - value=st.session_state.search_query kullanımı hatayı çözer
main_query = st.text_input(
    "GLOBAL SEARCH", 
    value=st.session_state.search_query,
    placeholder="Enter keywords...",
    key="main_search_input"
)

# TRENDING CHIPS
st.markdown("<small style='color:#64748b;'>TRENDING:</small>", unsafe_allow_html=True)
t_cols = st.columns(5)
trends = ["Quantum AI", "Rust Frameworks", "Cyber Security", "Neural Networks", "DeFi"]
for i, t in enumerate(trends):
    if t_cols[i].button(t, key=f"trend_{i}"):
        st.session_state.search_query = t
        st.rerun()

# --- 6. SEARCH LOGIC ---
# Arama yaparken session state'deki değeri kullanıyoruz
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    with st.spinner('🔭 Scanning...'):
        tab_web, tab_gh, tab_ar = st.tabs(["🌐 WEB", "🐙 GITHUB", "📄 ARXIV"])

        # GITHUB
        with tab_gh:
            try:
                res = requests.get(f"https://api.github.com/search/repositories?q={quote(active_search)}&sort=stars").json()
                for item in res.get('items', [])[:5]:
                    st.markdown(f'<div class="res-card"><b style="color:#38bdf8;">{item["full_name"]}</b><br><small>{item["description"]}</small></div>', unsafe_allow_html=True)
                    btn_c1, btn_c2, btn_c3, _ = st.columns([0.15, 0.1, 0.1, 0.65])
                    with btn_c1: st.link_button("VIEW", item['html_url'])
                    with btn_c2: 
                        if st.button("📚", key=f"r_gh_{item['id']}"):
                            st.session_state.reading_list.append({"title": item['full_name'], "link": item['html_url']})
                    with btn_c3:
                        if st.button("⭐", key=f"s_gh_{item['id']}"):
                            st.session_state.library.append({"title": item['full_name'], "link": item['html_url']})
            except: st.error("GitHub link error.")

        # ARXIV
        with tab_ar:
            try:
                ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(active_search)}&max_results=5").text
                root = ET.fromstring(ar_res)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                    l = entry.find('{http://www.w3.org/2005/Atom}id').text
                    st.markdown(f'<div class="res-card"><b style="color:#38bdf8;">{t}</b></div>', unsafe_allow_html=True)
                    bc1, bc2, bc3, _ = st.columns([0.15, 0.1, 0.1, 0.65])
                    with bc1: st.link_button("READ", l)
                    with bc2:
                        if st.button("📚", key=f"r_ar_{l}"):
                            st.session_state.reading_list.append({"title": t, "link": l})
                    with bc3:
                        if st.button("⭐", key=f"s_ar_{l}"):
                            st.session_state.library.append({"title": t, "link": l})
            except: st.error("Database error.")

    st.balloons()
