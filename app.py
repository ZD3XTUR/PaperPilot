import streamlit as st
import requests
import xml.etree.ElementTree as ET
from googlesearch import search as google_search

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Research-Pilot", page_icon="🚀", layout="wide")

# --- UI HEADER ---
st.title("🚀 Research-Pilot: All-in-One Search")
st.markdown("Search across **Google**, **GitHub**, and **Academic Papers** simultaneously.")

# --- SEARCH INPUT ---
query = st.text_input("What are you researching today?", placeholder="e.g. Quantum Computing")

if query:
    with st.spinner('Gathering information from the web...'):
        # Create tabs for different search sources
        tab1, tab2, tab3 = st.tabs(["🌐 Google", "🐙 GitHub", "📄 ArXiv"])

        # --- GOOGLE WEB SEARCH SECTION ---
        with tab1:
            st.subheader("Web Results from Google")
            try:
                # Fetching top 5 results from Google
                for url in google_search(query, num_results=5):
                    st.write(f"🔗 [Visit Link]({url})")
                    st.caption(f"Source: {url.split('/')[2]}")
                    st.divider()
            except Exception as e:
                st.error("Google search is temporarily unavailable. Please try again later.")

        # --- GITHUB REPOSITORY SECTION ---
        with tab2:
            st.subheader("Open Source Projects on GitHub")
            github_api_url = f"https://api.github.com/search/repositories?q={query}&sort=stars"
            try:
                response = requests.get(github_api_url).json()
                for item in response.get('items', [])[:5]:
                    # Display repository info in an expander for a clean UI
                    with st.expander(f"⭐ {item['stargazers_count']} | {item['full_name']}"):
                        st.write(item['description'] if item['description'] else "No description provided.")
                        st.link_button("View Repository", item['html_url'])
            except Exception as e:
                st.error("Could not fetch data from GitHub API.")

        # --- ARXIV ACADEMIC PAPERS SECTION ---
        with tab3:
            st.subheader("Academic Research Papers")
            arxiv_api_url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results=5"
            try:
                response = requests.get(arxiv_api_url).text
                root = ET.fromstring(response)
                # Parse XML response from ArXiv
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    paper_title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                    paper_link = entry.find('{http://www.w3.org/2005/Atom}id').text
                    st.info(f"**{paper_title}**")
                    st.write(f"[Read Full Paper]({paper_link})")
                    st.divider()
            except Exception as e:
                st.error("Could not fetch data from ArXiv API.")

    # Success effect when search is complete
    st.balloons()
