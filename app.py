import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import quote

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Research-Pilot Pro", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE (Hafıza Yönetimi) ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'library' not in st.session_state:
    st.session_state.library = []
if 'reading_list' not in st.session_state:
    st.session_state.reading_list = []

# KRİTİK: Arama kutusunu kontrol eden state
if 'main_input' not in st.session_state:
    st.session_state.main_input = ""

# --- 3. DARK MODE & UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .res-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 15px;
    }
    .res-title { color: #58a6ff; font-weight: 600; font-size: 18px; }
    .item-box {
        padding: 10px;
        background: #0d1117;
        border-left: 3px solid #ffaa00;
        margin-bottom: 8px;
        border-radius: 0 5px 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (RESEARCH HUB) ---
with st.sidebar:
    st.title("🛰️ Research Hub")
    
    hub_tab1, hub_tab2, hub_tab3 = st.tabs(["📜 Geçmiş", "⭐ Favoriler", "📚 Okunacaklar"])
    
    with hub_tab1:
        st.write("Tekrar aratmak için tıkla:")
        if not st.session_state.history:
            st.caption("Geçmiş boş.")
        for h_query in reversed(st.session_state.history[-10:]):
            # OTOMATİK ARAMA TETİKLEYİCİ
            if st.button(f"🔍 {h_query}", key=f"btn_{h_query}"):
                st.session_state.main_input = h_query # Input değerini güncelle
                st.rerun() # Sayfayı zorla yenile

    with hub_tab2:
        for item in st.session_state.library:
            st.markdown(f'<div class="item-box" style="border-left-color:#3fb950;"><b>{item["title"][:40]}...</b><br><a href="{item["link"]}" target="_blank" style="color:#58a6ff; font-size:11px;">Aç ↗</a></div>', unsafe_allow_html=True)

    with hub_tab3:
        for idx, paper in enumerate(st.session_state.reading_list):
            st.markdown(f'<div class="item-box"><b>{paper["title"][:40]}...</b></div>', unsafe_allow_html=True)
            if st.button(f"✅ Okundu", key=f"read_{idx}"):
                st.session_state.reading_list.pop(idx)
                st.rerun()

# --- 5. ANA ARAYÜZ ---
st.title("🛰️ Research-Pilot Pro")

# KRİTİK DÜZELTME: value=st.session_state.main_input kullanımı
query = st.text_input(
    "Küresel Arama", 
    value=st.session_state.main_input, 
    placeholder="Araştırma konunuzu girin...",
    key="search_widget" # Widget'ın kendi iç key'i
)

# Eğer kullanıcı kutuya elle bir şey yazarsa state'i güncelle
if query != st.session_state.main_input:
    st.session_state.main_input = query

result_count = st.select_slider("**Arama Derinliği**", options=[3, 5, 10, 15], value=5)

# --- 6. ARAMA MANTIĞI ---
if st.session_state.main_input:
    current_search = st.session_state.main_input
    
    # Geçmişe ekle
    if current_search not in st.session_state.history:
        st.session_state.history.append(current_search)

    with st.spinner(f'"{current_search}" taranıyor...'):
        tab1, tab2, tab3 = st.tabs(["🌐 Web", "🐙 GitHub", "📄 Akademik"])

        # Örnek ArXiv Arama (Okuma Listesi Fonksiyonlu)
        with tab3:
            ar_url = f"http://export.arxiv.org/api/query?search_query=all:{quote(current_search)}&max_results={result_count}"
            try:
                response = requests.get(ar_url, timeout=10).text
                root = ET.fromstring(response)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    t = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                    l = entry.find('{http://www.w3.org/2005/Atom}id').text
                    
                    st.markdown(f'<div class="res-card"><div class="res-title">{t[:100]}...</div></div>', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"⭐ Favori", key=f"f_{l}"):
                            st.session_state.library.append({"title": t, "link": l})
                            st.toast("Favorilere eklendi!")
                    with c2:
                        if st.button(f"📚 Okunacaklar", key=f"r_{l}"):
                            st.session_state.reading_list.append({"title": t, "link": l})
                            st.toast("Okuma listesine eklendi!")
            except: st.error("Bağlantı hatası.")

    st.balloons()
