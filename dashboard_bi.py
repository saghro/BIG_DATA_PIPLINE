import streamlit as st
import pandas as pd
from cassandra.cluster import Cluster
import time
import altair as alt
import re
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Big Data Pipeline - BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour le thème sombre moderne
st.markdown("""
<style>
    /* Thème sombre */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1a1a2e;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Métriques */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4fc3f7;
    }
    
    [data-testid="stMetricLabel"] {
        color: #b0bec5;
    }
    
    [data-testid="stMetricDelta"] {
        color: #66bb6a;
    }
    
    /* Cards */
    .card {
        background-color: #1e1e2e;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #2d2d44;
    }
    
    /* Boutons */
    .stButton>button {
        background-color: #1976d2;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    
    .stButton>button:hover {
        background-color: #1565c0;
    }
    
    /* Tables */
    .dataframe {
        background-color: #1e1e2e;
        color: #ffffff;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a2e;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #b0bec5;
    }
    
    .stTabs [aria-selected="true"] {
        color: #4fc3f7 !important;
    }
</style>
""", unsafe_allow_html=True)

# Connexion à Cassandra
@st.cache_resource
def get_session():
    import socket
    
    # Essayer plusieurs méthodes de connexion
    session = None
    
    # Méthode 1: Connexion directe sur localhost
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 9042))
        sock.close()
        
        if result == 0:
            cluster = Cluster(['127.0.0.1'], port=9042, connect_timeout=5)
            session = cluster.connect('reddit_keyspace')
            return session
    except Exception:
        pass
    
    # Méthode 2: Essayer avec localhost au lieu de 127.0.0.1
    try:
        cluster = Cluster(['localhost'], port=9042, connect_timeout=5)
        session = cluster.connect('reddit_keyspace')
        return session
    except Exception:
        pass
    
    # Si les deux méthodes échouent, afficher l'erreur
    st.error("""
    ⚠️ **Cassandra n'est pas accessible sur le port 9042**
    
    **Solutions possibles :**
    
    1. **Vérifier que Cassandra est démarré :**
       ```bash
       docker ps | grep cassandra
       ```
    
    2. **Démarrer l'infrastructure complète :**
       ```bash
       cd /Users/a/Projet_Pipeline_BigData_org
       ./start.sh
       ```
    
    3. **Vérifier que le port 9042 est bien mappé :**
       ```bash
       docker-compose ps
       ```
       Le conteneur `cassandra` doit être UP et le port `9042:9042` doit être visible.
    
    4. **Attendre que Cassandra soit complètement initialisé :**
       ```bash
       docker logs cassandra --tail 20
       ```
       Cherche "Starting listening for CQL clients" dans les logs.
    
    5. **Créer le keyspace manuellement si nécessaire :**
       ```bash
       docker exec -it cassandra cqlsh -e "CREATE KEYSPACE IF NOT EXISTS reddit_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};"
       ```
    """)
    return None

