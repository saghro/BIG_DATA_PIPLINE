import streamlit as st
import pandas as pd
from cassandra.cluster import Cluster
import time
import altair as alt
import re

# Page Config
st.set_page_config(
    page_title="Mastodon Crypto Monitor",
    page_icon="🐘",
    layout="wide"
)

# Connect to Cassandra
@st.cache_resource
def get_session():
    import socket
    
    # Vérifier d'abord si le port est accessible
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', 9042))
    sock.close()
    
    if result != 0:
        return None
    
    try:
        cluster = Cluster(['127.0.0.1'], port=9042, connect_timeout=5)
        session = cluster.connect('reddit_keyspace')
        return session
    except Exception as e:
        return None

session = get_session()
if session is None:
    st.error("""
    ⚠️ **Impossible de se connecter à Cassandra**
    
    **Vérifications :**
    
    1. Démarrer l'infrastructure :
       ```bash
       cd /Users/a/Projet_Pipeline_BigData_org
       ./start.sh
       ```
    
    2. Vérifier que Cassandra est UP :
       ```bash
       docker ps | grep cassandra
       ```
    
    3. Attendre l'initialisation complète (peut prendre 1-2 minutes)
    """)
    st.stop()

# Auto-refresh
if st.checkbox('🔄 Auto-refresh data (5s)', value=True):
    time.sleep(5)
    st.rerun()

# Title
st.title("🐘 Mastodon Big Data Real-Time Monitor")
st.markdown("Streaming data from **Mastodon** via **Kafka** & **Spark**")

# Data Fetching
def load_data():
    # Schéma actuel : id, author, creation_date, ingestion_date, score, subreddit, text_content
    # On remonte le subreddit à la place de l'ancienne colonne 'instance'
    query = """
        SELECT id, author, subreddit, text_content, score, creation_date, ingestion_date
        FROM reddit_posts
    """
    rows = session.execute(query)
    df = pd.DataFrame(list(rows))
    return df

data = load_data()

if data.empty:
    st.warning("Waiting for data... (Pipeline starting?)")
else:
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Posts", len(data))
    
    unique_authors = data['author'].nunique()
    col2.metric("Unique Authors", unique_authors)
    
    # Extract keywords simple count (case-insensitive)
    keywords = ["bitcoin", "ethereum", "crypto", "defi", "nft"]
    keyword_counts = {
        k: data['text_content'].str.count(k, flags=re.IGNORECASE).sum()
        for k in keywords
    }
    top_keyword = max(keyword_counts, key=keyword_counts.get)
    col3.metric("Top Trend", top_keyword.upper())

    # Charts
    st.subheader("📊 Trends & Activity")
    
    # Keyword Bar Chart
    kw_df = pd.DataFrame(list(keyword_counts.items()), columns=['Keyword', 'Count'])
    chart = alt.Chart(kw_df).mark_bar().encode(
        x='Count',
        y=alt.Y('Keyword', sort='-x'),
        color='Keyword'
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

    # Recent Posts Table
    st.subheader("📝 Recent Posts")
    st.dataframe(
        data[['creation_date', 'author', 'text_content', 'subreddit']]
        .sort_values(by='creation_date', ascending=False)
        .head(10),
        use_container_width=True
    )

    # Raw Data Expander
    with st.expander("View Raw Data"):
        st.write(data)
