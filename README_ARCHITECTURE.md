# 🏗️ Architecture du Pipeline Mastodon - Vue d'ensemble

## Diagramme d'Architecture

Pour visualiser l'architecture complète, utilise le fichier `architecture_mastodon.mmd` avec un visualiseur Mermaid (comme [Mermaid Live Editor](https://mermaid.live/)).

### Vue simplifiée

```
┌─────────────────┐
│    Mastodon     │  (Public Timeline)
│   🐘 Instance   │ ───┐
└─────────────────┘    │
                       │
                       ▼
                ┌──────────────┐
                │    Kafka     │  (Message Broker)
                │   Topic:     │
                │ Mastodon_Data│
                └──────────────┘
                       │
                       ▼
                ┌──────────────┐
                │    Spark     │  (Structured Streaming)
                │   Engine     │  - NLP Processing
                │              │  - Sentiment Analysis
                │              │  - Topic Modeling
                │              │  - Virality Prediction
                └──────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
    ┌─────────┐                 ┌─────────┐
    │Cassandra│                 │ MongoDB │
    │(Primary)│                 │(Fallback)│
    └─────────┘                 └─────────┘
         │                           │
         └───────────┬───────────────┘
                     │
                     ▼
            ┌──────────────┐
            │   Dashboard  │
            │      BI      │
            │  (Streamlit) │
            └──────────────┘
```

---

## Composants Principaux

### 1. **Source de Données : Mastodon**
- **Type** : Réseau social décentralisé
- **Accès** : Timeline publique (pas besoin d'API key)
- **Instance** : mastodon.social (par défaut)
- **Filtrage** : Mots-clés crypto/finance

### 2. **Kafka (Message Broker)**
- **Rôle** : Buffer de messages entre ingestion et traitement
- **Topic** : `Mastodon_Data`
- **Ports** : 9092 (interne), 9093 (externe)

### 3. **Spark Streaming (Traitement)**
- **Rôle** : Traitement temps réel des messages
- **Fonctionnalités** :
  - Pré-traitement texte
  - Analyse de sentiment
  - Modélisation de sujets (LDA)
  - Prédiction de viralité (Random Forest)

### 4. **Stockage**
- **Cassandra** : Stockage principal (haute performance)
- **MongoDB** : Fallback automatique si Cassandra échoue

### 5. **Orchestration : Airflow**
- **DAG** : `mastodon_pipeline`
- **Tâches** : Ingestion Mastodon + Traitement Spark

### 6. **Visualisation**
- **Dashboard BI** : Streamlit (temps réel)
- **Power BI** : Export CSV pour analyses avancées

---

## Flux de Données

1. **Ingestion** : Mastodon → Kafka
2. **Traitement** : Kafka → Spark → Enrichissement ML
3. **Stockage** : Spark → Cassandra (ou MongoDB si échec)
4. **Visualisation** : Cassandra/MongoDB → Dashboard BI

---

## Technologies Utilisées

- **Docker & Docker Compose** : Containerisation
- **Apache Kafka** : Streaming de messages
- **Apache Spark** : Traitement distribué
- **Apache Cassandra** : Base NoSQL
- **MongoDB** : Base de fallback
- **Apache Airflow** : Orchestration
- **Streamlit** : Dashboard temps réel
- **Python** : Langage principal

---

Pour plus de détails, voir **`DOCUMENTATION_DEMO.md`**