session = get_session()
if session is None:
    st.stop()

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0;">
        <h1 style="color: #4fc3f7; font-size: 2rem; margin-bottom: 30px;">📊 Pipeline BI</h1>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "Navigation",
        ["Dashboard", "Analyse", "Tendances", "Données Brutes"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### Support")
    st.markdown("- 📖 Documentation")
    st.markdown("- 💬 Aide")

# Fonction pour charger les données
@st.cache_data(ttl=5)
def load_data():
    try:
        query = """
            SELECT id, author, subreddit, text_content, score, creation_date, ingestion_date
            FROM reddit_posts
        """
        rows = session.execute(query)
        df = pd.DataFrame(list(rows))
        
        if not df.empty:
            # Convertir les timestamps
            if 'creation_date' in df.columns:
                df['creation_date'] = pd.to_datetime(df['creation_date'])
            if 'ingestion_date' in df.columns:
                df['ingestion_date'] = pd.to_datetime(df['ingestion_date'])
            
            # Extraire les features
            df['has_bitcoin'] = df['text_content'].str.contains('bitcoin', case=False, na=False)
            df['has_ethereum'] = df['text_content'].str.contains('ethereum', case=False, na=False)
            df['has_crypto'] = df['text_content'].str.contains('crypto', case=False, na=False)
            df['has_defi'] = df['text_content'].str.contains('defi', case=False, na=False)
            df['has_nft'] = df['text_content'].str.contains('nft', case=False, na=False)
            
            # Calculer le sentiment simple (basé sur des mots-clés)
            positive_words = ['bullish', 'moon', 'hodl', 'buy', 'good', 'amazing', 'future']
            negative_words = ['dip', 'sell', 'crash', 'bad', 'volatile', 'risky']
            
            def simple_sentiment(text):
                if pd.isna(text):
                    return 'Neutral'
                text_lower = str(text).lower()
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                if pos_count > neg_count:
                    return 'Positive'
                elif neg_count > pos_count:
                    return 'Negative'
                return 'Neutral'
            
            df['sentiment'] = df['text_content'].apply(simple_sentiment)
            
            # Catégoriser la viralité basée sur le score
            df['viralite'] = df['score'].apply(
                lambda x: '🔥 HOT' if x > 50 else ('📈 UP' if x > 20 else '💤 LOW')
            )
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

# Charger les données
data = load_data()

if data.empty:
    st.warning("⏳ En attente de données... Le pipeline démarre peut-être.")
    st.info("💡 Lance './demo.sh' pour générer des données de test.")
else:
    # Header principal
    col_header1, col_header2, col_header3 = st.columns([2, 3, 2])
    
    with col_header1:
        st.markdown("### 👋 Bienvenue")
        st.markdown("**Vue d'ensemble du pipeline Big Data**")
    
    with col_header2:
        st.markdown("")
        search = st.text_input("🔍 Rechercher dans les posts", placeholder="bitcoin, ethereum, defi...")
    
    with col_header3:
        st.markdown("")
        auto_refresh = st.checkbox("🔄 Auto-refresh (5s)", value=False)
        if auto_refresh:
            time.sleep(5)
            st.rerun()
    
    # Filtrer les données selon la recherche
    if search:
        mask = data['text_content'].str.contains(search, case=False, na=False)
        data = data[mask]
    
    # KPIs Principaux (Top Row)
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_posts = len(data)
        st.metric(
            label="Total Posts",
            value=f"{total_posts:,}",
            delta=f"+{total_posts - 100}" if total_posts > 100 else None
        )
    
    with col2:
        unique_authors = data['author'].nunique()
        st.metric(
            label="Auteurs Uniques",
            value=f"{unique_authors}",
            delta=None
        )
    
    with col3:
        avg_score = data['score'].mean() if not data.empty else 0
        st.metric(
            label="Score Moyen",
            value=f"{avg_score:.1f}",
            delta=f"+{avg_score - 30:.1f}" if avg_score > 30 else None
        )
    
    with col4:
        # Top keyword
        keywords = ["bitcoin", "ethereum", "crypto", "defi", "nft"]
        keyword_counts = {
            k: data['text_content'].str.count(k, flags=re.IGNORECASE).sum()
            for k in keywords
        }
        top_keyword = max(keyword_counts, key=keyword_counts.get) if keyword_counts else "N/A"
        st.metric(
            label="Tendance Top",
            value=top_keyword.upper(),
            delta=None
        )
    
    # Deuxième ligne : Graphiques principaux
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### 📈 Performance Temporelle")
        
        # Préparer les données pour le graphique temporel
        if 'creation_date' in data.columns and not data.empty:
            data['date'] = data['creation_date'].dt.date
            daily_counts = data.groupby('date').size().reset_index(name='count')
            daily_counts = daily_counts.sort_values('date')
            
            fig = px.line(
                daily_counts,
                x='date',
                y='count',
                labels={'date': 'Date', 'count': 'Nombre de Posts'},
                color_discrete_sequence=['#4fc3f7']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#ffffff',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données temporelles non disponibles")
    
    with col_chart2:
        st.markdown("### 🎯 Répartition par Subreddit")
        
        if not data.empty:
            subreddit_counts = data['subreddit'].value_counts().head(10)
            
            fig = px.bar(
                x=subreddit_counts.values,
                y=subreddit_counts.index,
                orientation='h',
                labels={'x': 'Nombre de Posts', 'y': 'Subreddit'},
                color_discrete_sequence=['#66bb6a']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#ffffff',
                height=300,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée disponible")
    
    # Troisième ligne : Analyse des tendances
    st.markdown("---")
    st.markdown("### 📊 Analyse des Tendances")
    
    col_trend1, col_trend2 = st.columns(2)
    
    with col_trend1:
        st.markdown("#### Mots-clés les plus fréquents")
        
        keyword_counts_df = pd.DataFrame(
            list(keyword_counts.items()),
            columns=['Keyword', 'Count']
        ).sort_values('Count', ascending=False)
        
        fig = px.bar(
            keyword_counts_df,
            x='Count',
            y='Keyword',
            orientation='h',
            labels={'Count': 'Occurrences', 'Keyword': 'Mot-clé'},
            color='Count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff',
            height=250,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_trend2:
        st.markdown("#### Répartition du Sentiment")
        
        if 'sentiment' in data.columns:
            sentiment_counts = data['sentiment'].value_counts()
            
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                color_discrete_map={
                    'Positive': '#66bb6a',
                    'Negative': '#ef5350',
                    'Neutral': '#b0bec5'
                }
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#ffffff',
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sentiment non disponible")
    
    # Quatrième ligne : Tableaux détaillés
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📋 Posts Récents", "🔥 Posts Viraux", "📈 Top Auteurs"])
    
    with tab1:
        st.markdown("#### Derniers Posts Ingérés")
        
        display_cols = ['creation_date', 'author', 'subreddit', 'text_content', 'score', 'viralite']
        available_cols = [col for col in display_cols if col in data.columns]
        
        if available_cols:
            recent_data = data[available_cols].sort_values(
                by='creation_date' if 'creation_date' in data.columns else 'ingestion_date',
                ascending=False
            ).head(20)
            
            # Formater les dates
            if 'creation_date' in recent_data.columns:
                recent_data['creation_date'] = recent_data['creation_date'].dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(
                recent_data,
                use_container_width=True,
                height=400
            )
        else:
            st.info("Colonnes non disponibles")
    
    with tab2:
        st.markdown("#### Posts les plus Viraux (Score > 50)")
        
        viral_posts = data[data['score'] > 50].sort_values('score', ascending=False).head(20)
        
        if not viral_posts.empty:
            display_cols = ['creation_date', 'author', 'subreddit', 'text_content', 'score', 'viralite']
            available_cols = [col for col in display_cols if col in viral_posts.columns]
            
            if 'creation_date' in viral_posts.columns:
                viral_posts['creation_date'] = viral_posts['creation_date'].dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(
                viral_posts[available_cols],
                use_container_width=True,
                height=400
            )
        else:
            st.info("Aucun post viral trouvé (score > 50)")
    
    with tab3:
        st.markdown("#### Top Auteurs par Nombre de Posts")
        
        author_stats = data.groupby('author').agg({
            'id': 'count',
            'score': 'mean'
        }).rename(columns={'id': 'nb_posts', 'score': 'score_moyen'}).sort_values('nb_posts', ascending=False).head(20)
        
        st.dataframe(
            author_stats,
            use_container_width=True,
            height=400
        )
    
    # Footer avec statistiques
    st.markdown("---")
    col_footer1, col_footer2, col_footer3 = st.columns(3)
    
    with col_footer1:
        st.markdown(f"**📅 Dernière mise à jour:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col_footer2:
        if 'ingestion_date' in data.columns:
            last_ingestion = data['ingestion_date'].max()
            st.markdown(f"**⏰ Dernier post ingéré:** {last_ingestion}")
    
    with col_footer3:
        st.markdown(f"**📊 Total de données:** {len(data)} posts")
