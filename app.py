import streamlit as st
import requests
import xml.etree.Tree as ET
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
    /* Global Background */
    .stApp { 
        background: #05070a; 
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Section */
    .hero-box {
        padding: 50px 0 10px 0;
        text-align: center;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 200;
        letter-spacing: -1px;
        color: #ffffff;
    }
    .hero-subtitle {
        color: #4b5563;
        font-size: 0.9rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 30px;
    }

    /* THE SEARCH BOX FIX: Pure Single Layer */
    /* Dıştaki kapsayıcıyı temizle */
    div[data-baseweb="input"] {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Gerçek giriş kutusunu tek renk ve düz yap */
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50px !important;
        padding: 20px 25px !important;
        color: white !important;
        font-size: 1.1rem !important;
        box-shadow: none !important;
        background-image: none !important;
    }
    
    .stTextInput input:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.1) !important;
    }

    /* Cards */
    .intel-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .intel-title {
        font-size: 1.1rem;
        font-weight: 500;
        color: #58a6ff;
        margin-bottom: 8px;
    }
    .stat-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 100px;
        background: rgba(88, 166, 255, 0.1);
        color: #58a6ff;
        font-size: 10px;
        font-weight: bold;
        margin-right: 5px;
    }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #58a6ff;'>HUB</h2>", unsafe_allow_html=True)
    tabs = st.tabs(["📜", "⭐", "📚"])
    
    with tabs[0]: # History
        if st.session_state.history:
            if st.button("🗑️ PURGE", use_container_width=True):
                st.session_state.history = []
                st.rerun()
            for h in reversed(st.session_state.history[-10:]):
                if st.button(f"🔍 {h}", key=f"hist_{h}", use_container_width=True):
                    st.session_state.search_query = h
                    st.rerun()
    
    with tabs[1]: # Starred
        for idx, item in enumerate(st.session_state.library):
            c1, c2 = st.columns([0.85, 0.15])
            c1.markdown(f"**[{item['title'][:25]}...]({item['link']})**")
            if c2.button("✖️", key=f"lib_rm_{idx}"):
                st.session_state.library.pop(idx); st.rerun()

    with tabs[2]: # Reading List
        for idx, p in enumerate(st.session_state.reading_list):
            if st.button(f"✔️ {p['title'][:30]}...", key=f"rd_f_{idx}", use_container_width=True):
                st.session_state.reading_list.pop(idx); st.rerun()

# --- 5. MAIN CONTENT ---
st.markdown('<div class="hero-box"><div class="hero-title">Research Pilot</div><div class="hero-subtitle">The Intelligence Layer</div></div>', unsafe_allow_html=True)

col_l, col_m, col_r = st.columns([0.2, 0.6, 0.2])
with col_m:
    main_query = st.text_input(
        "", 
        value=st.session_state.search_query,
        placeholder="Search global intelligence...",
        label_visibility="collapsed"
    )

# Trending / Quick Access
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
tr_cols = st.columns([0.35, 0.07, 0.07, 0.07, 0.07, 0.37])
trends = ["LLM", "SpaceX", "BioTech", "DeFi"]
for i, t in enumerate(trends):
    if tr_cols[i+1].button(t, key=f"tr_{i}"):
        st.session_state.search_query = t
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# --- 6. SEARCH LOGIC ---
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    t_web, t_gh, t_ar = st.tabs(["🌐 WEB", "🐙 CODE", "📄 ACADEMIC"])

    with t_web:
        google_url = f"https://www.google.com/search?q={quote(active_search)}"
        st.markdown(f"""
            <div class="intel-card">
                <div class="intel-title">Live Web Index: {active_search}</div>
                <p style="color:#94a3b8; font-size:14px;">External search for real-time news and global web updates.</p>
                <a href="{google_url}" target="_blank" style="text-decoration:none;">
                    <button style="background:#58a6ff; color:black; border:none; padding:8px 15px; border-radius:20px; font-weight:bold; cursor:pointer;">
                        Launch Search ↗
                    </button>
                </a>
            </div>
        """, unsafe_allow_html=True)

    with t_gh:
        try:
            res = requests.get(f"https://api.github.com/search/repositories?q={quote(active_search)}&sort=stars", timeout=10).json()
            for item in res.get('items', [])[:5]:
                st.markdown(f'<div class="intel-card"><div class="intel-title">{item["full_name"]}</div><p style="color:#94a3b8; font-size:13px;">{item["description"]}</p></div>', unsafe_allow_html=True)
                i1, i2, i3, _ = st.columns([0.05, 0.05, 0.05, 0.85])
                with i1: st.link_button("👁️", item['html_url'])
                with i2: 
                    if st.button("📚", key=f"r_gh_{item['id']}"):
                        st.session_state.reading_list.append({"title": item['full_name'], "link": item['html_url']})
                with i3:
                    if st.button("⭐", key=f"s_gh_{item['id']}"):
                        st.session_state.library.append({"title": item['full_name'], "link": item['html_url']})
        except: st.error("GitHub API busy.")

    with t_ar:
        try:
            ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(active_search)}&max_results=5", timeout=10).text
            import xml.etree.ElementTree as ET_mod
            root = ET_mod.fromstring(ar_res)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                l = entry.find('{http://www.w3.org/2005/Atom}id').text
                st.markdown(f'<div class="intel-card"><div class="intel-title">{t}</div><span class="stat-pill">ArXiv Paper</span></div>', unsafe_allow_html=True)
                i1, i2, i3, _ = st.columns([0.05, 0.05, 0.05, 0.85])
                with i1: st.link_button("👁️", l)
                with i2:
                    if st.button("📚", key=f"r_ar_{l}"):
                        st.session_state.reading_list.append({"title": t, "link": l})
                with i3:
                    if st.button("⭐", key=f"s_ar_{l}"):
                        st.session_state.library.append({"title": t, "link": l})
        except: st.error("Academic database unreachable.")
