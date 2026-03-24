import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot", page_icon="🚀", layout="wide")

# --- UI HEADER ---
st.title("🚀 Research-Pilot: All-in-One Search")
st.markdown("Search across **Google**, **GitHub**, and **Academic Papers** simultaneously.")

# --- SEARCH INPUT ---
query = st.text_input("What are you researching today?", placeholder="e.g. Quantum Computing")

if query:
    # URL encode the query for safe searching
    encoded_query = quote(query)
    
    with st.spinner('Gathering information...'):
        # Create tabs for different search sources
        tab1, tab2, tab3 = st.tabs(["🌐 Google", "🐙 GitHub", "📄 ArXiv"])

        # --- GOOGLE SEARCH SECTION ---
        with tab1:
            st.subheader("Web Search Results")
            st.info(f"Click the link below to see full Google results for your topic.")
            # Direct Google Search Link (Safest method to avoid ModuleNotFoundError)
            google_url = f"https://www.google.com/search?q={encoded_query}"
            st.link_button("🔍 View Results on Google", google_url)
            st.divider()
            st.write("Popular sub-topics often include documentation, news, and tutorials.")

        # --- GITHUB REPOSITORY SECTION ---
        with tab2:
            st.subheader("Open Source Projects on GitHub")
            github_api_url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars"
            try:
                response = requests.get(github_api_url, timeout=10).json()
                items = response.get('items', [])
                if items:
                    for item in items[:5]:
                        with st.expander(f"⭐ {item['stargazers_count']} | {item['full_name']}"):
                            st.write(item['description'] if item['description'] else "No description provided.")
                            st.link_button("View Repository", item['html_url'])
                else:
                    st.warning("No GitHub repositories found for this topic.")
            except:
                st.error("Could not connect to GitHub API.")

        # --- ARXIV ACADEMIC PAPERS SECTION ---
        with tab3:
            st.subheader("Academic Research Papers")
            arxiv_api_url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&max_results=5"
            try:
                response = requests.get(arxiv_api_url, timeout=10).text
                root = ET.fromstring(response)
                entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                if entries:
                    for entry in entries:
                        paper_title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                        paper_link = entry.find('{http://www.w3.org/2005/Atom}id').text
                        st.info(f"**{paper_title}**")
                        st.write(f"[Read Full Paper]({paper_link})")
                        st.divider()
                else:
                    st.warning("No academic papers found on ArXiv.")
            except:
                st.error("Could not connect to ArXiv API.")

    st.balloons()
