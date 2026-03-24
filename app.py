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

# --- 3. ZEN & FUTURISTIC UI STYLING (WITH FLAT SEARCH BOX) ---
st.markdown("""
    <style>
    /* Global Background & Font */
    .stApp { 
        background: #05070a; 
        font-family: 'Inter', sans-serif;
    }
    
    /* Minimalist Hero Section */
    .hero-box {
        padding: 60px 0 20px 0;
        text-align: center;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 200;
        letter-spacing: -1px;
        color: #ffffff;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        color: #4b5563;
        font-size: 1rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 40px;
    }

    /* CRITICAL FIX: Clean, Flat, Single-Color Search Input */
    .stTextInput input {
        background-color: #0d1117 !important; /* Single Solid Dark Color */
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50px !important;
        padding: 25px 30px !important;
        color: white !important;
        font-size: 1.2rem !important;
        
        /* Remove ALL shadows, gradients, and internal styling */
        box-shadow: none !important;
        background-image: none !important;
        -webkit-appearance: none !important;
        -moz-appearance: none !important;
        appearance: none !important;
        
        transition: 0.4s;
    }
    
    /* Input Focus State - Smooth Glow */
    .stTextInput input:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 20px rgba(88, 166, 255, 0.15) !important;
        background-color: #0d1117 !important; /* Keep Single Color */
    }

    /* Result Cards (Minimalist) */
    .intel-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .intel-card:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(88, 166, 255, 0.3);
    }
    .intel-title {
        font-size: 1.25rem;
        font-weight: 500;
        color: #58a6ff;
        margin-bottom: 10px;
    }

    /* Quick Stats Labels */
    .stat-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 100px;
        background: rgba(88, 166, 255, 0.1);
        color: #58a6ff;
        font-size: 11px;
        font-weight: bold;
        margin-right: 8px;
    }

    /* Hide default streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (STAYS THE SAME AS REQUESTED) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #58a6ff;'>HUB</h2>", unsafe_allow_html=True)
    tabs = st.tabs(["📜", "⭐", "📚"])
    with tabs[0]:
        if st.session_state.history:
            if st.button("🗑️ PURGE", use_container_width=True):
                st.session_state.history = []
                st.rerun()
            for h in reversed(st.session_state.history[-10:]):
                if st.button(f"🔍 {h}", key=f"hist_{h}", use_container_width=True):
                    st.session_state.search_query = h
                    st.rerun()
    with tabs[1]:
        for idx, item in enumerate(st.session_state.library):
            c_txt, c_rm = st.columns([0.8, 0.2])
            c_txt.markdown(f"**[{item['title'][:30]}...]({item['link']})**")
            if c_rm.button("✖️", key=f"lib_rm_{idx}"):
                st.session_state.library.pop(idx); st.rerun()
    with tabs[2]:
        for idx, p in enumerate(st.session_state.reading_list):
            if st.button(f"✔️ {p['title'][:35]}...", key=f"rd_fin_{idx}", use_container_width=True):
                st.session_state.reading_list.pop(idx); st.rerun()

# --- 5. ZEN MAIN SCREEN ---
st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Research Pilot</div>
        <div class="hero-subtitle">The Intelligence Layer</div>
    </div>
    """, unsafe_allow_html=True)

# Central Search Container
c_left, c_mid, c_right = st.columns([0.15, 0.7, 0.15])
with c_mid:
    main_query = st.text_input(
        "", 
        value=st.session_state.search_query,
        placeholder="Search repositories, archives, or web nodes...",
        label_visibility="collapsed"
    )

# Quick Access / Suggestions (More elegant)
st.markdown("<div style='text-align:center; margin-top:10px;'>", unsafe_allow_html=True)
s_cols = st.columns([0.3, 0.1, 0.1, 0.1, 0.1, 0.3])
trends = ["LLMs", "BioTech", "SpaceX", "Solana"]
for i, t in enumerate(trends):
    if s_cols[i+1].button(t, key=f"t_{i}"):
        st.session_state.search_query = t
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# --- 6. SEARCH LOGIC ---
active_search = main_query if main_query else st.session_state.search_query

if active_search:
    if active_search not in st.session_state.history:
        st.session_state.history.append(active_search)

    st.markdown(f"<p style='text-align:center; color:#4b5563; margin-top:30px;'>Displaying results for: <b>{active_search}</b></p>", unsafe_allow_html=True)
    
    # Modern Tabs
    t_web, t_gh, t_ar = st.tabs(["WEB", "CODE", "ACADEMIC"])

    with t_gh:
        try:
            res = requests.get(f"https://api.github.com/search/repositories?q={quote(active_search)}&sort=stars").json()
            for item in res.get('items', [])[:5]:
                st.markdown(f"""
                    <div class="intel-card">
                        <div class="intel-title">{item['full_name']}</div>
                        <p style="color:#94a3b8; font-size:14px;">{item['description'] or 'No description logs.'}</p>
                        <span class="stat-pill">⭐ {item['stargazers_count']}</span>
                        <span class="stat-pill">🛠️ {item['language']}</span>
                    </div>
                """, unsafe_allow_html=True)
                # Icons Only Row
                i1, i2, i3, _ = st.columns([0.05, 0.05, 0.05, 0.85])
                with i1: st.link_button("👁️", item['html_url'])
                with i2: 
                    if st.button("📚", key=f"r_gh_{item['id']}"):
                        st.session_state.reading_list.append({"title": item['full_name'], "link": item['html_url']})
                with i3:
                    if st.button("⭐", key=f"s_gh_{item['id']}"):
                        st.session_state.library.append({"title": item['full_name'], "link": item['html_url']})
        except: st.error("Link unstable.")

    with t_ar:
        try:
            ar_res = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{quote(active_search)}&max_results=5").text
            root = ET.fromstring(ar_res)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                l = entry.find('{http://www.w3.org/2005/Atom}id').text
                st.markdown(f"""
                    <div class="intel-card">
                        <div class="intel-title">{t}</div>
                        <span class="stat-pill">PDF AVAILABLE</span>
                    </div>
                """, unsafe_allow_html=True)
                i1, i2, i3, _ = st.columns([0.05, 0.05, 0.05, 0.85])
                with i1: st.link_button("👁️", l)
                with i2:
                    if st.button("📚", key=f"r_ar_{l}"):
                        st.session_state.reading_list.append({"title": t, "link": l})
                with i3:
                    if st.button("⭐", key=f"s_ar_{l}"):
                        st.session_state.library.append({"title": t, "link": l})
        except: st.error("Archive unreachable.")

    st.success(f"Analysis complete for {active_search}.")
