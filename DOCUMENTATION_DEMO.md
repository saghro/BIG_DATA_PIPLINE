# 📚 Documentation Complète - Pipeline Big Data Mastodon/Reddit

## Table des Matières

1. [Vue d'ensemble du projet](#vue-densemble-du-projet)
2. [Architecture du système](#architecture-du-système)
3. [Guide de démonstration](#guide-de-démonstration)
4. [Dépannage](#dépannage)
5. [Références techniques](#références-techniques)

---

## Vue d'ensemble du projet

### Objectif

Ce projet implémente un **pipeline Big Data temps réel** pour analyser des conversations en ligne autour des cryptomonnaies et de la finance. Il ingère des données depuis **Reddit** et **Mastodon**, les traite en streaming avec **Apache Spark**, et stocke les résultats dans **Cassandra** avec un mécanisme de fallback vers **MongoDB**.

### Fonctionnalités principales

- ✅ **Ingestion temps réel** depuis Reddit et Mastodon
- ✅ **Streaming** via Apache Kafka
- ✅ **Traitement en temps réel** avec Spark Structured Streaming
- ✅ **Analyse avancée** : NLP, sentiment, modélisation de sujets, prédiction de viralité
- ✅ **Stockage tolérant aux pannes** (Cassandra + MongoDB fallback)
- ✅ **Orchestration** avec Apache Airflow
- ✅ **Visualisation** via dashboard BI moderne

---

## Architecture du système

### Vue d'ensemble

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
                     │
                     ▼
            ┌──────────────┐
            │   Power BI   │
            │  (Export CSV)│
            └──────────────┘
```

### Composants détaillés

#### 1. **Ingestion de données** (`main/data_ingestion/`)

**Fichiers principaux :**
- `data_ingestion.py` : Ingestion depuis Reddit via PRAW
- `mastodon_ingestion.py` : Ingestion depuis Mastodon (timeline publique)
- `mock_data_generator.py` : Générateur de données de test

**Fonctionnement :**
- Se connecte aux APIs Reddit/Mastodon
- Filtre les messages contenant des mots-clés crypto/finance
- Publie les messages dans un topic Kafka (`Mastodon_Data`)

**Configuration :**
- Kafka Broker : `broker:9092` (interne Docker) ou `localhost:9093` (externe)
- Topic : `Mastodon_Data`
- Format : JSON avec champs `id`, `author`, `subreddit`, `text`, `timestamp`, `score`

---

#### 2. **Apache Kafka** (`broker`)

**Rôle :**
- Buffer de messages entre l'ingestion et le traitement
- Découplage des composants
- Gestion des offsets pour la reprise sur erreur

**Configuration :**
- Port interne : `9092` (communication entre conteneurs)
- Port externe : `9093` (accès depuis le host)
- Topic : `Mastodon_Data` avec 3 partitions

**Commandes utiles :**
```bash
# Voir les messages dans Kafka
docker exec -it broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic Mastodon_Data \
  --from-beginning \
  --max-messages 10
```

---

#### 3. **Apache Spark** (`spark/`)

**Composants :**

**a) Moteur d'inférence** (`engine.py`)
- Lit les messages depuis Kafka en streaming
- Applique le pré-traitement (nettoyage texte, tokenisation)
- Charge et applique les modèles ML :
  - **Word2Vec** : Vectorisation des mots
  - **CountVectorizer** : Matrice de fréquences
  - **LDA** : Modélisation de sujets latents
  - **Random Forest** : Prédiction de la viralité
- Enrichit les données avec :
  - Sentiment (Positive/Negative/Neutral)
  - Sujet dominant (basé sur LDA)
  - Score de viralité prédit
  - Catégorie de viralité (🔥 HOT / 📈 UP / 💤 LOW)

**b) Préprocesseur** (`preprocessor.py`)
- Nettoyage du texte (lowercase, stopwords)
- Extraction de features temporelles (jour, heure, jour de la semaine)
- Tokenisation et normalisation

**c) Chargeur de modèles** (`loader.py`)
- Charge les modèles ML pré-entraînés depuis `/opt/spark/models/`
- Gère le cache et la réutilisation des modèles

**d) Configuration** (`config.py`)
- Paramètres Kafka, Cassandra, MongoDB
- Chemins des modèles ML
- Configuration Spark

**Fonctionnement :**
1. Spark lit Kafka en micro-batches (toutes les 20 secondes)
2. Pour chaque batch :
   - Prépare les données
   - Applique les modèles ML
   - Enrichit avec sentiment/sujet/viralité
   - Tente d'écrire dans Cassandra
   - En cas d'échec, bascule vers MongoDB

---

#### 4. **Stockage** 

**a) Apache Cassandra** (Stockage principal)

**Rôle :**
- Base NoSQL optimisée pour les écritures haute performance
- Excellente pour les données time-series
- Scalabilité linéaire

**Schéma :**
```sql
CREATE KEYSPACE reddit_keyspace
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE reddit_posts (
    id TEXT PRIMARY KEY,
    author TEXT,
    subreddit TEXT,
    text_content TEXT,
    score INT,
    creation_date TIMESTAMP,
    ingestion_date TIMESTAMP
);
```

**Accès :**
- Port : `9042`
- Keyspace : `reddit_keyspace`
- Table : `reddit_posts`

**Commandes utiles :**
```bash
# Se connecter à Cassandra
docker exec -it cassandra cqlsh

# Compter les posts
docker exec -it cassandra cqlsh -e "SELECT count(*) FROM reddit_keyspace.reddit_posts;"

# Voir les derniers posts
docker exec -it cassandra cqlsh -e "SELECT * FROM reddit_keyspace.reddit_posts LIMIT 10;"
```

**b) MongoDB** (Fallback)

**Rôle :**
- Mécanisme de secours si Cassandra est indisponible
- Stockage schémaless pour éviter les rejets de données
- Garantit zéro perte de données

**Configuration :**
- Port : `27018` (mappé depuis `27017` du conteneur)
- Base : `reddit_backup_local`
- Collection : `viral_posts`

**Accès :**
```bash
# Se connecter à MongoDB
docker exec -it mongodb mongosh

# Voir les posts sauvegardés
docker exec -it mongodb mongosh --eval "use reddit_backup_local; db.viral_posts.find().limit(5)"
```

---

#### 5. **Apache Airflow** (`airflow/`)

**Rôle :**
- Orchestration des workflows
- Planification et monitoring des tâches
- Gestion des dépendances entre composants

**DAG principal :** `mastodon_pipeline`

**Tâches :**
1. `run_mastodon` : Lance l'ingestion Mastodon
2. `run_spark` : Lance le traitement Spark streaming

**Configuration :**
- UI : `http://localhost:8091`
- Credentials : `admin` / `admin`
- Base de données : PostgreSQL (métadonnées Airflow)

**Accès :**
```bash
# Activer un DAG
docker exec <airflow-container> airflow dags unpause mastodon_pipeline

# Déclencher un DAG
docker exec <airflow-container> airflow dags trigger mastodon_pipeline
```

---

#### 6. **Dashboard BI** (`dashboard_bi.py`)

**Fonctionnalités :**
- **KPIs en temps réel** : Total posts, auteurs uniques, score moyen, tendance top
- **Graphiques interactifs** :
  - Performance temporelle (ligne)
  - Répartition par subreddit (barres)
  - Mots-clés les plus fréquents
  - Répartition du sentiment (camembert)
- **Tableaux détaillés** :
  - Posts récents
  - Posts viraux (score > 50)
  - Top auteurs

**Technologies :**
- Streamlit pour l'interface
- Plotly pour les graphiques interactifs
- Pandas pour le traitement des données
- Driver Cassandra pour la connexion

**Lancement :**
```bash
./run_dashboard_bi.sh
# Puis ouvrir http://localhost:8501
```

---

### Infrastructure Docker

**Services définis dans `docker-compose.yml` :**

| Service | Image | Ports | Description |
|---------|-------|-------|-------------|
| `broker` | apache/kafka:latest | 9092, 9093 | Message broker Kafka |
| `cassandra` | cassandra:latest | 9042 | Base NoSQL principale |
| `cassandra-init` | cassandra:latest | - | Initialisation du schéma |
| `mongodb` | mongo:7.0 | 27018 | Base de fallback |
| `spark-master` | custom-spark:3.5.1 | 8083, 7077 | Master Spark |
| `spark-worker` | custom-spark:3.5.1 | 8084 | Worker Spark |
| `airflow-postgres` | postgres:15 | 5432 | Base Airflow |
| `airflow-webserver` | apache/airflow:2.7.1 | 8091 | UI Airflow |
| `airflow-scheduler` | apache/airflow:2.7.1 | - | Scheduler Airflow |

**Réseau :**
- Tous les services sont sur le réseau Docker `reddit-network`
- Communication interne via les noms de services (ex: `broker:9092`)

---

## Guide de démonstration

### Prérequis

1. **Docker Desktop** installé et lancé
2. **Python 3.8+** avec pip
3. **Git** (pour cloner le projet si nécessaire)

### Étape 1 : Préparation de l'environnement

```bash
# 1. Aller dans le dossier du projet
cd /Users/a/Projet_Pipeline_BigData_org

# 2. Vérifier que Docker est lancé
docker info

# Si Docker n'est pas lancé, ouvrir Docker Desktop
```

---

### Étape 2 : Démarrage de l'infrastructure

**Option A : Script automatique (recommandé)**

```bash
./start.sh
```

Ce script :
- Vérifie Docker
- Nettoie les anciens conteneurs
- Construit et démarre tous les services
- Attend l'initialisation de Cassandra
- Affiche les URLs utiles

**Temps d'attente :** 2-5 minutes pour la première fois

**Option B : Script de correction complète**

Si tu rencontres des problèmes :

```bash
./fix_and_start.sh
```

Ce script fait tout + corrige les problèmes courants.

---

### Étape 3 : Vérification de l'infrastructure

```bash
# Vérifier que tous les services sont UP
docker-compose ps

# Vérifier spécifiquement Cassandra
./check_cassandra.sh
```

**Résultat attendu :**
- ✅ Tous les conteneurs avec statut "Up"
- ✅ Cassandra accessible sur le port 9042
- ✅ Keyspace `reddit_keyspace` créé

---

### Étape 4 : Génération de données de test

**Option A : Script de démo automatique (recommandé)**

```bash
./demo.sh
```

Ce script :
- Génère 20 posts mock
- Les envoie dans Kafka
- Attend que Spark les traite (30 secondes)
- Vérifie qu'ils sont dans Cassandra
- Affiche des exemples de données

**Option B : Génération manuelle**

```bash
# Trouver le conteneur Airflow
AIRFLOW_CONTAINER=$(docker ps | grep airflow-webserver | awk '{print $1}')

# Générer 50 posts mock
docker exec -it $AIRFLOW_CONTAINER python /opt/airflow/main/data_ingestion/mock_data_generator.py
```

**Attendre 1-2 minutes** que Spark traite les données.

---

### Étape 5 : Vérification des données

```bash
# Compter les posts dans Cassandra
docker exec -it cassandra cqlsh -e "SELECT count(*) FROM reddit_keyspace.reddit_posts;"

# Voir quelques exemples
docker exec -it cassandra cqlsh -e "SELECT * FROM reddit_keyspace.reddit_posts LIMIT 5;"
```

**Résultat attendu :** Un nombre > 0 de posts dans Cassandra

---

### Étape 6 : Lancement du Dashboard BI

```bash
./run_dashboard_bi.sh
```

Puis ouvrir dans le navigateur : `http://localhost:8501`

**Ce que tu devrais voir :**
- KPIs en haut (Total Posts, Auteurs Uniques, Score Moyen, Tendance Top)
- Graphiques interactifs (performance temporelle, répartition par subreddit, mots-clés, sentiment)
- Tableaux détaillés (posts récents, posts viraux, top auteurs)

---

### Étape 7 : Démonstration des composants

#### A. Architecture Docker

```bash
docker-compose ps
```

**Montrer :**
- Les 8 services en cours d'exécution
- Les ports mappés
- Les statuts (healthy, Up)

#### B. Kafka - Messages en temps réel

```bash
docker exec -it broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic Mastodon_Data \
  --from-beginning \
  --max-messages 5
```

**Montrer :** Les messages JSON bruts dans Kafka

#### C. Spark UI - Monitoring des jobs

Ouvrir dans le navigateur : `http://localhost:8083`

**Montrer :**
- Les "Streaming Queries" actives
- Les "Completed Applications"
- Les "Workers" et leur statut

#### D. Airflow UI - Orchestration

Ouvrir dans le navigateur : `http://localhost:8091` (admin/admin)

**Montrer :**
- Le DAG `mastodon_pipeline`
- Les runs réussis (cercle vert)
- Les logs des tâches
- Le graphe des dépendances

#### E. Dashboard BI - Visualisation

Déjà ouvert à `http://localhost:8501`

**Montrer :**
- Les KPIs en temps réel
- Les graphiques interactifs
- Les tableaux avec filtres
- La recherche en temps réel

#### F. Export pour Power BI

```bash
# Exporter depuis Cassandra
docker exec -it cassandra cqlsh -e "COPY reddit_keyspace.reddit_posts TO 'reddit_posts.csv' WITH HEADER = TRUE;"

# Copier le fichier vers le host
docker cp cassandra:/reddit_posts.csv /Users/a/Projet_Pipeline_BigData_org/reddit_posts.csv

# Vérifier le fichier
ls -lh reddit_posts.csv
```

Puis importer `reddit_posts.csv` dans Power BI Desktop.

---

### Checklist de démo

- [ ] Docker Desktop est lancé
- [ ] Tous les conteneurs sont UP (`docker-compose ps`)
- [ ] Cassandra est accessible (`./check_cassandra.sh` tout vert)
- [ ] Des données sont présentes dans Cassandra (count > 0)
- [ ] Le dashboard BI affiche des données
- [ ] Spark UI montre des queries actives
- [ ] Airflow UI montre des runs réussis

---

## Dépannage

### Problème 1 : Docker n'est pas lancé

**Symptôme :**
```
❌ Docker is not running!
```

**Solution :**
1. Ouvrir Docker Desktop depuis Applications
2. Attendre que l'icône soit verte dans la barre de menu
3. Relancer `./start.sh`

---

### Problème 2 : Cassandra n'est pas accessible

**Symptôme :**
```
❌ Le port 9042 n'est PAS accessible depuis le host
```

**Solutions :**

**Solution A : Script automatique**
```bash
./fix_cassandra_port.sh
```

**Solution B : Redémarrage manuel**
```bash
docker restart cassandra
sleep 60
./check_cassandra.sh
```

**Solution C : Création manuelle du keyspace**
```bash
docker exec -it cassandra cqlsh -e "
CREATE KEYSPACE IF NOT EXISTS reddit_keyspace
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS reddit_keyspace.reddit_posts (
    id TEXT PRIMARY KEY,
    author TEXT,
    subreddit TEXT,
    text_content TEXT,
    score INT,
    creation_date TIMESTAMP,
    ingestion_date TIMESTAMP
);"
```

---

### Problème 3 : Aucune donnée dans Cassandra

**Symptôme :**
```
count
-------
    0
```

**Solutions :**

1. **Vérifier que Kafka reçoit des données :**
```bash
docker exec -it broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic Mastodon_Data \
  --from-beginning \
  --max-messages 5
```

2. **Générer des données mock :**
```bash
./demo.sh
```

3. **Vérifier que Spark traite les données :**
```bash
# Voir les logs Spark
docker logs spark-worker --tail 50

# Vérifier dans Spark UI
# Ouvrir http://localhost:8083
# Regarder "Streaming Queries"
```

4. **Déclencher le DAG Airflow manuellement :**
```bash
AIRFLOW_CONTAINER=$(docker ps | grep airflow-webserver | awk '{print $1}')
docker exec $AIRFLOW_CONTAINER airflow dags unpause mastodon_pipeline
docker exec $AIRFLOW_CONTAINER airflow dags trigger mastodon_pipeline
```

---

### Problème 4 : Le dashboard BI ne se connecte pas

**Symptôme :**
```
⚠️ Cassandra n'est pas accessible sur le port 9042
```

**Solutions :**

1. **Vérifier que Cassandra est démarré :**
```bash
docker ps | grep cassandra
```

2. **Vérifier le port :**
```bash
docker-compose ps | grep cassandra
# Doit afficher : 0.0.0.0:9042->9042/tcp
```

3. **Redémarrer Cassandra :**
```bash
./fix_cassandra_port.sh
```

4. **Relancer le dashboard :**
```bash
./run_dashboard_bi.sh
```

---

### Problème 5 : Le DAG Airflow reste en "queued"

**Symptôme :**
- Le DAG est déclenché mais reste en état "queued"
- Les tâches ne démarrent pas

**Solutions :**

1. **Vérifier les logs du scheduler :**
```bash
docker logs projet_pipeline_bigdata_org-airflow-scheduler-1 --tail 50
```

2. **Lancer Spark manuellement (bypass Airflow) :**
```bash
docker exec -d spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --py-files /opt/spark/work-dir/config.py \
  --files /opt/spark/work-dir/config.py \
  --conf spark.dynamicAllocation.enabled=false \
  /opt/spark/work-dir/run.py
```

3. **Vérifier que Spark traite les données :**
```bash
docker logs spark-worker --tail 50
```

---

## Références techniques

### Scripts disponibles

| Script | Description | Usage |
|--------|-------------|-------|
| `start.sh` | Démarre toute l'infrastructure | `./start.sh` |
| `fix_and_start.sh` | Corrige et démarre tout | `./fix_and_start.sh` |
| `check_cassandra.sh` | Vérifie la connexion Cassandra | `./check_cassandra.sh` |
| `fix_cassandra_port.sh` | Corrige le port Cassandra | `./fix_cassandra_port.sh` |
| `demo.sh` | Génère des données de test | `./demo.sh` |
| `run_dashboard_bi.sh` | Lance le dashboard BI | `./run_dashboard_bi.sh` |
| `run_dashboard.sh` | Lance l'ancien dashboard | `./run_dashboard.sh` |
| `verify_pipeline.sh` | Vérifie le pipeline complet | `./verify_pipeline.sh` |
| `test_pipeline.sh` | Test avec données mock | `./test_pipeline.sh` |

### URLs importantes

| Service | URL | Credentials |
|---------|-----|-------------|
| Dashboard BI | http://localhost:8501 | - |
| Airflow UI | http://localhost:8091 | admin / admin |
| Spark Master UI | http://localhost:8083 | - |
| Spark Worker UI | http://localhost:8084 | - |
| Kafka | localhost:9093 | - |
| Cassandra | localhost:9042 | - |
| MongoDB | localhost:27018 | - |

### Commandes Docker utiles

```bash
# Voir tous les conteneurs
docker-compose ps

# Voir les logs d'un service
docker logs <container-name> --tail 50 -f

# Redémarrer un service
docker restart <container-name>

# Arrêter tout
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Reconstruire les images
docker-compose build --no-cache
```

### Structure des fichiers

```
Projet_Pipeline_BigData_org/
├── airflow/
│   └── dags/
│       └── orchestration_pipeline.py    # DAG Airflow
├── main/
│   └── data_ingestion/
│       ├── data_ingestion.py            # Ingestion Reddit
│       ├── mastodon_ingestion.py        # Ingestion Mastodon
│       ├── mock_data_generator.py       # Générateur de test
│       └── config.py                    # Configuration
├── spark/
│   ├── engine.py                        # Moteur Spark principal
│   ├── run.py                           # Point d'entrée Spark
│   ├── config.py                        # Configuration Spark
│   ├── preprocessor.py                  # Pré-traitement
│   ├── loader.py                        # Chargeur de modèles
│   └── utils.py                         # Utilitaires
├── dashboard_bi.py                      # Dashboard BI moderne
├── dashboard.py                         # Ancien dashboard
├── docker-compose.yml                   # Infrastructure Docker
├── Dockerfile                           # Image Spark custom
├── Dockerfile.airflow                   # Image Airflow custom
├── init.cql                            # Schéma Cassandra
└── *.sh                                # Scripts de démarrage
```

---

## Conclusion

Ce pipeline Big Data démontre une architecture complète et production-ready pour l'analyse de données en temps réel. Il combine les meilleures pratiques de l'industrie :

- **Scalabilité** : Kafka + Spark pour gérer de gros volumes
- **Fiabilité** : Mécanisme de fallback MongoDB
- **Orchestration** : Airflow pour la gestion des workflows
- **Visualisation** : Dashboard BI interactif
- **Maintenabilité** : Infrastructure containerisée avec Docker

Pour toute question ou problème, consulte la section [Dépannage](#dépannage) ou vérifie les logs des services avec `docker logs <container-name>`.

---

**Mainteneur (fork) :** [saghro](https://github.com/saghro) — dépôt `BIG_DATA_PIPLINE`

**Auteurs du projet initial (remerciements) :**
- EL RHERBI Mohamed Amine
- CHATRAOUI Hamza
- DHAH Chaimaa
- EL Houdaigui Maria
- AMMAM Yassir

**Date de documentation :** Février 2026
