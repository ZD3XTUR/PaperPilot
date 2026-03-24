import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import quote

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Research-Pilot Pro", page_icon="🛰️", layout="wide")

# --- 2. SESSION STATE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'library' not in st.session_state: st.session_state.library = []
if 'reading_list' not in st.session_state: st.session_state.reading_list = []
if 'main_input' not in st.session_state: st.session_state.main_input = ""

# --- 3. DARK MODE & UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .res-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
    .res-title { color: #58a6ff; font-weight: 600; font-size: 17px; margin-bottom: 10px; }
    /* Emoji Butonları için Stil */
    div.stButton > button {
        border-radius: 8px;
        padding: 5px 10px;
        background-color: #21262d;
        border: 1px solid #30363d;
        color: white;
    }
    div.stButton > button:hover {
        border-color: #58a6ff;
        background-color: #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛰️ Research Hub")
    tabs = st.tabs(["📜 Geçmiş", "⭐ Yıldızlı", "📚 Okunacak"])
    
    with tabs[0]:
        for h in reversed(st.session_state.history[-10:]):
            if st.button(f"🔍 {h}", key=f"hist_{h}"):
                st.session_state.main_input = h
                st.rerun()
    with tabs[1]:
        for item in st.session_state.library:
            st.caption(f"⭐ {item['title'][:40]}...")
            st.write(f"[Git ↗]({item['link']})")
    with tabs[2]:
        for idx, paper in enumerate(st.session_state.reading_list):
            st.caption(f"📚 {paper['title'][:40]}...")
            if st.button(f"✅ Okundu", key=f"read_done_{idx}"):
                st.session_state.reading_list.pop(idx)
                st.rerun()

# --- 5. ANA EKRAN ---
st.title("🛰️ Research-Pilot")
query = st.text_input("Arama", value=st.session_state.main_input, placeholder="Konu girin...", key="search_bar")

if query != st.session_state.main_input:
    st.session_state.main_input = query

depth = st.select_slider("Arama Derinliği", options=[3, 5, 10, 15], value=5)

# --- 6. ARAMA MANTIĞI ---
if st.session_state.main_input:
    cur = st.session_state.main_input
    if cur not in st.session_state.history: st.session_state.history.append(cur)

    with st.spinner('Taranıyor...'):
        t1, t2, t3 = st.tabs(["🌐 Web", "🐙 GitHub", "📄 Akademik"])

        with t3: # ARXİV BÖLÜMÜ - ÖZEL BUTON SIRALAMASI
            ar_url = f"http://export.arxiv.org/api/query?search_query=all:{quote(cur)}&max_results={depth}"
            try:
                root = ET.fromstring(requests.get(ar_url, timeout=10).text)
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', '')
                    link = entry.find('{http://www.w3.org/2005/Atom}id').text
                    
                    st.markdown(f'<div class="res-card"><div class="res-title">{title[:120]}...</div></div>', unsafe_allow_html=True)
                    
                    # 👁️ Oku | 📚 Okunacaklar | ⭐ Yıldızla (Emoji Sıralaması)
                    c1, c2, c3, c_spacer = st.columns([0.1, 0.1, 0.1, 0.7])
                    
                    with c1: # 👁️ OKU (Linke Git)
                        st.link_button("👁️", link, help="Makaleyi Aç")
                    
                    with c2: # 📚 OKUNACAKLAR LİSTESİNE EKLE
                        if st.button("📚", key=f"read_{link}", help="Okunacaklara Ekle"):
                            if {"title": title, "link": link} not in st.session_state.reading_list:
                                st.session_state.reading_list.append({"title": title, "link": link})
                                st.toast("Okuma listesine eklendi!")
                    
                    with c3: # ⭐ YILDIZLA (FAVORİ)
                        if st.button("⭐", key=f"star_{link}", help="Yıldızla / Favoriye Ekle"):
                            if {"title": title, "link": link} not in st.session_state.library:
                                st.session_state.library.append({"title": title, "link": link})
                                st.toast("Kütüphaneye kaydedildi!")
                                
            except: st.error("Bağlantı hatası.")

    st.balloons()
